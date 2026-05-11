# Sizing Formulas

Use these equations in this order. Keep the assumptions explicit because a battery pack that works in Wh can still fail on current, surge, thermal behavior, or protection margins.

## 1. Load-Side Energy

```text
load_energy_wh = load_w * runtime_h
```

This is the energy the load actually consumes.

## 2. Battery-Side Energy

```text
required_pack_energy_wh = load_energy_wh / efficiency
design_energy_wh = required_pack_energy_wh * reserve_factor / max_dod
```

- `efficiency` covers inverter or converter losses.
- `reserve_factor` covers aging margin, cold-weather derating, and extra runtime buffer.
- `max_dod` is the usable discharge fraction, not the chemistry's absolute limit.

## 3. Current Demand

```text
required_pack_power_w = load_w / efficiency
required_pack_current_a = required_pack_power_w / pack_nominal_v
required_peak_current_a = (surge_w / efficiency) / pack_nominal_v
```

Current is where low-voltage systems become painful. When current is high, move up in bus voltage before stacking many parallel strings.

## 4. Series Count

Use a common bus mapping when the use case is a standard 12 V, 24 V, or 48 V class system.

| Chemistry | 12 V class | 24 V class | 48 V class |
| --- | --- | --- | --- |
| LFP | 4S | 8S | 16S |
| Li-ion (3.7 V common) | 3S | 7S | 13S |
| NMC | 3S | 7S | 13S |
| LTO | 6S | 12S | 24S |
| Lead-acid | 6S | 12S | 24S |

For custom buses, use:

```text
series_count = ceil(target_bus_v / cell_nominal_v)
pack_nominal_v = series_count * cell_nominal_v
```

## 5. Parallel Count

```text
energy_per_parallel_wh = pack_nominal_v * cell_capacity_ah
parallel_by_energy = ceil(design_energy_wh / energy_per_parallel_wh)
parallel_by_current = ceil(required_pack_current_a / cell_continuous_a)
parallel_by_peak = ceil(required_peak_current_a / cell_peak_a)
parallel_count = max(parallel_by_energy, parallel_by_current, parallel_by_peak)
```

If peak-current data is not available, say so and keep the surge conclusion conditional.

## 6. Pack Summary

```text
pack_capacity_ah = parallel_count * cell_capacity_ah
pack_energy_wh = pack_nominal_v * pack_capacity_ah
max_continuous_current_a = parallel_count * cell_continuous_a
```

## 7. Interpretation Shortcuts

- `parallel_by_current > parallel_by_energy`: the design is power-limited, not runtime-limited.
- `pack_energy_wh >> design_energy_wh`: the chosen bus voltage is likely too low for the power level.
- `required_pack_current_a > 50 A`: compare the next higher bus class before finalizing.
- `required_pack_current_a > 100 A`: treat conductor, fuse, switchgear, and thermal planning as major design drivers, not cleanup work.
