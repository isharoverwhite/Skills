# Topology Guide

Use this file when the user wants a recommendation, not just raw pack math.

## Quick Selection

- `12 V class`: Keep this for automotive-style loads, small routers, LED loads, or legacy gear that truly needs 12 V. Avoid it for sustained mid-power inverter work because current rises quickly.
- `24 V class`: Best default for mixed-use DC systems, workshop backup power, and many UPS-style loads below about 1 kW continuous.
- `48 V class`: Best default for inverter-heavy systems, longer cable runs, and any design where current at 24 V starts to look awkward.

## Chemistry Heuristics

- `LFP`: Default choice for UPS, backup batteries, and hobby or workshop systems. It trades energy density for cycle life, thermal stability, and simpler operating margins.
- `Li-ion (3.7 V common)`: Use this when the user is dealing with generic consumer-style lithium-ion cells such as many 18650 or 21700 cells and the exact subtype is unknown. In preliminary sizing, treat it close to NMC but keep voltage and thermal limits explicit.
- `NMC`: Use when weight or volume matters enough to justify tighter thermal and protection requirements.
- `LTO`: Use for cold environments, fast charge acceptance, or very high cycle life. It is rarely the lowest-cost answer.
- `Lead-acid`: Use only when legacy compatibility or budget dominates and the user accepts lower usable capacity and shorter cycle life.

## Use-Case Mapping

### UPS or inverter backup

- Include inverter efficiency in every runtime estimate.
- Compare 24 V and 48 V once the continuous load is more than a few hundred watts.
- Prefer LFP unless the user has a hard space or weight constraint.

### Native DC backup

- Start from the load rail and determine whether the battery should match that rail or feed a regulator above it.
- Include converter efficiency, minimum input voltage, and hold-up margin.
- Keep the storage bus separate from the regulated output in the final explanation.

### Multi-purpose portable power

- Start with 24 V LFP if the system needs to support DC loads plus a modest inverter.
- Move to 48 V LFP when the inverter becomes the dominant load or future expansion matters.
- Treat 12 V output as a downstream converter rail instead of forcing the whole pack to stay at 12 V.

### Bench supply or workshop source

- Separate the energy-storage bus from the final regulated output rail.
- Oversize the downstream DC-DC stage for transient load steps.
- If the user says "one battery for everything," bias toward 24 V or 48 V plus converters, not a giant 12 V pack.

## Safety Gates

- Require BMS current headroom, fuse or breaker planning, charger compatibility, and thermal monitoring before calling any design "ready."
- Escalate when the design crosses 60 VDC nominal, interfaces with mains wiring, or is intended for life-safety or always-on unattended operation.
- Call out unknowns explicitly when the user does not provide real cell ratings, surge requirements, or temperature limits.
