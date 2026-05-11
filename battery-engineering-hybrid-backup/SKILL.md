---
name: battery-engineering-hybrid-backup
description: Battery engineering for hybrid UPS, inverter, and solar-buffer systems. Use when Claude needs to size battery banks, estimate no-sun autonomy, model solar-assisted runtime, compare 24V and 48V topologies, choose chemistry including common 3.7V lithium-ion, and sanity-check BMS, MPPT, inverter, and reserve assumptions for hybrid backup designs.
---

# Battery Engineering Hybrid Backup

Part of the Battery Engineering Bundle. Use this skill when the problem is not just "how big should the battery be?" but "how should a hybrid battery, inverter, and PV buffer behave during outages and recovery." Keep the scope to low-voltage system planning and sizing logic, not final wiring instructions or code-compliance approval. When the user also needs protection hardware, hand off to the companion bundle skill `battery-engineering-protection`.

## Safety Boundary

- Treat every result as preliminary engineering, not final electrical design.
- Do not provide procedural instructions for mains tie-in, transfer switching, anti-islanding, PV string wiring, or bypassing protection hardware.
- Escalate when the request involves grid export, building wiring changes, licensed electrical work, life-safety loads, or battery systems above 60 VDC nominal.
- Always call out the need to validate inverter-charger settings, MPPT voltage window, BMS charge and discharge limits, fuse or breaker strategy, and enclosure thermal management.

## Workflow

1. Identify the operating mode.
   - `backup`: size for the full outage with no solar contribution.
   - `buffer`: size for a daylight outage where PV offsets part of the battery draw.
2. Collect the minimum inputs.
   - Critical AC load in watts
   - Surge load in watts if motors or compressors are present
   - Required outage runtime
   - Solar array power in watts if PV is part of the design
   - Solar-assist hours during the outage
   - Effective sun hours per day if refill time matters
   - Battery chemistry, including common 3.7 V lithium-ion where relevant, and cell or module specs
3. Size the battery from the worst relevant scenario.
   - No-sun autonomy is the resilience baseline.
   - Solar-assisted autonomy is only valid when daylight overlap is explicit.
   - In buffer mode, keep a non-zero battery floor for cloud cover, transfer time, and transient support.
   - Continuous current, surge current, and charge current can all force a larger parallel count.
4. Choose the bus class.
   - Default to `48 V` for serious inverter loads or larger PV arrays.
   - Keep `24 V` for smaller hybrid systems where DC current stays reasonable.
   - Avoid making `12 V` the default for hybrid inverter systems.
5. Check the solar side.
   - Estimate how much PV can directly support the load during sun.
   - Estimate how much energy the array can return in one good day.
   - State whether the solar side is a partial buffer, a daytime sustain source, or enough to restore the pack after an outage.
6. Return one short decision report.
   - Recommended chemistry, bus class, and SxP topology
   - No-sun battery target and solar-assisted battery target
   - PV contribution during outage and expected refill ability
   - Key follow-up checks for inverter, MPPT, BMS, and protection

## Calculator

Use the bundled calculator for deterministic sizing:

```bash
python3 scripts/hybrid_backup_calc.py --help
```

Add `--json` if another agent needs machine-readable output.

### Common Examples

Compare common bus classes for an 800 W critical load with 4 hours of outage runtime, 1.2 kW PV, and 3 hours of daytime solar assist:

```bash
python3 scripts/hybrid_backup_calc.py \
  --load-w 800 \
  --surge-w 1400 \
  --runtime-h 4 \
  --solar-array-w 1200 \
  --solar-assist-h 3 \
  --sun-hours 4.5 \
  --chemistry lfp \
  --cell-capacity-ah 100 \
  --cell-continuous-a 100 \
  --cell-charge-a 50 \
  --compare-common-buses
```

Force a conservative 48 V backup design that ignores solar during the outage but still checks recharge:

```bash
python3 scripts/hybrid_backup_calc.py \
  --design-mode backup \
  --bus-class 48 \
  --load-w 1500 \
  --surge-w 2500 \
  --runtime-h 6 \
  --solar-array-w 2000 \
  --sun-hours 5 \
  --chemistry lfp \
  --cell-capacity-ah 100 \
  --cell-continuous-a 100 \
  --cell-charge-a 50
```

Use buffer mode for a daylight-only resilience scenario:

```bash
python3 scripts/hybrid_backup_calc.py \
  --design-mode buffer \
  --load-w 500 \
  --runtime-h 5 \
  --solar-array-w 1000 \
  --solar-assist-h 5 \
  --sun-hours 4 \
  --minimum-buffer-min 45 \
  --chemistry li-ion \
  --cell-capacity-ah 5 \
  --cell-continuous-a 10 \
  --cell-charge-a 5
```

## Interpretation Rules

- If `backup` and `buffer` results are very different, the design depends heavily on having real sunlight during the outage.
- If the PV array cannot sustain at least a large fraction of the critical load, treat it as a buffer, not as a replacement for battery capacity.
- If one good solar day cannot substantially refill the battery target, call out that recovery after a long outage will be slow.
- If the DC current at `24 V` looks uncomfortable, move to `48 V` before adding more parallel strings.

## References

- Read [references/hybrid-formulas.md](references/hybrid-formulas.md) for the calculation order and energy accounting.
- Read [references/topology-and-checks.md](references/topology-and-checks.md) for bus selection, PV role, MPPT checks, and inverter or UPS integration notes.

## Output Format

Use this default structure unless the user asks for something else:

```text
Recommendation
- Design mode:
- Recommended chemistry:
- Recommended bus class and topology:
- Why:

Scenario summary
- Critical load:
- Required outage runtime:
- No-sun battery target:
- Solar-assisted battery target:
- Effective solar-to-load power:
- One-good-day PV harvest:

Checks
- Inverter and UPS limits:
- MPPT and PV window:
- BMS charge and discharge headroom:
- Protection and thermal follow-up:
```
