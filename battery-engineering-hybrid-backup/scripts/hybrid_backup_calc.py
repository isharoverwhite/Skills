#!/usr/bin/env python3
"""
Hybrid backup sizing helper for UPS + inverter + solar buffer systems.
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
        "summary": "Best default for hybrid backup because cycle life, thermal behavior, and partial-state cycling are easier to manage.",
    },
    "li-ion": {
        "cell_nominal_v": 3.7,
        "max_dod": 0.8,
        "summary": "Common 3.7 V lithium-ion cylindrical or pouch cells, suitable when the exact subtype is not specified but voltage and thermal control still need tighter review than LFP.",
    },
    "nmc": {
        "cell_nominal_v": 3.6,
        "max_dod": 0.8,
        "summary": "Higher energy density, but usually needs tighter thermal and protection review than LFP.",
    },
    "lto": {
        "cell_nominal_v": 2.3,
        "max_dod": 0.9,
        "summary": "Good for extreme cycle life, cold conditions, and fast charging, but typically expensive and bulky.",
    },
    "lead-acid": {
        "cell_nominal_v": 2.0,
        "max_dod": 0.5,
        "summary": "Legacy option with lower usable capacity and weaker cycling performance for solar buffer use.",
    },
}

COMMON_SERIES = {
    "lfp": {12: 4, 24: 8, 48: 16},
    "li-ion": {12: 3, 24: 7, 48: 13},
    "nmc": {12: 3, 24: 7, 48: 13},
    "lto": {12: 6, 24: 12, 48: 24},
    "lead-acid": {12: 6, 24: 12, 48: 24},
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
    design_mode: str
    ac_load_energy_wh: float
    battery_energy_no_solar_wh: float
    battery_target_no_solar_wh: float
    solar_generation_during_outage_wh: float
    battery_energy_with_solar_wh: float
    battery_target_with_solar_wh: float
    minimum_buffer_target_wh: float
    selected_battery_target_wh: float
    effective_solar_to_load_w: float | None
    load_gap_during_sun_w: float | None
    daily_pv_harvest_wh: float | None
    minimum_array_w_for_daily_recovery: float | None
    estimated_refill_days: float | None
    required_discharge_current_a: float
    required_peak_current_a: float | None
    required_charge_current_a: float | None
    max_discharge_current_a: float
    max_charge_current_a: float | None
    minimum_parallel_by_energy: int
    minimum_parallel_by_discharge: int
    minimum_parallel_by_peak: int | None
    minimum_parallel_by_charge: int | None
    limiting_factor: str
    suggested_bms_discharge_a: float
    suggested_bms_peak_a: float | None
    suggested_bms_charge_a: float | None
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
    return CHEMISTRY_PRESETS[args.chemistry]["cell_nominal_v"]


def resolve_max_dod(args: argparse.Namespace) -> float:
    if args.max_dod is not None:
        return args.max_dod
    return CHEMISTRY_PRESETS[args.chemistry]["max_dod"]


def select_series_count(
    bus_class: int | None,
    target_bus_v: float | None,
    chemistry: str,
    cell_nominal_v: float,
) -> int:
    if bus_class is not None:
        if bus_class in COMMON_SERIES[chemistry]:
            return COMMON_SERIES[chemistry][bus_class]
        return ceil_units(bus_class / cell_nominal_v)

    if target_bus_v is not None:
        common_target = int(round(target_bus_v))
        if common_target in COMMON_SERIES[chemistry] and abs(target_bus_v - common_target) <= 1.0:
            return COMMON_SERIES[chemistry][common_target]
        return ceil_units(target_bus_v / cell_nominal_v)

    raise ValueError("provide a bus target")


def determine_limiting_factor(sources: dict[str, int | None]) -> str:
    filtered = {name: value for name, value in sources.items() if value is not None}
    maximum = max(filtered.values())
    winners = [name for name, value in filtered.items() if value == maximum]
    return "+".join(winners)


def build_notes(
    args: argparse.Namespace,
    candidate: Candidate,
) -> list[str]:
    notes: list[str] = []

    if args.design_mode == "buffer":
        notes.append("Buffer mode depends on real daylight overlap and is not a worst-case no-sun resilience guarantee.")
    if args.design_mode == "backup" and args.solar_array_w is not None and args.solar_assist_h is None:
        notes.append("Solar is used for refill only because no daylight-overlap assumption was provided for the outage.")
    if candidate.minimum_parallel_by_discharge > candidate.minimum_parallel_by_energy:
        notes.append("Discharge current, not energy, is driving the pack size.")
    if args.design_mode == "buffer" and candidate.minimum_buffer_target_wh >= candidate.selected_battery_target_wh - 1e-6:
        notes.append("The selected target is being held up by the minimum battery buffer floor, not by outage-energy math alone.")
    if candidate.minimum_parallel_by_charge is not None and candidate.minimum_parallel_by_charge > max(
        candidate.minimum_parallel_by_energy,
        candidate.minimum_parallel_by_discharge,
        candidate.minimum_parallel_by_peak or 1,
    ):
        notes.append("Charge current from the PV side is driving the parallel count.")
    if candidate.minimum_parallel_by_peak is not None and candidate.minimum_parallel_by_peak > max(
        candidate.minimum_parallel_by_energy,
        candidate.minimum_parallel_by_discharge,
    ):
        notes.append("Startup or surge current is the main sizing driver.")
    if candidate.required_charge_current_a is not None and args.cell_charge_a is None:
        notes.append("Charge-current validation is incomplete because no per-cell or per-module charge rating was provided.")
    if candidate.pack_energy_wh > candidate.selected_battery_target_wh * 1.8:
        notes.append("The selected cell or module size makes the resulting pack much larger than the target battery energy.")
    if candidate.bus_class_v == 24 and args.load_w > 1000:
        notes.append("24 V is possible on paper here, but 48 V usually simplifies current, fusing, and cable management.")
    if candidate.required_discharge_current_a > 60 and candidate.pack_nominal_v < 40:
        notes.append("DC discharge current is high for this voltage class; compare 48 V before finalizing hardware.")
    if candidate.effective_solar_to_load_w is not None:
        if candidate.effective_solar_to_load_w >= args.load_w:
            notes.append("The PV side can cover the critical load during good sun and may leave surplus for charging.")
        elif candidate.effective_solar_to_load_w >= args.load_w * 0.6:
            notes.append("The PV side can carry a large fraction of the load, but the battery still does meaningful work during sun.")
        else:
            notes.append("The PV side acts mainly as a buffer and cannot sustain the critical load by itself.")
    if candidate.daily_pv_harvest_wh is not None and candidate.daily_pv_harvest_wh < candidate.battery_target_no_solar_wh:
        notes.append("One good solar day is not enough to fully restore a full no-sun discharge.")
    if args.chemistry == "lead-acid":
        notes.append("Lead-acid is usually a weak fit for frequent solar-buffer cycling because usable depth of discharge is limited.")
    if args.chemistry in {"nmc", "li-ion"}:
        notes.append("Common 3.7 V lithium-ion and NMC cells require tighter thermal and charge-limit review than LFP for unattended backup systems.")

    return notes


def build_candidate(
    args: argparse.Namespace,
    bus_class: int | None,
    target_bus_v: float | None,
    cell_nominal_v: float,
    max_dod: float,
) -> Candidate:
    series_count = select_series_count(bus_class, target_bus_v, args.chemistry, cell_nominal_v)
    pack_nominal_v = series_count * cell_nominal_v

    runtime_h = args.runtime_h
    ac_load_energy_wh = args.load_w * runtime_h
    battery_energy_no_solar_wh = ac_load_energy_wh / args.inverter_efficiency
    battery_target_no_solar_wh = battery_energy_no_solar_wh * args.reserve_factor / max_dod

    solar_generation_during_outage_wh = 0.0
    effective_solar_to_load_w = None
    load_gap_during_sun_w = None
    if args.solar_array_w is not None and args.solar_assist_h is not None:
        solar_assist_h = min(args.solar_assist_h, runtime_h)
        solar_dc_power_w = args.solar_array_w * args.pv_derate * args.controller_efficiency
        solar_generation_during_outage_wh = solar_dc_power_w * solar_assist_h
        effective_solar_to_load_w = solar_dc_power_w * args.inverter_efficiency
        load_gap_during_sun_w = max(0.0, args.load_w - effective_solar_to_load_w)

    battery_energy_with_solar_wh = max(0.0, battery_energy_no_solar_wh - solar_generation_during_outage_wh)
    battery_target_with_solar_wh = battery_energy_with_solar_wh * args.reserve_factor / max_dod
    minimum_buffer_energy_wh = (args.load_w * (args.minimum_buffer_min / 60.0)) / args.inverter_efficiency
    minimum_buffer_target_wh = minimum_buffer_energy_wh * args.reserve_factor / max_dod

    if args.design_mode == "backup":
        selected_battery_target_wh = battery_target_no_solar_wh
    else:
        selected_battery_target_wh = max(battery_target_with_solar_wh, minimum_buffer_target_wh)

    required_discharge_power_w = args.load_w / args.inverter_efficiency
    required_discharge_current_a = required_discharge_power_w / pack_nominal_v

    required_peak_current_a = None
    if args.surge_w is not None:
        required_peak_current_a = (args.surge_w / args.inverter_efficiency) / pack_nominal_v

    required_charge_current_a = None
    if args.solar_array_w is not None:
        solar_dc_power_w = args.solar_array_w * args.pv_derate * args.controller_efficiency
        required_charge_current_a = solar_dc_power_w / pack_nominal_v

    energy_per_parallel_wh = pack_nominal_v * args.cell_capacity_ah
    minimum_parallel_by_energy = ceil_units(selected_battery_target_wh / energy_per_parallel_wh)
    minimum_parallel_by_discharge = ceil_units(required_discharge_current_a / args.cell_continuous_a)

    minimum_parallel_by_peak = None
    if required_peak_current_a is not None and args.cell_peak_a is not None:
        minimum_parallel_by_peak = ceil_units(required_peak_current_a / args.cell_peak_a)

    minimum_parallel_by_charge = None
    if required_charge_current_a is not None and args.cell_charge_a is not None:
        minimum_parallel_by_charge = ceil_units(required_charge_current_a / args.cell_charge_a)

    parallel_count = max(
        minimum_parallel_by_energy,
        minimum_parallel_by_discharge,
        minimum_parallel_by_peak or 1,
        minimum_parallel_by_charge or 1,
    )

    pack_capacity_ah = parallel_count * args.cell_capacity_ah
    pack_energy_wh = pack_nominal_v * pack_capacity_ah
    max_discharge_current_a = parallel_count * args.cell_continuous_a
    max_charge_current_a = None if args.cell_charge_a is None else parallel_count * args.cell_charge_a

    daily_pv_harvest_wh = None
    minimum_array_w_for_daily_recovery = None
    estimated_refill_days = None
    if args.solar_array_w is not None and args.sun_hours is not None:
        daily_pv_harvest_wh = (
            args.solar_array_w
            * args.sun_hours
            * args.pv_derate
            * args.controller_efficiency
            * args.charge_path_efficiency
        )
        minimum_array_w_for_daily_recovery = selected_battery_target_wh / (
            args.sun_hours
            * args.pv_derate
            * args.controller_efficiency
            * args.charge_path_efficiency
        )
        estimated_refill_days = selected_battery_target_wh / daily_pv_harvest_wh

    limiting_factor = determine_limiting_factor(
        {
            "energy": minimum_parallel_by_energy,
            "discharge": minimum_parallel_by_discharge,
            "peak": minimum_parallel_by_peak,
            "charge": minimum_parallel_by_charge,
        }
    )

    candidate = Candidate(
        label=f"{bus_class} V class" if bus_class is not None else f"{pack_nominal_v:.1f} V target",
        bus_class_v=bus_class,
        series_count=series_count,
        parallel_count=parallel_count,
        pack_nominal_v=pack_nominal_v,
        pack_capacity_ah=pack_capacity_ah,
        pack_energy_wh=pack_energy_wh,
        design_mode=args.design_mode,
        ac_load_energy_wh=ac_load_energy_wh,
        battery_energy_no_solar_wh=battery_energy_no_solar_wh,
        battery_target_no_solar_wh=battery_target_no_solar_wh,
        solar_generation_during_outage_wh=solar_generation_during_outage_wh,
        battery_energy_with_solar_wh=battery_energy_with_solar_wh,
        battery_target_with_solar_wh=battery_target_with_solar_wh,
        minimum_buffer_target_wh=minimum_buffer_target_wh,
        selected_battery_target_wh=selected_battery_target_wh,
        effective_solar_to_load_w=effective_solar_to_load_w,
        load_gap_during_sun_w=load_gap_during_sun_w,
        daily_pv_harvest_wh=daily_pv_harvest_wh,
        minimum_array_w_for_daily_recovery=minimum_array_w_for_daily_recovery,
        estimated_refill_days=estimated_refill_days,
        required_discharge_current_a=required_discharge_current_a,
        required_peak_current_a=required_peak_current_a,
        required_charge_current_a=required_charge_current_a,
        max_discharge_current_a=max_discharge_current_a,
        max_charge_current_a=max_charge_current_a,
        minimum_parallel_by_energy=minimum_parallel_by_energy,
        minimum_parallel_by_discharge=minimum_parallel_by_discharge,
        minimum_parallel_by_peak=minimum_parallel_by_peak,
        minimum_parallel_by_charge=minimum_parallel_by_charge,
        limiting_factor=limiting_factor,
        suggested_bms_discharge_a=round_up(required_discharge_current_a * 1.25),
        suggested_bms_peak_a=None if required_peak_current_a is None else round_up(required_peak_current_a * 1.15),
        suggested_bms_charge_a=None if required_charge_current_a is None else round_up(required_charge_current_a * 1.25),
        notes=[],
    )
    candidate.notes = build_notes(args, candidate)
    return candidate


def choose_recommended_candidate(args: argparse.Namespace, candidates: list[Candidate]) -> Candidate:
    prefer_24 = args.load_w <= 800 and (args.solar_array_w or 0) <= 1200
    preferred_buses = [24, 48, 12] if prefer_24 else [48, 24, 12]

    current_limit = 45.0 if prefer_24 else 60.0
    eligible = [candidate for candidate in candidates if candidate.required_discharge_current_a <= current_limit]
    pool = eligible if eligible else candidates

    for bus_class in preferred_buses:
        for candidate in pool:
            if candidate.bus_class_v == bus_class:
                return candidate

    return min(pool, key=lambda candidate: candidate.required_discharge_current_a)


def validate_args(args: argparse.Namespace) -> None:
    for name in ("inverter_efficiency", "controller_efficiency", "charge_path_efficiency", "pv_derate"):
        value = getattr(args, name)
        if not (0 < value <= 1):
            raise ValueError(f"--{name.replace('_', '-')} must be between 0 and 1")
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
    if args.design_mode == "buffer" and args.solar_array_w is None:
        raise ValueError("--design-mode buffer requires --solar-array-w")
    if args.design_mode == "buffer" and args.solar_assist_h is None:
        raise ValueError("--design-mode buffer requires --solar-assist-h")
    if args.minimum_buffer_min <= 0:
        raise ValueError("--minimum-buffer-min must be greater than zero")
    if args.solar_assist_h is not None and args.solar_array_w is None:
        raise ValueError("--solar-assist-h requires --solar-array-w")
    if args.sun_hours is not None and args.solar_array_w is None:
        raise ValueError("--sun-hours requires --solar-array-w")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Size a hybrid battery + inverter + solar-buffer system for critical AC loads.",
    )
    parser.add_argument("--design-mode", choices=["backup", "buffer"], default="backup")
    parser.add_argument("--load-w", required=True, type=positive_number, help="Critical AC load in watts.")
    parser.add_argument("--surge-w", type=positive_number, help="Peak AC load in watts.")
    parser.add_argument("--runtime-h", required=True, type=positive_number, help="Required outage runtime in hours.")
    parser.add_argument("--solar-array-w", type=positive_number, help="PV array STC rating in watts.")
    parser.add_argument("--solar-assist-h", type=positive_number, help="Hours of meaningful PV support during the outage.")
    parser.add_argument("--sun-hours", type=positive_number, help="Effective sun hours per good day for refill estimates.")
    parser.add_argument("--minimum-buffer-min", type=positive_number, default=30.0, help="Minimum battery buffer floor in minutes for transient support and cloud cover.")

    parser.add_argument("--chemistry", choices=sorted(CHEMISTRY_PRESETS.keys()), default="lfp")
    parser.add_argument("--cell-nominal-v", type=positive_number, help="Nominal voltage of one cell or module.")
    parser.add_argument("--cell-capacity-ah", required=True, type=positive_number, help="Capacity per cell or module in Ah.")
    parser.add_argument("--cell-continuous-a", required=True, type=positive_number, help="Continuous discharge current per cell or module in A.")
    parser.add_argument("--cell-peak-a", type=positive_number, help="Peak discharge current per cell or module in A.")
    parser.add_argument("--cell-charge-a", type=positive_number, help="Continuous charge current per cell or module in A.")

    parser.add_argument("--bus-class", choices=[12, 24, 48], type=positive_int, help="Evaluate one common bus class.")
    parser.add_argument("--target-bus-v", type=positive_number, help="Evaluate one custom nominal bus target.")
    parser.add_argument("--compare-common-buses", action="store_true", help="Compare 12 V, 24 V, and 48 V classes.")

    parser.add_argument("--inverter-efficiency", type=positive_number, default=0.9)
    parser.add_argument("--controller-efficiency", type=positive_number, default=0.97)
    parser.add_argument("--charge-path-efficiency", type=positive_number, default=0.95)
    parser.add_argument("--pv-derate", type=positive_number, default=0.75)
    parser.add_argument("--max-dod", type=positive_number, help="Usable depth of discharge as a fraction.")
    parser.add_argument("--reserve-factor", type=positive_number, default=1.15)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args()


def render_text(
    args: argparse.Namespace,
    cell_nominal_v: float,
    max_dod: float,
    candidates: list[Candidate],
    recommended: Candidate,
) -> str:
    lines: list[str] = []
    lines.append("Hybrid Backup Sizing Summary")
    lines.append(f"- Design mode: {args.design_mode}")
    lines.append(f"- Critical load: {args.load_w:.0f} W")
    if args.surge_w is not None:
        lines.append(f"- Surge load: {args.surge_w:.0f} W")
    lines.append(f"- Required outage runtime: {args.runtime_h:.2f} h")
    lines.append(f"- Chemistry: {args.chemistry} ({CHEMISTRY_PRESETS[args.chemistry]['summary']})")
    lines.append(f"- Cell nominal voltage: {cell_nominal_v:.2f} V")
    lines.append(f"- Cell capacity: {args.cell_capacity_ah:.2f} Ah")
    lines.append(f"- Cell discharge current: {args.cell_continuous_a:.2f} A")
    if args.cell_charge_a is not None:
        lines.append(f"- Cell charge current: {args.cell_charge_a:.2f} A")
    lines.append(f"- Inverter efficiency: {args.inverter_efficiency:.2f}")
    lines.append(f"- Controller efficiency: {args.controller_efficiency:.2f}")
    lines.append(f"- PV derate: {args.pv_derate:.2f}")
    lines.append(f"- Max DoD: {max_dod:.2f}")
    lines.append(f"- Reserve factor: {args.reserve_factor:.2f}")
    if args.solar_array_w is not None:
        lines.append(f"- PV array: {args.solar_array_w:.0f} W")
    if args.solar_assist_h is not None:
        lines.append(f"- Solar assist during outage: {args.solar_assist_h:.2f} h")
    if args.sun_hours is not None:
        lines.append(f"- Effective sun hours: {args.sun_hours:.2f} h/day")

    lines.append("")
    lines.append("Candidates")
    for candidate in candidates:
        marker = "*" if candidate == recommended else "-"
        lines.append(
            f"{marker} {candidate.label}: {candidate.series_count}S{candidate.parallel_count}P, "
            f"{candidate.pack_nominal_v:.2f} V nominal, {candidate.pack_capacity_ah:.2f} Ah, "
            f"{candidate.pack_energy_wh:.1f} Wh, limiting factor: {candidate.limiting_factor}"
        )
        lines.append(
            f"  Selected battery target {candidate.selected_battery_target_wh:.1f} Wh, "
            f"no-sun target {candidate.battery_target_no_solar_wh:.1f} Wh, "
            f"solar-assisted target {candidate.battery_target_with_solar_wh:.1f} Wh, "
            f"buffer floor {candidate.minimum_buffer_target_wh:.1f} Wh"
        )
        lines.append(
            f"  Discharge {candidate.required_discharge_current_a:.1f} A required, "
            f"{candidate.max_discharge_current_a:.1f} A available, "
            f"BMS discharge >= {candidate.suggested_bms_discharge_a:.0f} A"
        )
        if candidate.required_charge_current_a is not None:
            charge_text = (
                f"  Charge {candidate.required_charge_current_a:.1f} A from PV"
            )
            if candidate.max_charge_current_a is not None:
                charge_text += f", {candidate.max_charge_current_a:.1f} A available"
            if candidate.suggested_bms_charge_a is not None:
                charge_text += f", BMS charge >= {candidate.suggested_bms_charge_a:.0f} A"
            lines.append(charge_text)
        if candidate.effective_solar_to_load_w is not None:
            lines.append(
                f"  Solar-to-load support {candidate.effective_solar_to_load_w:.0f} W, "
                f"daylight load gap {candidate.load_gap_during_sun_w:.0f} W"
            )
        if candidate.daily_pv_harvest_wh is not None:
            lines.append(
                f"  One-good-day PV harvest {candidate.daily_pv_harvest_wh:.0f} Wh, "
                f"minimum array for one-day recovery {candidate.minimum_array_w_for_daily_recovery:.0f} W"
            )
        for note in candidate.notes:
            lines.append(f"  Note: {note}")

    lines.append("")
    lines.append("Recommended")
    lines.append(
        f"- {recommended.label}: {recommended.series_count}S{recommended.parallel_count}P "
        f"at {recommended.pack_nominal_v:.2f} V nominal"
    )
    lines.append(f"- Selected battery target: {recommended.selected_battery_target_wh:.1f} Wh")
    lines.append(f"- No-sun battery target: {recommended.battery_target_no_solar_wh:.1f} Wh")
    lines.append(f"- Solar-assisted battery target: {recommended.battery_target_with_solar_wh:.1f} Wh")
    lines.append(f"- Suggested BMS discharge rating: >= {recommended.suggested_bms_discharge_a:.0f} A")
    if recommended.suggested_bms_peak_a is not None:
        lines.append(f"- Suggested BMS peak rating: >= {recommended.suggested_bms_peak_a:.0f} A")
    if recommended.suggested_bms_charge_a is not None:
        lines.append(f"- Suggested BMS charge rating: >= {recommended.suggested_bms_charge_a:.0f} A")
    lines.append("- Validate MPPT input window, inverter-charger behavior, bypass transfer path, and protection hardware before build.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    try:
        validate_args(args)
        cell_nominal_v = resolve_cell_nominal_v(args)
        max_dod = resolve_max_dod(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    candidates: list[Candidate] = []
    if args.compare_common_buses or (args.bus_class is None and args.target_bus_v is None):
        for bus_class in (12, 24, 48):
            candidates.append(build_candidate(args, bus_class, None, cell_nominal_v, max_dod))
    else:
        candidates.append(build_candidate(args, args.bus_class, args.target_bus_v, cell_nominal_v, max_dod))

    recommended = choose_recommended_candidate(args, candidates)

    if args.json:
        payload = {
            "inputs": {
                "design_mode": args.design_mode,
                "load_w": args.load_w,
                "surge_w": args.surge_w,
                "runtime_h": args.runtime_h,
                "solar_array_w": args.solar_array_w,
                "solar_assist_h": args.solar_assist_h,
                "sun_hours": args.sun_hours,
                "minimum_buffer_min": args.minimum_buffer_min,
                "chemistry": args.chemistry,
                "cell_nominal_v": cell_nominal_v,
                "cell_capacity_ah": args.cell_capacity_ah,
                "cell_continuous_a": args.cell_continuous_a,
                "cell_peak_a": args.cell_peak_a,
                "cell_charge_a": args.cell_charge_a,
                "inverter_efficiency": args.inverter_efficiency,
                "controller_efficiency": args.controller_efficiency,
                "charge_path_efficiency": args.charge_path_efficiency,
                "pv_derate": args.pv_derate,
                "max_dod": max_dod,
                "reserve_factor": args.reserve_factor,
            },
            "recommended": asdict(recommended),
            "candidates": [asdict(candidate) for candidate in candidates],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(args, cell_nominal_v, max_dod, candidates, recommended))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
