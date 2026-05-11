# S And P Formulas

Use this file when the user needs the exact logic for `S`, `P`, pack Ah, pack Wh, and total cell count.

## Core Meanings

- `S` means cells connected in series.
  Series raises nominal pack voltage.
- `P` means cells connected in parallel.
  Parallel raises pack capacity and current capability.

Examples:

- `3S1P` = 3 cells in series, 1 parallel path
- `3S3P` = 9 total cells
- `13S4P` = 52 total cells

## 1. Series Count

If the user already knows the topology, use it directly:

```text
series_count = user_supplied_S
```

If the user gives a target pack voltage:

```text
series_count = ceil(target_pack_v / cell_nominal_v)
pack_nominal_v = series_count * cell_nominal_v
```

If the user gives a common bus class:

| Chemistry | 12 V class | 24 V class | 48 V class |
| --- | --- | --- | --- |
| LFP | 4S | 8S | 16S |
| Li-ion (3.7 V common) | 3S | 7S | 13S |
| NMC | 3S | 7S | 13S |
| LTO | 6S | 12S | 24S |
| Lead-acid | 6S | 12S | 24S |

## 2. Parallel Count

Parallel count can be driven by one or more requirements:

```text
parallel_by_capacity = ceil(target_capacity_ah / cell_capacity_ah)
parallel_by_energy = ceil(target_energy_wh / (series_count * cell_nominal_v * cell_capacity_ah))
parallel_by_current = ceil(target_discharge_a / cell_continuous_a)
parallel_count = max(parallel_by_capacity, parallel_by_energy, parallel_by_current)
```

If the user gives an exact `P`, use that directly.

## 3. Pack Summary

```text
total_cells = series_count * parallel_count
pack_nominal_v = series_count * cell_nominal_v
pack_capacity_ah = parallel_count * cell_capacity_ah
pack_energy_wh = pack_nominal_v * pack_capacity_ah
max_continuous_current_a = parallel_count * cell_continuous_a
```

## 4. Layout Inputs

The electrical topology alone is not enough for a physical pack estimate. You also need:

- Cell footprint dimensions
- Cell height
- Gap between cells
- Gap between series groups
- Allowed number of layers

## 5. Interpretation Shortcuts

- Increasing `S` changes voltage class.
- Increasing `P` changes Ah and current.
- If `parallel_by_current` is larger than `parallel_by_capacity`, the pack is current-limited rather than energy-limited.
- Real enclosure size must be larger than raw cell-only dimensions.
