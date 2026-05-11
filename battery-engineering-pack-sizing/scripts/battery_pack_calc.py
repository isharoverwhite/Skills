#!/usr/bin/env python3
"""
Battery pack sizing helper for low-voltage energy storage.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass


CHEMISTRY_PRESETS = {
    "lfp": {
        "cell_nominal_v": 3.2,
        "max_dod": 0.8,
        "summary": "Default for UPS and backup systems because cycle life and thermal behavior are easier to manage.",
    },
    "li-ion": {
        "cell_nominal_v": 3.7,
        "max_dod": 0.8,
        "summary": "Common 3.7 V lithium-ion cylindrical or pouch cells, useful when the exact subtype is not specified but tighter voltage and thermal discipline than LFP is still expected.",
    },
    "nmc": {
        "cell_nominal_v": 3.6,
        "max_dod": 0.8,
        "summary": "Higher energy density, but usually needs tighter thermal and protection discipline than LFP.",
    },
    "lto": {
        "cell_nominal_v": 2.3,
        "max_dod": 0.9,
        "summary": "Good for very high cycle life, cold weather, and fast charging, but usually expensive and bulky.",
    },
    "lead-acid": {
        "cell_nominal_v": 2.0,
        "max_dod": 0.5,
        "summary": "Legacy or cost-driven option with much lower usable depth of discharge and cycle life.",
    },
}

COMMON_SERIES = {
    "lfp": {12: 4, 24: 8, 48: 16},
    "li-ion": {12: 3, 24: 7, 48: 13},
    "nmc": {12: 3, 24: 7, 48: 13},
    "lto": {12: 6, 24: 12, 48: 24},
    "lead-acid": {12: 6, 24: 12, 48: 24},
}

DEFAULT_EFFICIENCY = {
    "ups": 0.88,
    "dc-backup": 0.94,
    "portable-power": 0.9,
    "bench-supply": 0.92,
    "inverter": 0.9,
}

DEFAULT_CURRENT_LIMIT = {
    "ups": 50.0,
    "dc-backup": 40.0,
    "portable-power": 40.0,
    "bench-supply": 30.0,
    "inverter": 60.0,
}

PREFERRED_BUS_ORDER = {
    "ups": [24, 48, 12],
    "dc-backup": [24, 12, 48],
    "portable-power": [24, 48, 12],
    "bench-supply": [24, 48, 12],
    "inverter": [48, 24, 12],
}


@dataclass
class Candidate:
    label: str
    bus_class_v: int | None
    series_count: int
    parallel_count: int
    pack_nominal_v: float
    pack_capacity_ah: float
    pack_energy_wh: float
    design_energy_wh: float
    load_energy_wh: float
    required_pack_power_w: float
    required_pack_current_a: float
    required_peak_current_a: float | None
    max_continuous_current_a: float
    max_peak_current_a: float | None
    minimum_parallel_by_energy: int
    minimum_parallel_by_current: int
    minimum_parallel_by_peak: int | None
    limiting_factor: str
    suggested_bms_continuous_a: float
    suggested_bms_peak_a: float | None
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
    if args.chemistry:
        return CHEMISTRY_PRESETS[args.chemistry]["cell_nominal_v"]
    raise ValueError("provide --chemistry or --cell-nominal-v")


def resolve_max_dod(args: argparse.Namespace) -> float:
    if args.max_dod is not None:
        return args.max_dod
    if args.chemistry:
        return CHEMISTRY_PRESETS[args.chemistry]["max_dod"]
    return 0.8


def resolve_efficiency(args: argparse.Namespace) -> float:
    if args.efficiency is not None:
        return args.efficiency
    return DEFAULT_EFFICIENCY[args.use_case]


def resolve_runtime_hours(args: argparse.Namespace) -> float:
    if args.runtime_h is not None:
        return args.runtime_h
    return args.runtime_min / 60.0


def select_series_count(
    bus_class: int | None,
    target_bus_v: float | None,
    chemistry: str | None,
    cell_nominal_v: float,
) -> int:
    if bus_class is not None:
        if chemistry in COMMON_SERIES and bus_class in COMMON_SERIES[chemistry]:
            return COMMON_SERIES[chemistry][bus_class]
        return ceil_units(bus_class / cell_nominal_v)

    if target_bus_v is not None:
        common_target = int(round(target_bus_v))
        if chemistry in COMMON_SERIES and common_target in COMMON_SERIES[chemistry]:
            if abs(target_bus_v - common_target) <= 1.0:
                return COMMON_SERIES[chemistry][common_target]
        return ceil_units(target_bus_v / cell_nominal_v)

    raise ValueError("provide a bus target")


def determine_limiting_factor(
    by_energy: int,
    by_current: int,
    by_peak: int | None,
) -> str:
    sources = {"energy": by_energy, "current": by_current}
    if by_peak is not None:
        sources["peak"] = by_peak

    maximum = max(sources.values())
    winners = [name for name, value in sources.items() if value == maximum]
    if len(winners) == 1:
        return winners[0]
    return "+".join(winners)


def build_notes(
    args: argparse.Namespace,
    bus_class: int | None,
    pack_energy_wh: float,
    design_energy_wh: float,
    required_pack_current_a: float,
    max_continuous_current_a: float,
    minimum_parallel_by_energy: int,
    minimum_parallel_by_current: int,
    minimum_parallel_by_peak: int | None,
) -> list[str]:
    notes: list[str] = []

    if minimum_parallel_by_current > minimum_parallel_by_energy:
        notes.append("Continuous current, not runtime, is driving the parallel count.")
    if minimum_parallel_by_peak is not None and minimum_parallel_by_peak > max(
        minimum_parallel_by_energy,
        minimum_parallel_by_current,
    ):
        notes.append("Surge current, not steady runtime, is driving the parallel count.")
    if max_continuous_current_a / required_pack_current_a < 1.25:
        notes.append("Continuous-current headroom is slim; compare a higher bus voltage or higher-current cells.")
    if pack_energy_wh > design_energy_wh * 1.8:
        notes.append("The selected cell or module size makes the pack much larger than the design-energy target.")
    if bus_class == 12 and args.load_w > 300:
        notes.append("12 V becomes cable-heavy above a few hundred watts; compare 24 V or 48 V before finalizing.")
    if bus_class == 24 and args.use_case in {"ups", "inverter"} and args.load_w > 1000:
        notes.append("24 V can work here, but 48 V usually simplifies current, fusing, and cable sizing.")
    if args.surge_w is not None and args.cell_peak_a is None:
        notes.append("Surge sizing is incomplete because no peak-current rating was provided for the cell or module.")
    if args.chemistry == "lead-acid":
        notes.append("Lead-acid assumptions should stay conservative because usable depth of discharge and voltage sag are limiting.")
    if args.chemistry in {"nmc", "li-ion"}:
        notes.append("Common 3.7 V lithium-ion and NMC cells usually need stricter thermal and charge-limit review than LFP for workshop or UPS builds.")

    return notes


def build_candidate(
    args: argparse.Namespace,
    bus_class: int | None,
    target_bus_v: float | None,
    cell_nominal_v: float,
    max_dod: float,
    efficiency: float,
    runtime_h: float,
) -> Candidate:
    series_count = select_series_count(bus_class, target_bus_v, args.chemistry, cell_nominal_v)
    pack_nominal_v = series_count * cell_nominal_v
    load_energy_wh = args.load_w * runtime_h
    required_pack_power_w = args.load_w / efficiency
    design_energy_wh = (load_energy_wh / efficiency) * args.reserve_factor / max_dod
    required_pack_current_a = required_pack_power_w / pack_nominal_v

    required_peak_current_a = None
    if args.surge_w is not None:
        required_peak_current_a = (args.surge_w / efficiency) / pack_nominal_v

    energy_per_parallel_wh = pack_nominal_v * args.cell_capacity_ah
    minimum_parallel_by_energy = ceil_units(design_energy_wh / energy_per_parallel_wh)
    minimum_parallel_by_current = ceil_units(required_pack_current_a / args.cell_continuous_a)

    minimum_parallel_by_peak = None
    if required_peak_current_a is not None and args.cell_peak_a is not None:
        minimum_parallel_by_peak = ceil_units(required_peak_current_a / args.cell_peak_a)

    parallel_count = max(
        minimum_parallel_by_energy,
        minimum_parallel_by_current,
        minimum_parallel_by_peak or 1,
    )

    pack_capacity_ah = parallel_count * args.cell_capacity_ah
    pack_energy_wh = pack_nominal_v * pack_capacity_ah
    max_continuous_current_a = parallel_count * args.cell_continuous_a
    max_peak_current_a = None
    if args.cell_peak_a is not None:
        max_peak_current_a = parallel_count * args.cell_peak_a

    notes = build_notes(
        args=args,
        bus_class=bus_class,
        pack_energy_wh=pack_energy_wh,
        design_energy_wh=design_energy_wh,
        required_pack_current_a=required_pack_current_a,
        max_continuous_current_a=max_continuous_current_a,
        minimum_parallel_by_energy=minimum_parallel_by_energy,
        minimum_parallel_by_current=minimum_parallel_by_current,
        minimum_parallel_by_peak=minimum_parallel_by_peak,
    )

    label = f"{bus_class} V class" if bus_class is not None else f"{pack_nominal_v:.1f} V target"
    limiting_factor = determine_limiting_factor(
        minimum_parallel_by_energy,
        minimum_parallel_by_current,
        minimum_parallel_by_peak,
    )

    suggested_bms_continuous_a = round_up(required_pack_current_a * 1.25)
    suggested_bms_peak_a = None
    if required_peak_current_a is not None:
        suggested_bms_peak_a = round_up(required_peak_current_a * 1.15)

    return Candidate(
        label=label,
        bus_class_v=bus_class,
        series_count=series_count,
        parallel_count=parallel_count,
        pack_nominal_v=pack_nominal_v,
        pack_capacity_ah=pack_capacity_ah,
        pack_energy_wh=pack_energy_wh,
        design_energy_wh=design_energy_wh,
        load_energy_wh=load_energy_wh,
        required_pack_power_w=required_pack_power_w,
        required_pack_current_a=required_pack_current_a,
        required_peak_current_a=required_peak_current_a,
        max_continuous_current_a=max_continuous_current_a,
        max_peak_current_a=max_peak_current_a,
        minimum_parallel_by_energy=minimum_parallel_by_energy,
        minimum_parallel_by_current=minimum_parallel_by_current,
        minimum_parallel_by_peak=minimum_parallel_by_peak,
        limiting_factor=limiting_factor,
        suggested_bms_continuous_a=suggested_bms_continuous_a,
        suggested_bms_peak_a=suggested_bms_peak_a,
        notes=notes,
    )


def choose_recommended_candidate(
    args: argparse.Namespace,
    candidates: list[Candidate],
) -> Candidate:
    preferred_buses = list(PREFERRED_BUS_ORDER[args.use_case])
    max_preferred_current_a = args.max_preferred_current_a or DEFAULT_CURRENT_LIMIT[args.use_case]

    eligible = [
        candidate for candidate in candidates
        if candidate.required_pack_current_a <= max_preferred_current_a
    ]

    if args.use_case in {"ups", "inverter"} and args.load_w > 1000:
        preferred_buses = [48, 24, 12]
    elif args.use_case in {"dc-backup", "portable-power", "bench-supply"}:
        preferred_buses = [24, 48, 12]

    pool = eligible if eligible else candidates
    for bus_class in preferred_buses:
        for candidate in pool:
            if candidate.bus_class_v == bus_class:
                return candidate

    return min(pool, key=lambda candidate: candidate.required_pack_current_a)


def validate_args(args: argparse.Namespace) -> None:
    if args.efficiency is not None and not (0 < args.efficiency <= 1):
        raise ValueError("--efficiency must be between 0 and 1")
    if args.max_dod is not None and not (0 < args.max_dod <= 1):
        raise ValueError("--max-dod must be between 0 and 1")
    if args.reserve_factor < 1:
        raise ValueError("--reserve-factor must be at least 1")
    if args.surge_w is not None and args.surge_w < args.load_w:
        raise ValueError("--surge-w must be greater than or equal to --load-w")
    if args.cell_peak_a is not None and args.cell_peak_a < args.cell_continuous_a:
        raise ValueError("--cell-peak-a must be greater than or equal to --cell-continuous-a")
    if args.bus_class is not None and args.target_bus_v is not None:
        raise ValueError("use either --bus-class or --target-bus-v, not both")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Size a low-voltage battery pack from runtime and current requirements.",
    )
    parser.add_argument(
        "--use-case",
        choices=sorted(DEFAULT_EFFICIENCY.keys()),
        default="ups",
        help="Helps set sensible defaults for efficiency and bus preference.",
    )
    parser.add_argument("--load-w", required=True, type=positive_number, help="Continuous load in watts.")
    parser.add_argument("--surge-w", type=positive_number, help="Peak or startup load in watts.")

    runtime_group = parser.add_mutually_exclusive_group(required=True)
    runtime_group.add_argument("--runtime-min", type=positive_number, help="Required runtime in minutes.")
    runtime_group.add_argument("--runtime-h", type=positive_number, help="Required runtime in hours.")

    parser.add_argument(
        "--chemistry",
        choices=sorted(CHEMISTRY_PRESETS.keys()),
        help="Optional chemistry preset for nominal cell voltage and default usable depth of discharge.",
    )
    parser.add_argument("--cell-nominal-v", type=positive_number, help="Nominal voltage of one cell or module.")
    parser.add_argument("--cell-capacity-ah", required=True, type=positive_number, help="Capacity per cell or module in Ah.")
    parser.add_argument("--cell-continuous-a", required=True, type=positive_number, help="Continuous current per cell or module in A.")
    parser.add_argument("--cell-peak-a", type=positive_number, help="Peak current per cell or module in A.")

    parser.add_argument("--bus-class", choices=[12, 24, 48], type=positive_int, help="Evaluate one common bus class.")
    parser.add_argument("--target-bus-v", type=positive_number, help="Evaluate one custom pack target voltage.")
    parser.add_argument(
        "--compare-common-buses",
        action="store_true",
        help="Compare 12 V, 24 V, and 48 V classes instead of a single target.",
    )

    parser.add_argument("--efficiency", type=positive_number, help="Overall discharge-side efficiency as a fraction.")
    parser.add_argument("--max-dod", type=positive_number, help="Usable depth of discharge as a fraction.")
    parser.add_argument("--reserve-factor", type=positive_number, default=1.15, help="Aging and reserve multiplier.")
    parser.add_argument(
        "--max-preferred-current-a",
        type=positive_number,
        help="Soft limit for choosing the recommended bus class when comparing candidates.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args()


def render_text(
    args: argparse.Namespace,
    cell_nominal_v: float,
    max_dod: float,
    efficiency: float,
    runtime_h: float,
    candidates: list[Candidate],
    recommended: Candidate,
) -> str:
    lines: list[str] = []
    lines.append("Battery Pack Sizing Summary")
    lines.append(f"- Use case: {args.use_case}")
    lines.append(f"- Load: {args.load_w:.0f} W continuous")
    if args.surge_w is not None:
        lines.append(f"- Surge: {args.surge_w:.0f} W")
    lines.append(f"- Runtime: {runtime_h:.2f} h")
    if args.chemistry:
        lines.append(f"- Chemistry: {args.chemistry} ({CHEMISTRY_PRESETS[args.chemistry]['summary']})")
    lines.append(f"- Cell nominal voltage: {cell_nominal_v:.2f} V")
    lines.append(f"- Cell capacity: {args.cell_capacity_ah:.2f} Ah")
    lines.append(f"- Cell continuous current: {args.cell_continuous_a:.2f} A")
    if args.cell_peak_a is not None:
        lines.append(f"- Cell peak current: {args.cell_peak_a:.2f} A")
    lines.append(f"- Efficiency: {efficiency:.2f}")
    lines.append(f"- Max DoD: {max_dod:.2f}")
    lines.append(f"- Reserve factor: {args.reserve_factor:.2f}")
    lines.append("")
    lines.append("Candidates")

    for candidate in candidates:
        marker = "*" if candidate == recommended else "-"
        lines.append(
            f"{marker} {candidate.label}: {candidate.series_count}S{candidate.parallel_count}P, "
            f"{candidate.pack_nominal_v:.2f} V nominal, {candidate.pack_capacity_ah:.2f} Ah, "
            f"{candidate.pack_energy_wh:.1f} Wh, {candidate.required_pack_current_a:.1f} A required, "
            f"{candidate.max_continuous_current_a:.1f} A available, limiting factor: {candidate.limiting_factor}"
        )
        lines.append(
            f"  Energy min {candidate.minimum_parallel_by_energy}P, current min {candidate.minimum_parallel_by_current}P, "
            f"suggested BMS >= {candidate.suggested_bms_continuous_a:.0f} A continuous"
        )
        if candidate.required_peak_current_a is not None:
            peak_text = f"{candidate.required_peak_current_a:.1f} A peak required"
            if candidate.minimum_parallel_by_peak is not None:
                peak_text += f", peak min {candidate.minimum_parallel_by_peak}P"
            if candidate.suggested_bms_peak_a is not None:
                peak_text += f", suggested BMS peak >= {candidate.suggested_bms_peak_a:.0f} A"
            lines.append(f"  {peak_text}")
        for note in candidate.notes:
            lines.append(f"  Note: {note}")

    lines.append("")
    lines.append("Recommended")
    lines.append(
        f"- {recommended.label}: {recommended.series_count}S{recommended.parallel_count}P "
        f"at {recommended.pack_nominal_v:.2f} V nominal"
    )
    lines.append(f"- Design energy target: {recommended.design_energy_wh:.1f} Wh")
    lines.append(f"- Required continuous pack current: {recommended.required_pack_current_a:.1f} A")
    lines.append(f"- Suggested BMS continuous rating: >= {recommended.suggested_bms_continuous_a:.0f} A")
    if recommended.suggested_bms_peak_a is not None:
        lines.append(f"- Suggested BMS peak rating: >= {recommended.suggested_bms_peak_a:.0f} A")
    lines.append("- Validate charger profile, thermal monitoring, fuse strategy, and enclosure before build.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    try:
        validate_args(args)
        cell_nominal_v = resolve_cell_nominal_v(args)
        max_dod = resolve_max_dod(args)
        efficiency = resolve_efficiency(args)
        runtime_h = resolve_runtime_hours(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    candidates: list[Candidate] = []
    if args.compare_common_buses or (args.bus_class is None and args.target_bus_v is None):
        for bus_class in (12, 24, 48):
            candidates.append(
                build_candidate(
                    args=args,
                    bus_class=bus_class,
                    target_bus_v=None,
                    cell_nominal_v=cell_nominal_v,
                    max_dod=max_dod,
                    efficiency=efficiency,
                    runtime_h=runtime_h,
                )
            )
    else:
        candidates.append(
            build_candidate(
                args=args,
                bus_class=args.bus_class,
                target_bus_v=args.target_bus_v,
                cell_nominal_v=cell_nominal_v,
                max_dod=max_dod,
                efficiency=efficiency,
                runtime_h=runtime_h,
            )
        )

    recommended = choose_recommended_candidate(args, candidates)

    if args.json:
        payload = {
            "inputs": {
                "use_case": args.use_case,
                "load_w": args.load_w,
                "surge_w": args.surge_w,
                "runtime_h": runtime_h,
                "chemistry": args.chemistry,
                "cell_nominal_v": cell_nominal_v,
                "cell_capacity_ah": args.cell_capacity_ah,
                "cell_continuous_a": args.cell_continuous_a,
                "cell_peak_a": args.cell_peak_a,
                "efficiency": efficiency,
                "max_dod": max_dod,
                "reserve_factor": args.reserve_factor,
            },
            "recommended": asdict(recommended),
            "candidates": [asdict(candidate) for candidate in candidates],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(
            render_text(
                args=args,
                cell_nominal_v=cell_nominal_v,
                max_dod=max_dod,
                efficiency=efficiency,
                runtime_h=runtime_h,
                candidates=candidates,
                recommended=recommended,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
