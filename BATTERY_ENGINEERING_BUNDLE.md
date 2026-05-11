# Battery Engineering Bundle

This bundle standardizes four related skills under one naming scheme:

- `battery-engineering-pack-sizing`
- `battery-engineering-hybrid-backup`
- `battery-engineering-cell-layout`
- `battery-engineering-protection`

## Bundle Scope

- Pack sizing and topology selection
- Hybrid UPS, inverter, and solar-buffer sizing
- Cell layout and `SxP` physical arrangement
- BMS, fuse, and wire sizing

## Shared Trigger Pattern

Each skill now uses the same trigger style:

`Battery engineering for ... Use when Claude needs to ...`

This keeps discovery and selection consistent across the bundle.

## Shared Chemistry Support

The bundle supports these chemistry labels consistently:

- `lfp`
- `li-ion` for common 3.7 V lithium-ion cells
- `nmc`
- `lto`
- `lead-acid`

## Suggested Use Order

1. Use `battery-engineering-pack-sizing` for energy, voltage class, and `SxP` math.
2. Use `battery-engineering-cell-layout` when cell count and physical arrangement matter.
3. Use `battery-engineering-protection` when the user also needs BMS, fuse, and wire sizing.
4. Use `battery-engineering-hybrid-backup` when the system includes inverter or UPS behavior plus solar buffering.

## Notes

- `li-ion` is meant for generic 3.7 V lithium-ion cells when the exact subtype is unknown.
- `battery-engineering-protection` is the bundle skill that covers explicit BMS calculation.
- Basic power math for the bundle lives in [BATTERY_ENGINEERING_POWER_BASICS.md](BATTERY_ENGINEERING_POWER_BASICS.md).
