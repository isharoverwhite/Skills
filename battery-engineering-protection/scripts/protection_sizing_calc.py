#!/usr/bin/env python3
"""
Select preliminary BMS specs and conservative DC fuse and wire sizing.
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

STANDARD_FUSES_A = [
    5, 7.5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100,
    110, 125, 150, 175, 200, 225, 250, 300, 350, 400,
]

STANDARD_WIRES = [
    ("AWG 20", 0.52),
    ("AWG 18", 0.82),
    ("AWG 16", 1.31),
    ("AWG 14", 2.08),
    ("AWG 12", 3.31),
    ("AWG 10", 5.26),
    ("AWG 8", 8.37),
    ("AWG 6", 13.3),
    ("AWG 4", 21.1),
    ("AWG 2", 33.6),
    ("AWG 1", 42.4),
    ("AWG 1/0", 53.5),
    ("AWG 2/0", 67.4),
    ("AWG 3/0", 85.0),
    ("AWG 4/0", 107.2),
    ("120 mm2", 120.0),
    ("150 mm2", 150.0),
    ("185 mm2", 185.0),
]


@dataclass
class WireRecommendation:
    path_name: str
    current_a: float
    one_way_length_m: float
    max_drop_pct: float
    required_area_drop_mm2: float
    required_area_thermal_mm2: float
    selected_wire_label: str
    selected_area_mm2: float
    estimated_ampacity_a: float
    selected_fuse_a: float | None
    voltage_drop_v: float
    voltage_drop_pct: float


@dataclass
class BMSRecommendation:
    chemistry: str
    series_count: int
    pack_nominal_v: float
    recommended_continuous_discharge_a: float | None
    recommended_peak_discharge_a: float | None
    recommended_continuous_charge_a: float | None
    pack_capacity_ah: float | None
    suggested_temp_sensor_count: int
    balancing_guidance: str
    feature_notes: list[str]


@dataclass
class ProtectionResult:
    series_count: int
    pack_nominal_v: float
    discharge_current_a: float | None
    surge_current_a: float | None
    charge_current_a: float | None
    bms: BMSRecommendation
    discharge_path: WireRecommendation | None
    charge_path: WireRecommendation | None
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


def round_up(value: float, step: float = 5.0) -> float:
    if value <= 0:
        return step
    return math.ceil(value / step) * step


def resolve_cell_nominal_v(args: argparse.Namespace) -> float:
    if args.cell_nominal_v is not None:
        return args.cell_nominal_v
    if args.chemistry is not None:
        return CHEMISTRY_PRESETS[args.chemistry]["cell_nominal_v"]
    raise ValueError("provide --chemistry or --cell-nominal-v")


def resolve_series_count(args: argparse.Namespace, cell_nominal_v: float) -> int:
    modes = [args.series_count is not None, args.bus_class is not None, args.target_pack_v is not None]
    if sum(modes) != 1:
        raise ValueError("choose exactly one of --series-count, --bus-class, or --target-pack-v")

    if args.series_count is not None:
        return args.series_count
    if args.bus_class is not None:
        if args.chemistry in COMMON_SERIES and args.bus_class in COMMON_SERIES[args.chemistry]:
            return COMMON_SERIES[args.chemistry][args.bus_class]
        return ceil_units(args.bus_class / cell_nominal_v)
    return ceil_units(args.target_pack_v / cell_nominal_v)


def derive_current_from_power(
    power_w: float | None,
    pack_nominal_v: float,
    load_side: str,
    inverter_efficiency: float,
) -> float | None:
    if power_w is None:
        return None
    battery_power_w = power_w if load_side == "dc" else power_w / inverter_efficiency
    return battery_power_w / pack_nominal_v


def resolve_discharge_current(args: argparse.Namespace, pack_nominal_v: float) -> tuple[float | None, float | None]:
    continuous_options = [
        value for value in (
            args.discharge_current_a,
            derive_current_from_power(args.load_w, pack_nominal_v, args.load_side, args.inverter_efficiency),
        ) if value is not None
    ]
    surge_options = [
        value for value in (
            args.surge_current_a,
            derive_current_from_power(args.surge_w, pack_nominal_v, args.load_side, args.inverter_efficiency),
        ) if value is not None
    ]
    discharge_current = max(continuous_options) if continuous_options else None
    surge_current = max(surge_options) if surge_options else None
    return discharge_current, surge_current


def resolve_charge_current(args: argparse.Namespace, pack_nominal_v: float) -> float | None:
    options = [
        value for value in (
            args.charge_current_a,
            args.charge_w / pack_nominal_v if args.charge_w is not None else None,
        ) if value is not None
    ]
    return max(options) if options else None


def infer_pack_capacity_ah(args: argparse.Namespace) -> float | None:
    if args.pack_capacity_ah is not None:
        return args.pack_capacity_ah
    if args.parallel_count is not None and args.cell_capacity_ah is not None:
        return args.parallel_count * args.cell_capacity_ah
    return None


def recommend_bms(
    args: argparse.Namespace,
    series_count: int,
    pack_nominal_v: float,
    discharge_current_a: float | None,
    surge_current_a: float | None,
    charge_current_a: float | None,
) -> BMSRecommendation:
    pack_capacity_ah = infer_pack_capacity_ah(args)
    discharge_rating = None if discharge_current_a is None else round_up(discharge_current_a * args.bms_headroom)
    peak_rating = None if surge_current_a is None else round_up(surge_current_a * args.peak_headroom)
    charge_rating = None if charge_current_a is None else round_up(charge_current_a * args.bms_headroom)

    temp_sensor_count = 1
    if (discharge_current_a or 0) > 50 or series_count > 8 or (pack_capacity_ah or 0) > 80:
        temp_sensor_count = 2
    if (discharge_current_a or 0) > 150 or series_count > 16 or (pack_capacity_ah or 0) > 200:
        temp_sensor_count = 3

    if args.reused_cells or series_count > 16 or (pack_capacity_ah or 0) > 150:
        balancing_guidance = "Consider active balancing or at least a stronger balancing strategy than basic low-current passive balancing."
    elif (pack_capacity_ah or 0) > 80:
        balancing_guidance = "Prefer passive balancing with meaningful current, roughly 100-200 mA or better for matched new cells."
    else:
        balancing_guidance = "Passive balancing is usually acceptable for matched new cells; look for a sane balancing current rather than a token feature."

    feature_notes: list[str] = []
    if args.chemistry == "lfp":
        feature_notes.append("Require low-temperature charge cutoff or an equivalent control strategy for LFP.")
    if args.chemistry in {"nmc", "li-ion"}:
        feature_notes.append("Common 3.7 V lithium-ion and NMC packs need careful charger compatibility and accurate high and low voltage thresholds.")
    if args.needs_comms:
        feature_notes.append("Prefer a BMS with communication support that matches the inverter or charger integration path.")
    if args.load_side == "ac" and ((args.load_w or 0) > 500 or (discharge_current_a or 0) * pack_nominal_v > 1000):
        feature_notes.append("Consider precharge planning because inverter input capacitance can stress contactors and BMS MOSFETs.")
    if args.reused_cells:
        feature_notes.append("Repurposed or mixed cells increase the importance of balancing quality and conservative current settings.")
    feature_notes.append("Verify the BMS charge and discharge current are both compatible with the actual charger and load path.")

    return BMSRecommendation(
        chemistry=args.chemistry if args.chemistry is not None else "custom",
        series_count=series_count,
        pack_nominal_v=pack_nominal_v,
        recommended_continuous_discharge_a=discharge_rating,
        recommended_peak_discharge_a=peak_rating,
        recommended_continuous_charge_a=charge_rating,
        pack_capacity_ah=pack_capacity_ah,
        suggested_temp_sensor_count=temp_sensor_count,
        balancing_guidance=balancing_guidance,
        feature_notes=feature_notes,
    )


def choose_fuse(required_current_a: float, max_safe_fuse_a: float) -> float | None:
    for fuse in STANDARD_FUSES_A:
        if fuse >= required_current_a and fuse <= max_safe_fuse_a + 1e-9:
            return fuse
    return None


def choose_wire_and_fuse(
    path_name: str,
    current_a: float,
    one_way_length_m: float,
    pack_nominal_v: float,
    max_drop_pct: float,
    args: argparse.Namespace,
) -> WireRecommendation:
    allowed_drop_v = pack_nominal_v * max_drop_pct / 100.0
    required_area_drop = (2 * one_way_length_m * current_a * args.copper_resistivity_ohm_mm2_per_m) / allowed_drop_v
    required_area_thermal = current_a / args.amps_per_mm2
    required_fuse_current = current_a * args.fuse_headroom

    for label, area in STANDARD_WIRES:
        ampacity = area * args.amps_per_mm2
        max_safe_fuse = ampacity * args.fuse_wire_utilization
        if area + 1e-9 < max(required_area_drop, required_area_thermal):
            continue
        selected_fuse = choose_fuse(required_fuse_current, max_safe_fuse)
        if selected_fuse is None:
            continue
        voltage_drop_v = (2 * one_way_length_m * current_a * args.copper_resistivity_ohm_mm2_per_m) / area
        return WireRecommendation(
            path_name=path_name,
            current_a=current_a,
            one_way_length_m=one_way_length_m,
            max_drop_pct=max_drop_pct,
            required_area_drop_mm2=required_area_drop,
            required_area_thermal_mm2=required_area_thermal,
            selected_wire_label=label,
            selected_area_mm2=area,
            estimated_ampacity_a=ampacity,
            selected_fuse_a=selected_fuse,
            voltage_drop_v=voltage_drop_v,
            voltage_drop_pct=(voltage_drop_v / pack_nominal_v) * 100.0,
        )

    area = max(
        required_area_drop,
        required_area_thermal,
        required_fuse_current / (args.amps_per_mm2 * args.fuse_wire_utilization),
    )
    ampacity = area * args.amps_per_mm2
    voltage_drop_v = (2 * one_way_length_m * current_a * args.copper_resistivity_ohm_mm2_per_m) / area
    selected_fuse = choose_fuse(required_fuse_current, ampacity * args.fuse_wire_utilization)
    return WireRecommendation(
        path_name=path_name,
        current_a=current_a,
        one_way_length_m=one_way_length_m,
        max_drop_pct=max_drop_pct,
        required_area_drop_mm2=required_area_drop,
        required_area_thermal_mm2=required_area_thermal,
        selected_wire_label=f"custom >= {area:.1f} mm2",
        selected_area_mm2=area,
        estimated_ampacity_a=ampacity,
        selected_fuse_a=selected_fuse,
        voltage_drop_v=voltage_drop_v,
        voltage_drop_pct=(voltage_drop_v / pack_nominal_v) * 100.0,
    )


def build_notes(
    args: argparse.Namespace,
    pack_nominal_v: float,
    discharge_path: WireRecommendation | None,
    charge_path: WireRecommendation | None,
) -> list[str]:
    notes: list[str] = []
    if discharge_path is not None and discharge_path.required_area_drop_mm2 > discharge_path.required_area_thermal_mm2:
        notes.append("Discharge wire sizing is voltage-drop-limited rather than thermal-limited.")
    if charge_path is not None and charge_path.required_area_drop_mm2 > charge_path.required_area_thermal_mm2:
        notes.append("Charge wire sizing is voltage-drop-limited rather than thermal-limited.")
    if args.chemistry == "lfp":
        notes.append("LFP systems should explicitly validate low-temperature charging behavior.")
    if (args.load_w or 0) > 1000 or (args.discharge_current_a or 0) > 100:
        notes.append("High-power systems need real attention on lug heating, busbar design, and fault-current interruption.")
    if pack_nominal_v >= 48:
        notes.append("Verify that the fuse, breaker, contactor, and BMS are all rated for the real DC voltage, not just a nominal label.")
    notes.append("Keep the main fuse as close to battery positive as practical and verify interrupt rating against the battery fault capability.")
    notes.append("Final conductor choice still depends on insulation rating, bundling, ambient temperature, enclosure, and code requirements.")
    return notes


def validate_args(args: argparse.Namespace) -> None:
    if args.chemistry is None and args.cell_nominal_v is None:
        raise ValueError("provide --chemistry or --cell-nominal-v")
    if not (0 < args.inverter_efficiency <= 1):
        raise ValueError("--inverter-efficiency must be between 0 and 1")
    if args.amps_per_mm2 <= 0:
        raise ValueError("--amps-per-mm2 must be greater than zero")
    if args.fuse_wire_utilization <= 0 or args.fuse_wire_utilization > 1:
        raise ValueError("--fuse-wire-utilization must be between 0 and 1")
    if args.bms_headroom < 1 or args.peak_headroom < 1 or args.fuse_headroom < 1:
        raise ValueError("headroom values must be at least 1")
    if args.surge_w is not None and args.load_w is not None and args.surge_w < args.load_w:
        raise ValueError("--surge-w must be greater than or equal to --load-w")
    if args.surge_current_a is not None and args.discharge_current_a is not None and args.surge_current_a < args.discharge_current_a:
        raise ValueError("--surge-current-a must be greater than or equal to --discharge-current-a")

    has_discharge_basis = any(value is not None for value in (args.discharge_current_a, args.load_w))
    has_charge_basis = any(value is not None for value in (args.charge_current_a, args.charge_w))
    if not has_discharge_basis and not has_charge_basis:
        raise ValueError("provide at least one discharge or charge input")

    if args.parallel_count is not None and args.cell_capacity_ah is None and args.pack_capacity_ah is None:
        raise ValueError("--parallel-count is only useful with --cell-capacity-ah or --pack-capacity-ah")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select preliminary BMS specs and conservative DC fuse and wire sizing.",
    )
    parser.add_argument("--chemistry", choices=sorted(CHEMISTRY_PRESETS.keys()))
    parser.add_argument("--cell-nominal-v", type=positive_number)
    parser.add_argument("--series-count", type=positive_int)
    parser.add_argument("--bus-class", choices=[12, 24, 48], type=positive_int)
    parser.add_argument("--target-pack-v", type=positive_number)
    parser.add_argument("--parallel-count", type=positive_int)
    parser.add_argument("--cell-capacity-ah", type=positive_number)
    parser.add_argument("--pack-capacity-ah", type=positive_number)

    parser.add_argument("--load-side", choices=["dc", "ac"], default="dc")
    parser.add_argument("--load-w", type=positive_number)
    parser.add_argument("--surge-w", type=positive_number)
    parser.add_argument("--inverter-efficiency", type=positive_number, default=0.9)
    parser.add_argument("--discharge-current-a", type=positive_number)
    parser.add_argument("--surge-current-a", type=positive_number)
    parser.add_argument("--charge-current-a", type=positive_number)
    parser.add_argument("--charge-w", type=positive_number)

    parser.add_argument("--discharge-length-m", type=positive_number, default=1.0)
    parser.add_argument("--charge-length-m", type=positive_number)
    parser.add_argument("--max-drop-pct", type=positive_number, default=3.0)
    parser.add_argument("--charge-drop-pct", type=positive_number)

    parser.add_argument("--bms-headroom", type=positive_number, default=1.25)
    parser.add_argument("--peak-headroom", type=positive_number, default=1.15)
    parser.add_argument("--fuse-headroom", type=positive_number, default=1.25)
    parser.add_argument("--amps-per-mm2", type=positive_number, default=5.0)
    parser.add_argument("--fuse-wire-utilization", type=positive_number, default=0.9)
    parser.add_argument("--copper-resistivity-ohm-mm2-per-m", type=positive_number, default=0.0175)
    parser.add_argument("--needs-comms", action="store_true")
    parser.add_argument("--reused-cells", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def render_text(result: ProtectionResult) -> str:
    lines: list[str] = []
    lines.append("Protection Sizing Summary")
    lines.append(f"- Pack support: {result.series_count}S, {result.pack_nominal_v:.2f} V nominal")
    if result.discharge_current_a is not None:
        lines.append(f"- Discharge current basis: {result.discharge_current_a:.1f} A")
    if result.surge_current_a is not None:
        lines.append(f"- Surge current basis: {result.surge_current_a:.1f} A")
    if result.charge_current_a is not None:
        lines.append(f"- Charge current basis: {result.charge_current_a:.1f} A")

    lines.append("")
    lines.append("BMS Recommendation")
    lines.append(f"- Chemistry: {result.bms.chemistry}")
    if result.bms.pack_capacity_ah is not None:
        lines.append(f"- Pack capacity context: {result.bms.pack_capacity_ah:.1f} Ah")
    if result.bms.recommended_continuous_discharge_a is not None:
        lines.append(f"- Continuous discharge rating: >= {result.bms.recommended_continuous_discharge_a:.0f} A")
    if result.bms.recommended_peak_discharge_a is not None:
        lines.append(f"- Peak discharge rating: >= {result.bms.recommended_peak_discharge_a:.0f} A")
    if result.bms.recommended_continuous_charge_a is not None:
        lines.append(f"- Continuous charge rating: >= {result.bms.recommended_continuous_charge_a:.0f} A")
    lines.append(f"- Suggested temperature sensors: {result.bms.suggested_temp_sensor_count}")
    lines.append(f"- Balancing guidance: {result.bms.balancing_guidance}")
    for note in result.bms.feature_notes:
        lines.append(f"- Feature note: {note}")

    if result.discharge_path is not None:
        path = result.discharge_path
        lines.append("")
        lines.append("Discharge Path")
        lines.append(f"- Wire: {path.selected_wire_label} ({path.selected_area_mm2:.1f} mm2)")
        lines.append(f"- Fuse: {path.selected_fuse_a if path.selected_fuse_a is not None else 'manual review required'} A")
        lines.append(f"- Estimated ampacity by heuristic: {path.estimated_ampacity_a:.1f} A")
        lines.append(f"- Estimated voltage drop: {path.voltage_drop_v:.3f} V ({path.voltage_drop_pct:.2f}%)")
        lines.append(
            f"- Minimum area by drop: {path.required_area_drop_mm2:.2f} mm2, "
            f"by thermal heuristic: {path.required_area_thermal_mm2:.2f} mm2"
        )

    if result.charge_path is not None:
        path = result.charge_path
        lines.append("")
        lines.append("Charge Path")
        lines.append(f"- Wire: {path.selected_wire_label} ({path.selected_area_mm2:.1f} mm2)")
        lines.append(f"- Fuse: {path.selected_fuse_a if path.selected_fuse_a is not None else 'manual review required'} A")
        lines.append(f"- Estimated ampacity by heuristic: {path.estimated_ampacity_a:.1f} A")
        lines.append(f"- Estimated voltage drop: {path.voltage_drop_v:.3f} V ({path.voltage_drop_pct:.2f}%)")
        lines.append(
            f"- Minimum area by drop: {path.required_area_drop_mm2:.2f} mm2, "
            f"by thermal heuristic: {path.required_area_thermal_mm2:.2f} mm2"
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
        cell_nominal_v = resolve_cell_nominal_v(args)
        series_count = resolve_series_count(args, cell_nominal_v)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    pack_nominal_v = series_count * cell_nominal_v
    discharge_current_a, surge_current_a = resolve_discharge_current(args, pack_nominal_v)
    charge_current_a = resolve_charge_current(args, pack_nominal_v)

    bms = recommend_bms(
        args=args,
        series_count=series_count,
        pack_nominal_v=pack_nominal_v,
        discharge_current_a=discharge_current_a,
        surge_current_a=surge_current_a,
        charge_current_a=charge_current_a,
    )

    discharge_path = None
    if discharge_current_a is not None:
        discharge_path = choose_wire_and_fuse(
            path_name="discharge",
            current_a=discharge_current_a,
            one_way_length_m=args.discharge_length_m,
            pack_nominal_v=pack_nominal_v,
            max_drop_pct=args.max_drop_pct,
            args=args,
        )

    charge_path = None
    if charge_current_a is not None:
        charge_path = choose_wire_and_fuse(
            path_name="charge",
            current_a=charge_current_a,
            one_way_length_m=args.charge_length_m or args.discharge_length_m,
            pack_nominal_v=pack_nominal_v,
            max_drop_pct=args.charge_drop_pct or args.max_drop_pct,
            args=args,
        )

    result = ProtectionResult(
        series_count=series_count,
        pack_nominal_v=pack_nominal_v,
        discharge_current_a=discharge_current_a,
        surge_current_a=surge_current_a,
        charge_current_a=charge_current_a,
        bms=bms,
        discharge_path=discharge_path,
        charge_path=charge_path,
        notes=build_notes(args, pack_nominal_v, discharge_path, charge_path),
    )

    if args.json:
        payload = {
            "inputs": {
                "chemistry": args.chemistry,
                "cell_nominal_v": cell_nominal_v,
                "series_count": args.series_count,
                "bus_class": args.bus_class,
                "target_pack_v": args.target_pack_v,
                "load_side": args.load_side,
                "load_w": args.load_w,
                "surge_w": args.surge_w,
                "discharge_current_a": args.discharge_current_a,
                "surge_current_a": args.surge_current_a,
                "charge_current_a": args.charge_current_a,
                "charge_w": args.charge_w,
                "discharge_length_m": args.discharge_length_m,
                "charge_length_m": args.charge_length_m,
                "max_drop_pct": args.max_drop_pct,
                "charge_drop_pct": args.charge_drop_pct,
                "pack_capacity_ah": args.pack_capacity_ah,
                "parallel_count": args.parallel_count,
                "cell_capacity_ah": args.cell_capacity_ah,
            },
            "result": asdict(result),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(result))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
