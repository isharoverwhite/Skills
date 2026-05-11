# Hybrid Formulas

Use this file when the user asks how the hybrid UPS plus inverter plus solar-buffer math is derived.

## 1. AC Load Energy

```text
ac_load_energy_wh = load_w * runtime_h
```

This is the energy the critical AC load consumes during the outage.

## 2. Battery Energy Without Solar

```text
battery_energy_no_solar_wh = ac_load_energy_wh / inverter_efficiency
battery_target_no_solar_wh = battery_energy_no_solar_wh * reserve_factor / max_dod
```

This is the resilience baseline. Use it when the design must survive the outage even if PV contributes nothing.

## 3. Solar Contribution During Outage

```text
solar_dc_power_w = solar_array_w * pv_derate * controller_efficiency
solar_generation_during_outage_wh = solar_dc_power_w * solar_assist_h
effective_solar_to_load_w = solar_dc_power_w * inverter_efficiency
```

- `pv_derate` absorbs real-world losses such as temperature, orientation, irradiance mismatch, and non-ideal operation.
- `controller_efficiency` covers the MPPT or charge-controller conversion path.

## 4. Battery Energy With Solar Assist

```text
battery_energy_with_solar_wh = max(0, battery_energy_no_solar_wh - solar_generation_during_outage_wh)
battery_target_with_solar_wh = battery_energy_with_solar_wh * reserve_factor / max_dod
minimum_buffer_target_wh = ((load_w * minimum_buffer_min / 60) / inverter_efficiency) * reserve_factor / max_dod
selected_battery_target_wh = max(battery_target_with_solar_wh, minimum_buffer_target_wh)
```

This is valid only when the outage is known to overlap with usable solar production.

## 5. Daily Refill Estimate

```text
daily_pv_harvest_wh = solar_array_w * sun_hours * pv_derate * controller_efficiency * charge_path_efficiency
minimum_array_w_for_daily_recovery = selected_battery_target_wh / (sun_hours * pv_derate * controller_efficiency * charge_path_efficiency)
estimated_refill_days = selected_battery_target_wh / daily_pv_harvest_wh
```

Use this to judge whether the system can recover from an outage in one good solar day.

## 6. Current Checks

```text
required_discharge_current_a = (load_w / inverter_efficiency) / pack_nominal_v
required_peak_current_a = (surge_w / inverter_efficiency) / pack_nominal_v
required_charge_current_a = solar_dc_power_w / pack_nominal_v
```

All three can force the topology upward or increase the required parallel count.

## 7. Parallel Count

```text
parallel_by_energy = ceil(selected_battery_target_wh / (pack_nominal_v * cell_capacity_ah))
parallel_by_discharge = ceil(required_discharge_current_a / cell_continuous_a)
parallel_by_peak = ceil(required_peak_current_a / cell_peak_a)
parallel_by_charge = ceil(required_charge_current_a / cell_charge_a)
parallel_count = max(parallel_by_energy, parallel_by_discharge, parallel_by_peak, parallel_by_charge)
```

If `parallel_by_discharge` or `parallel_by_charge` dominates, the design is current-limited rather than runtime-limited.
