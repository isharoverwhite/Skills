#!/usr/bin/env python3
"""
Calculate S/P battery topology and estimate compact cell layouts.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass


CHEMISTRY_PRESETS = {
    "lfp": {"cell_nominal_v": 3.2},
    "li-ion": {"cell_nominal_v": 3.7},
    "nmc": {"cell_nominal_v": 3.6},
    "lto": {"cell_nominal_v": 2.3},
    "lead-acid": {"cell_nominal_v": 2.0},
}

COMMON_SERIES = {
    "lfp": {12: 4, 24: 8, 48: 16},
    "li-ion": {12: 3, 24: 7, 48: 13},
    "nmc": {12: 3, 24: 7, 48: 13},
    "lto": {12: 6, 24: 12, 48: 24},
    "lead-acid": {12: 6, 24: 12, 48: 24},
}

FORM_FACTOR_PRESETS = {
    "12700": {"shape": "cylindrical", "diameter_mm": 12.0, "height_mm": 70.0},
    "14500": {"shape": "cylindrical", "diameter_mm": 14.0, "height_mm": 50.0},
    "18650": {"shape": "cylindrical", "diameter_mm": 18.0, "height_mm": 65.0},
    "21700": {"shape": "cylindrical", "diameter_mm": 21.0, "height_mm": 70.0},
    "26650": {"shape": "cylindrical", "diameter_mm": 26.0, "height_mm": 65.0},
    "32700": {"shape": "cylindrical", "diameter_mm": 32.0, "height_mm": 70.0},
    "38120": {"shape": "cylindrical", "diameter_mm": 38.0, "height_mm": 120.0},
    "4680": {"shape": "cylindrical", "diameter_mm": 46.0, "height_mm": 80.0},
}


@dataclass
class CellGeometry:
    label: str
    shape: str
    plan_width_mm: float
    plan_depth_mm: float
    height_mm: float
    source: str


@dataclass
class LayoutCandidate:
    layout_goal: str
    orientation: str
    layers: int
    groups_per_layer: int
    parallel_cluster_rows: int
    parallel_cluster_cols: int
    parallel_cluster_empty_slots: int
    series_group_rows: int
    series_group_cols: int
    total_empty_group_slots: int
    width_mm: float
    depth_mm: float
    height_mm: float
    footprint_mm2: float
    volume_mm3: float
    score: float


@dataclass
class PackResult:
    series_count: int
    parallel_count: int
    total_cells: int
    pack_nominal_v: float
    pack_capacity_ah: float
    pack_energy_wh: float
    target_pack_v: float | None
    target_capacity_ah: float | None
    target_energy_wh: float | None
    target_discharge_a: float | None
    parallel_by_capacity: int | None
    parallel_by_energy: int | None
    parallel_by_current: int | None
    max_continuous_current_a: float | None
    recommended_layout: LayoutCandidate
    alternative_layouts: list[LayoutCandidate]
    notes: list[str]


def positive_number(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def ceil_units(value: float) -> int:
    return max(1, int(math.ceil(value - 1e-9)))


def resolve_cell_geometry(args: argparse.Namespace) -> CellGeometry:
    if args.cell_format is not None:
        preset = FORM_FACTOR_PRESETS[args.cell_format]
        diameter = preset["diameter_mm"]
        return CellGeometry(
            label=args.cell_format,
            shape="cylindrical",
            plan_width_mm=diameter,
            plan_depth_mm=diameter,
            height_mm=preset["height_mm"],
            source="preset",
        )

    if args.shape == "cylindrical":
        return CellGeometry(
            label="custom cylindrical",
            shape="cylindrical",
            plan_width_mm=args.diameter_mm,
            plan_depth_mm=args.diameter_mm,
            height_mm=args.cell_height_mm,
            source="custom",
        )

    return CellGeometry(
        label="custom prismatic",
        shape="prismatic",
        plan_width_mm=args.cell_width_mm,
        plan_depth_mm=args.cell_depth_mm,
        height_mm=args.cell_height_mm,
        source="custom",
    )


def resolve_cell_nominal_v(args: argparse.Namespace) -> float:
    if args.cell_nominal_v is not None:
        return args.cell_nominal_v
    if args.chemistry is not None:
        return CHEMISTRY_PRESETS[args.chemistry]["cell_nominal_v"]
    raise ValueError("provide --chemistry or --cell-nominal-v")


def resolve_series_count(args: argparse.Namespace, cell_nominal_v: float) -> tuple[int, float | None]:
    if args.series_count is not None:
        return args.series_count, None

    if args.bus_class is not None:
        if args.chemistry in COMMON_SERIES and args.bus_class in COMMON_SERIES[args.chemistry]:
            series_count = COMMON_SERIES[args.chemistry][args.bus_class]
        else:
            series_count = ceil_units(args.bus_class / cell_nominal_v)
        return series_count, float(args.bus_class)

    if args.target_pack_v is not None:
        return ceil_units(args.target_pack_v / cell_nominal_v), args.target_pack_v

    raise ValueError("provide --series-count, --bus-class, or --target-pack-v")


def resolve_parallel_counts(
    args: argparse.Namespace,
    series_count: int,
    cell_nominal_v: float,
) -> tuple[int, int | None, int | None, int | None]:
    if args.parallel_count is not None:
        return args.parallel_count, None, None, None

    by_capacity = None
    by_energy = None
    by_current = None

    if args.target_capacity_ah is not None:
        by_capacity = ceil_units(args.target_capacity_ah / args.cell_capacity_ah)
    if args.target_energy_wh is not None:
        cell_string_energy_wh = series_count * cell_nominal_v * args.cell_capacity_ah
        by_energy = ceil_units(args.target_energy_wh / cell_string_energy_wh)
    if args.target_discharge_a is not None:
        by_current = ceil_units(args.target_discharge_a / args.cell_continuous_a)

    candidates = [value for value in (by_capacity, by_energy, by_current) if value is not None]
    if not candidates:
        raise ValueError(
            "provide --parallel-count or at least one of --target-capacity-ah, --target-energy-wh, or --target-discharge-a"
        )

    return max(candidates), by_capacity, by_energy, by_current


def orientation_options(geometry: CellGeometry) -> list[tuple[str, float, float]]:
    options = [("default", geometry.plan_width_mm, geometry.plan_depth_mm)]
    if abs(geometry.plan_width_mm - geometry.plan_depth_mm) > 1e-6:
        options.append(("rotated", geometry.plan_depth_mm, geometry.plan_width_mm))
    return options


def cluster_options(
    parallel_count: int,
    geometry: CellGeometry,
    cell_spacing_mm: float,
) -> list[dict[str, float | int | str]]:
    options: list[dict[str, float | int | str]] = []
    for orientation, cell_w, cell_d in orientation_options(geometry):
        for rows in range(1, parallel_count + 1):
            cols = ceil_units(parallel_count / rows)
            slots = rows * cols
            empty_slots = slots - parallel_count
            width = cols * cell_w + max(0, cols - 1) * cell_spacing_mm
            depth = rows * cell_d + max(0, rows - 1) * cell_spacing_mm
            aspect = max(width, depth) / min(width, depth)
            area = width * depth
            score = area * (1 + 0.08 * (aspect - 1) + 0.04 * empty_slots)
            options.append(
                {
                    "orientation": orientation,
                    "cluster_rows": rows,
                    "cluster_cols": cols,
                    "cluster_empty_slots": empty_slots,
                    "cluster_width_mm": width,
                    "cluster_depth_mm": depth,
                    "cluster_score": score,
                }
            )
    return options


def layout_score(
    goal: str,
    width_mm: float,
    depth_mm: float,
    height_mm: float,
    layers: int,
    empty_group_slots: int,
    empty_cluster_slots: int,
) -> float:
    footprint = width_mm * depth_mm
    volume = footprint * height_mm
    aspect = max(width_mm, depth_mm) / min(width_mm, depth_mm)
    if goal == "compact":
        return volume * (1 + 0.05 * (aspect - 1) + 0.03 * empty_group_slots + 0.01 * empty_cluster_slots)
    if goal == "footprint":
        return footprint * (1 + 0.1 * (aspect - 1) + 0.02 * empty_group_slots)
    if goal == "flat":
        return height_mm * 100000.0 + footprint + layers * 1000.0 + empty_group_slots * 100.0
    return footprint * (1 + 0.15 * (aspect - 1) + 0.04 * max(0, layers - 1) + 0.02 * empty_group_slots)


def enumerate_layouts(
    series_count: int,
    parallel_count: int,
    geometry: CellGeometry,
    args: argparse.Namespace,
) -> list[LayoutCandidate]:
    layouts: list[LayoutCandidate] = []
    for cluster in cluster_options(parallel_count, geometry, args.cell_spacing_mm):
        cluster_width = float(cluster["cluster_width_mm"])
        cluster_depth = float(cluster["cluster_depth_mm"])
        cluster_empty = int(cluster["cluster_empty_slots"])
        for layers in range(1, args.max_layers + 1):
            groups_per_layer = ceil_units(series_count / layers)
            for group_rows in range(1, groups_per_layer + 1):
                group_cols = ceil_units(groups_per_layer / group_rows)
                slots_per_layer = group_rows * group_cols
                total_empty_group_slots = slots_per_layer * layers - series_count
                width = group_cols * cluster_width + max(0, group_cols - 1) * args.series_gap_mm
                depth = group_rows * cluster_depth + max(0, group_rows - 1) * args.series_gap_mm
                height = layers * geometry.height_mm + max(0, layers - 1) * args.layer_gap_mm
                footprint = width * depth
                volume = footprint * height
                score = layout_score(
                    goal=args.layout_goal,
                    width_mm=width,
                    depth_mm=depth,
                    height_mm=height,
                    layers=layers,
                    empty_group_slots=total_empty_group_slots,
                    empty_cluster_slots=cluster_empty,
                )
                layouts.append(
                    LayoutCandidate(
                        layout_goal=args.layout_goal,
                        orientation=str(cluster["orientation"]),
                        layers=layers,
                        groups_per_layer=groups_per_layer,
                        parallel_cluster_rows=int(cluster["cluster_rows"]),
                        parallel_cluster_cols=int(cluster["cluster_cols"]),
                        parallel_cluster_empty_slots=cluster_empty,
                        series_group_rows=group_rows,
                        series_group_cols=group_cols,
                        total_empty_group_slots=total_empty_group_slots,
                        width_mm=width,
                        depth_mm=depth,
                        height_mm=height,
                        footprint_mm2=footprint,
                        volume_mm3=volume,
                        score=score,
                    )
                )

    layouts.sort(
        key=lambda item: (
            round(item.score, 6),
            round(item.footprint_mm2, 6),
            round(item.volume_mm3, 6),
            round(max(item.width_mm, item.depth_mm), 6),
            item.layers,
        )
    )

    unique_layouts: list[LayoutCandidate] = []
    seen = set()
    for layout in layouts:
        key = (
            round(layout.width_mm, 3),
            round(layout.depth_mm, 3),
            round(layout.height_mm, 3),
            layout.layers,
            layout.parallel_cluster_rows,
            layout.parallel_cluster_cols,
            layout.series_group_rows,
            layout.series_group_cols,
        )
        if key in seen:
            continue
        seen.add(key)
        unique_layouts.append(layout)
    return unique_layouts


def build_notes(
    args: argparse.Namespace,
    geometry: CellGeometry,
    pack_result: PackResult,
) -> list[str]:
    notes: list[str] = []
    if geometry.shape == "cylindrical":
        notes.append("Cylindrical layout uses a rectangular grouped-envelope estimate; real honeycomb packing can be somewhat denser.")
    if geometry.shape == "prismatic" and geometry.source == "custom":
        notes.append("Prismatic layout depends heavily on real terminal clearance, compression hardware, and datasheet orientation limits.")
    if pack_result.parallel_by_current is not None and pack_result.parallel_by_current > max(
        value or 0 for value in (pack_result.parallel_by_capacity, pack_result.parallel_by_energy)
    ):
        notes.append("Parallel count is being driven by current capability more than by nominal capacity.")
    if pack_result.recommended_layout.layers > 1:
        notes.append("Multiple layers reduce footprint but can complicate thermal paths, wiring, and serviceability.")
    if pack_result.recommended_layout.total_empty_group_slots > 0:
        notes.append("The recommended grouped layout includes unused group slots in the rectangular envelope estimate.")
    notes.append("Add real margin for cell holders, insulation, busbars, BMS, wiring, padding, and enclosure walls.")
    return notes


def validate_args(args: argparse.Namespace) -> None:
    if args.chemistry is None and args.cell_nominal_v is None:
        raise ValueError("provide --chemistry or --cell-nominal-v")
    if args.cell_format is None and args.shape is None:
        raise ValueError("provide --cell-format or --shape")

    series_modes = [args.series_count is not None, args.bus_class is not None, args.target_pack_v is not None]
    if sum(series_modes) != 1:
        raise ValueError("choose exactly one of --series-count, --bus-class, or --target-pack-v")

    if args.parallel_count is not None and any(
        value is not None for value in (args.target_capacity_ah, args.target_energy_wh, args.target_discharge_a)
    ):
        raise ValueError("use --parallel-count by itself, or derive P from targets, but not both")

    if args.parallel_count is None and all(
        value is None for value in (args.target_capacity_ah, args.target_energy_wh, args.target_discharge_a)
    ):
        raise ValueError(
            "provide --parallel-count or at least one of --target-capacity-ah, --target-energy-wh, or --target-discharge-a"
        )

    if args.target_discharge_a is not None and args.cell_continuous_a is None:
        raise ValueError("--target-discharge-a requires --cell-continuous-a")

    if args.cell_format is not None and args.shape is not None:
        raise ValueError("use either --cell-format or --shape, not both")

    if args.shape == "cylindrical":
        if args.diameter_mm is None or args.cell_height_mm is None:
            raise ValueError("custom cylindrical cells require --diameter-mm and --cell-height-mm")
    if args.shape == "prismatic":
        if args.cell_width_mm is None or args.cell_depth_mm is None or args.cell_height_mm is None:
            raise ValueError("custom prismatic cells require --cell-width-mm, --cell-depth-mm, and --cell-height-mm")

    if args.max_layers < 1:
        raise ValueError("--max-layers must be at least 1")
    if args.top_n < 1:
        raise ValueError("--top-n must be at least 1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate S/P topology and compact battery-cell layouts.",
    )
    parser.add_argument("--chemistry", choices=sorted(CHEMISTRY_PRESETS.keys()))
    parser.add_argument("--cell-nominal-v", type=positive_number, help="Nominal voltage of one cell.")
    parser.add_argument("--cell-capacity-ah", required=True, type=positive_number, help="Capacity of one cell in Ah.")
    parser.add_argument("--cell-continuous-a", type=positive_number, help="Continuous current rating of one cell in A.")

    parser.add_argument("--cell-format", choices=sorted(FORM_FACTOR_PRESETS.keys()), help="Preset cylindrical form factor.")
    parser.add_argument("--shape", choices=["cylindrical", "prismatic"], help="Custom cell geometry.")
    parser.add_argument("--diameter-mm", type=positive_number, help="Diameter for custom cylindrical cells.")
    parser.add_argument("--cell-width-mm", type=positive_number, help="Width for custom prismatic cells.")
    parser.add_argument("--cell-depth-mm", type=positive_number, help="Depth for custom prismatic cells.")
    parser.add_argument("--cell-height-mm", type=positive_number, help="Height for custom cells.")

    parser.add_argument("--series-count", type=positive_int, help="Exact series count, such as 3 for 3S.")
    parser.add_argument("--bus-class", choices=[12, 24, 48], type=positive_int, help="Common bus class.")
    parser.add_argument("--target-pack-v", type=positive_number, help="Target nominal pack voltage.")

    parser.add_argument("--parallel-count", type=positive_int, help="Exact parallel count, such as 3 for 3P.")
    parser.add_argument("--target-capacity-ah", type=positive_number, help="Target pack capacity in Ah.")
    parser.add_argument("--target-energy-wh", type=positive_number, help="Target nominal pack energy in Wh.")
    parser.add_argument("--target-discharge-a", type=positive_number, help="Target pack current in A.")

    parser.add_argument("--layout-goal", choices=["balanced", "compact", "footprint", "flat"], default="balanced")
    parser.add_argument("--cell-spacing-mm", type=positive_number, default=2.0)
    parser.add_argument("--series-gap-mm", type=positive_number, default=4.0)
    parser.add_argument("--layer-gap-mm", type=positive_number, default=5.0)
    parser.add_argument("--max-layers", type=positive_int, default=2)
    parser.add_argument("--top-n", type=positive_int, default=3)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def render_text(
    geometry: CellGeometry,
    result: PackResult,
) -> str:
    lines: list[str] = []
    lines.append("Cell Pack Layout Summary")
    lines.append(f"- Cell geometry: {geometry.label} ({geometry.shape}), {geometry.plan_width_mm:.1f} x {geometry.plan_depth_mm:.1f} x {geometry.height_mm:.1f} mm")
    lines.append(f"- Recommended topology: {result.series_count}S{result.parallel_count}P")
    lines.append(f"- Total cells: {result.total_cells}")
    lines.append(f"- Pack nominal voltage: {result.pack_nominal_v:.2f} V")
    lines.append(f"- Pack capacity: {result.pack_capacity_ah:.2f} Ah")
    lines.append(f"- Pack nominal energy: {result.pack_energy_wh:.1f} Wh")
    if result.max_continuous_current_a is not None:
        lines.append(f"- Max continuous current by cell rating: {result.max_continuous_current_a:.1f} A")
    if result.target_pack_v is not None:
        lines.append(f"- Voltage target used: {result.target_pack_v:.2f} V")
    if result.parallel_by_capacity is not None:
        lines.append(f"- Parallel count by capacity: {result.parallel_by_capacity}P")
    if result.parallel_by_energy is not None:
        lines.append(f"- Parallel count by energy: {result.parallel_by_energy}P")
    if result.parallel_by_current is not None:
        lines.append(f"- Parallel count by current: {result.parallel_by_current}P")

    lines.append("")
    lines.append("Recommended Layout")
    recommended = result.recommended_layout
    lines.append(
        f"- Goal: {recommended.layout_goal}"
    )
    lines.append(
        f"- Envelope: {recommended.width_mm:.1f} x {recommended.depth_mm:.1f} x {recommended.height_mm:.1f} mm"
    )
    lines.append(
        f"- Layers: {recommended.layers} layer(s), {recommended.groups_per_layer} series groups per layer"
    )
    lines.append(
        f"- Parallel cluster: {recommended.parallel_cluster_rows} x {recommended.parallel_cluster_cols} for each {result.parallel_count}P group"
    )
    lines.append(
        f"- Series-group grid: {recommended.series_group_rows} x {recommended.series_group_cols} per layer"
    )
    if recommended.parallel_cluster_empty_slots > 0:
        lines.append(f"- Empty slots inside cluster envelope: {recommended.parallel_cluster_empty_slots}")
    if recommended.total_empty_group_slots > 0:
        lines.append(f"- Empty series-group slots in envelope: {recommended.total_empty_group_slots}")

    if result.alternative_layouts:
        lines.append("")
        lines.append("Alternatives")
        for layout in result.alternative_layouts:
            lines.append(
                f"- {layout.width_mm:.1f} x {layout.depth_mm:.1f} x {layout.height_mm:.1f} mm, "
                f"{layout.layers} layer(s), cluster {layout.parallel_cluster_rows}x{layout.parallel_cluster_cols}, "
                f"group grid {layout.series_group_rows}x{layout.series_group_cols}"
            )

    lines.append("")
    lines.append("Notes")
    for note in result.notes:
        lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)
        geometry = resolve_cell_geometry(args)
        cell_nominal_v = resolve_cell_nominal_v(args)
        series_count, target_pack_v = resolve_series_count(args, cell_nominal_v)
        parallel_count, by_capacity, by_energy, by_current = resolve_parallel_counts(args, series_count, cell_nominal_v)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    total_cells = series_count * parallel_count
    pack_nominal_v = series_count * cell_nominal_v
    pack_capacity_ah = parallel_count * args.cell_capacity_ah
    pack_energy_wh = pack_nominal_v * pack_capacity_ah
    max_continuous_current_a = None
    if args.cell_continuous_a is not None:
        max_continuous_current_a = parallel_count * args.cell_continuous_a

    layouts = enumerate_layouts(series_count, parallel_count, geometry, args)
    recommended_layout = layouts[0]
    alternatives = layouts[1:args.top_n]

    provisional = PackResult(
        series_count=series_count,
        parallel_count=parallel_count,
        total_cells=total_cells,
        pack_nominal_v=pack_nominal_v,
        pack_capacity_ah=pack_capacity_ah,
        pack_energy_wh=pack_energy_wh,
        target_pack_v=target_pack_v,
        target_capacity_ah=args.target_capacity_ah,
        target_energy_wh=args.target_energy_wh,
        target_discharge_a=args.target_discharge_a,
        parallel_by_capacity=by_capacity,
        parallel_by_energy=by_energy,
        parallel_by_current=by_current,
        max_continuous_current_a=max_continuous_current_a,
        recommended_layout=recommended_layout,
        alternative_layouts=alternatives,
        notes=[],
    )
    provisional.notes = build_notes(args, geometry, provisional)

    if args.json:
        payload = {
            "inputs": {
                "chemistry": args.chemistry,
                "cell_nominal_v": cell_nominal_v,
                "cell_capacity_ah": args.cell_capacity_ah,
                "cell_continuous_a": args.cell_continuous_a,
                "cell_format": args.cell_format,
                "shape": args.shape,
                "series_count": args.series_count,
                "bus_class": args.bus_class,
                "target_pack_v": args.target_pack_v,
                "parallel_count": args.parallel_count,
                "target_capacity_ah": args.target_capacity_ah,
                "target_energy_wh": args.target_energy_wh,
                "target_discharge_a": args.target_discharge_a,
                "layout_goal": args.layout_goal,
            },
            "cell_geometry": asdict(geometry),
            "result": asdict(provisional),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(geometry, provisional))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
