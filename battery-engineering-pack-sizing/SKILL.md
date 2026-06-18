---
name: battery-engineering-pack-sizing
description: Battery engineering for pack sizing and topology selection. Use when Claude needs to calculate Wh and Ah, compare 12V, 24V, 48V, or custom buses, choose chemistry including common 3.7V lithium-ion, recommend SxP topology, and sanity-check runtime, current, reserve, and preliminary BMS assumptions for low-voltage battery systems.
---

# Battery Engineering Pack Sizing

Part of the Battery Engineering Bundle. Use this skill to turn a vague backup-power request into a preliminary battery-pack recommendation. Keep the scope to low-voltage planning math and architecture tradeoffs, not final electrical approval or hazardous assembly instructions. When the user also needs BMS, fuse, or wire sizing, follow with the companion bundle skill `battery-engineering-protection`.

## Safety Boundary

- Treat every result as preliminary engineering only.
- Do not provide build steps that bypass BMS, charger protections, fusing, thermal monitoring, or cell-matching requirements.
- Escalate when the request involves mains wiring, grid interconnect, certified life-safety loads, medical loads, or packs above 60 VDC nominal.
- State clearly when a licensed electrician, battery engineer, or product compliance review is required.

## Workflow

1. Define the load side first.
   - AC via inverter or UPS
   - Native DC rail
   - Mixed-use system
2. Collect the minimum inputs.
   - Continuous load in watts
   - Surge load in watts if motors or compressors are involved
   - Required runtime
   - Preferred bus class: 12V, 24V, 48V, or a custom target
   - Cell or module nominal voltage, capacity in Ah, and continuous current rating
   - Chemistry preference, efficiency, max depth of discharge, reserve margin
3. Choose the chemistry before the exact topology.
   - Default to LFP for UPS, backup power, and workshop systems.
   - Use `li-ion` for common 3.7 V lithium-ion cylindrical or pouch cells when the exact subtype is not specified.
   - Consider NMC only when weight or volume matters more than cycle life and thermal simplicity.
   - Use LTO only for extreme cycle life, fast charging, or cold conditions.
   - Treat lead-acid as a legacy or cost-driven option with shallower usable depth of discharge.
4. Choose the bus class.
   - Keep 12V for small legacy loads and low-power automotive-style systems.
   - Start with 24V for mixed-use DC systems and sub-1 kW backup systems.
   - Move to 48V when inverter power or cable current becomes high.
   - Read [references/topologies.md](references/topologies.md) when the user needs a bus-level tradeoff analysis.
5. Size the pack from both energy and current.
   - Energy determines minimum parallel count for runtime.
   - Continuous and surge current determine minimum parallel count for power delivery.
   - Use the larger result; do not size from Wh alone.
6. Sanity-check the recommendation.
   - Verify BMS current headroom, fuse or breaker planning, thermal monitoring, charger compatibility, enclosure constraints, and serviceability.
   - Call out when the design becomes current-limited or when the pack is heavily oversized on energy because the bus voltage is too low.
7. Return a short decision report.
   - Recommended chemistry
   - Recommended bus class and SxP topology
   - Required pack energy and expected usable energy
   - Current draw at nominal voltage
   - Key safety or validation follow-ups

## Calculator

Use the bundled calculator for deterministic sizing:

```bash
python3 scripts/battery_pack_calc.py --help
```

Add `--json` if another tool or agent needs machine-readable output.

### Common Examples

Compare common bus classes for a 600 W UPS with 45 minutes of runtime using LFP cells:

```bash
python3 scripts/battery_pack_calc.py \
  --use-case ups \
  --load-w 600 \
  --surge-w 900 \
  --runtime-min 45 \
  --chemistry lfp \
  --cell-capacity-ah 5 \
  --cell-continuous-a 10 \
  --cell-peak-a 15 \
  --compare-common-buses
```

Size a fixed 48 V class LFP pack for an inverter-heavy setup:

```bash
python3 scripts/battery_pack_calc.py \
  --use-case inverter \
  --load-w 1500 \
  --surge-w 2500 \
  --runtime-min 30 \
  --chemistry lfp \
  --bus-class 48 \
  --cell-capacity-ah 100 \
  --cell-continuous-a 100
```

Size a custom bus voltage with explicit cell voltage:

```bash
python3 scripts/battery_pack_calc.py \
  --use-case dc-backup \
  --load-w 180 \
  --runtime-h 3 \
  --target-bus-v 12 \
  --chemistry li-ion \
  --cell-capacity-ah 3 \
  --cell-continuous-a 10
```

### Interpretation Rules

- If current, not runtime, drives the parallel count, prefer a higher bus class before blindly adding more parallel strings.
- If the pack energy is much larger than the design energy, the system is likely bus-voltage-limited rather than runtime-limited.
- For UPS or inverter requests above roughly 1 kW continuous, compare 48 V even if 24 V still works on paper.
- For legacy 12 V loads, keep the battery bus and the regulated output stage separate in the analysis.

## References

- Read [references/formulas.md](references/formulas.md) when you need the exact sizing equations and assumption order.
- Read [references/topologies.md](references/topologies.md) when you need use-case guidance for UPS, DC backup, portable power, or bench supplies.

## Output Format

Use this default structure unless the user asks for something else:

```text
Recommendation
- Use case:
- Recommended chemistry:
- Recommended topology:
- Why this topology:

Sizing summary
- Continuous load:
- Surge load:
- Required runtime:
- Design energy:
- Pack nominal voltage:
- Required pack current:
- Minimum parallel count by energy:
- Minimum parallel count by current:

Open checks
- BMS / fuse headroom:
- Charger profile:
- Thermal and enclosure constraints:
- Validation still required:
```

## 👨‍💻 Mandatory Code Editing Protocol

1. **Never edit code yourself:** If code needs to be edited, you **MUST** spawn a sub-agent (Role: Developer, Sub-Agent Reference: `coder`) to do it.
2. **Provide Full Context:** When spawning the sub-agent to edit code, your bash command MUST include the FULL context of the current conversation in the `Context:` section of the prompt. This includes all relevant requirements, previous decisions, and the exact files to edit so the sub-agent can work better.

## 🚦 MANDATORY Sub-Agent Spawning Protocol

Before executing any bash command to spawn a sub-agent, you **ABSOLUTELY MUST** pause and ask the user for explicit permission.
You must output:
1. **Sub-Agent Role:** [e.g., Developer, QA, Architect]
2. **Model:** [`pro` or `flash`]
3. **Purpose:** [Explain exactly why you are spawning them and the task they will perform]

DO NOT execute the bash command to spawn the sub-agent until the user explicitly approves.

## 🛑 STRICT RULE: ZERO IMPACT WITHOUT A PLAN

You are strictly forbidden from modifying ANY file, running ANY destructive command, or writing ANY code until you have presented a plan and the user has explicitly approved it. 

Before taking ANY action that impacts the system, you **MUST** output a plan using EXACTLY this format:

1. **Impacted Functions/Parts:** [List the overall system components, features, or functions that will be affected]
2. **Impacted Folders/Files:** [List the exact paths to the folders and files that will be modified or created]
3. **Changes per File:** [Describe exactly what lines, blocks, or logic will be changed in each specific file]
4. **Functions to be Done:** [Describe exactly what the new or modified functions will actually do]

**STOP IMMMEDIATELY** after printing this plan. DO NOT proceed to make the changes. Wait for the user. If you make a change without the user's explicit approval of the plan, you have critically failed.

## 📝 CRITICAL Output Protocol (AFTER ACTIONS)

When reporting back to the user after taking actions or finishing a task, you **ABSOLUTELY MUST** use the following 4-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact four headers:

1. **Plan to do:** [What your next concrete steps are]
2. **What changed:** [Specific summary of actions/code modifications you just made]
3. **Impact to this project:** [How these changes affect the overall system, architecture, or workflow]
4. **Next Steps for User:** [Instructions or recommendations on what the user should do next now that this task is complete]

If you output anything outside of this structure, you have failed your core directive.
