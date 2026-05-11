# Topology And Checks

Use this file when the user needs guidance beyond raw battery math.

## Bus Selection

- `48 V`: Default for most hybrid inverter systems, larger PV arrays, or any design where `24 V` would push DC current too high.
- `24 V`: Fine for smaller critical loads and lighter hybrid systems, especially below roughly 800 W to 1 kW.
- `12 V`: Keep only for legacy or automotive-style systems. It is usually the wrong default for UPS plus inverter plus PV buffering.

## Topology Heuristics

### DC-coupled hybrid

- PV charges the battery through an MPPT or inverter-charger.
- The inverter serves the AC critical load from the DC bus.
- This is the simplest mental model for backup plus solar-buffer planning.

### UPS plus external battery plus PV assist

- Treat the UPS path and the battery path separately first.
- Verify that the UPS allows the intended external battery configuration and charge profile.
- Do not assume consumer UPS hardware can safely behave like a configurable inverter-charger.

### Inverter-charger with PV input

- Validate PV input voltage window, battery charge current settings, low-voltage cutoff, and transfer behavior.
- Prefer `48 V LFP` once inverter power, cable length, or future expansion becomes substantial.

## Chemistry Notes

- `LFP`: Best default for hybrid backup and solar buffer cycling.
- `Li-ion (3.7 V common)`: Reasonable for smaller consumer-cell-based systems, but keep charger compatibility, cutoff voltage, and thermal review stricter than with LFP.
- `NMC`: Similar bus math to common 3.7 V lithium-ion, but use the more specific label when the exact chemistry family is known.

## What To Check Before Calling A Design Reasonable

- MPPT voltage window versus real PV string `Vmp` and `Voc`
- Inverter continuous power, surge power, and low-voltage behavior
- Battery charge current versus PV-side charging capability
- Battery discharge current versus inverter peak demand
- Fuse or breaker placement, DC disconnects, and service isolation
- Enclosure cooling and cell temperature monitoring

## Interpretation Guide

- If PV can carry only a small fraction of the load, call it a `solar buffer`, not a solar-backed UPS.
- If one good solar day cannot refill the selected battery target, say that recovery after deep discharge will be slow.
- If the design works only in `buffer` mode but not `backup` mode, state clearly that the system depends on daylight conditions.
