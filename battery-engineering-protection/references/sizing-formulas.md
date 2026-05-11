# Sizing Formulas

Use this file when the user asks how the BMS, fuse, and wire recommendations are derived.

## 1. Pack Voltage

```text
pack_nominal_v = series_count * cell_nominal_v
```

## 2. Battery-Side Current From Power

For a DC load:

```text
battery_current_a = load_w / pack_nominal_v
```

For an AC load behind an inverter:

```text
battery_current_a = (load_w / inverter_efficiency) / pack_nominal_v
```

Apply the same idea to surge power if the user gives a surge value.

## 3. BMS Current Headroom

```text
bms_continuous_discharge_a = discharge_current_a * discharge_headroom
bms_peak_discharge_a = surge_current_a * peak_headroom
bms_continuous_charge_a = charge_current_a * charge_headroom
```

Typical conservative defaults in this skill:

- continuous headroom: `1.25x`
- peak headroom: `1.15x`

These are heuristics, not compliance rules.

## 4. Wire Area By Voltage Drop

For a round-trip copper path:

```text
required_area_drop_mm2 = (2 * one_way_length_m * current_a * copper_resistivity) / allowed_drop_v
allowed_drop_v = pack_nominal_v * max_drop_pct / 100
```

This skill uses copper resistivity in `ohm * mm2 / m`.

## 5. Wire Area By Thermal Heuristic

```text
required_area_thermal_mm2 = current_a / amps_per_mm2
```

This is intentionally conservative and generic. Final ampacity depends on insulation, bundling, ambient temperature, and installation method.

## 6. Fuse Selection

```text
required_fuse_current = operating_current * fuse_headroom
```

Then choose the smallest standard fuse that is:

- at or above the required protection current
- still below the chosen wire's safe protection ceiling

The fuse should protect the conductor, not merely match the load.
