---
name: battery-engineering-protection
description: Battery engineering for BMS, fuse, and wire sizing. Use when Claude needs to recommend BMS series compatibility, charge and discharge current ratings, support common 3.7V lithium-ion or other chemistries, and select conservative DC fuse and wire sizes from current, cable length, voltage-drop, and protection constraints.
---

# Battery Engineering Protection

Part of the Battery Engineering Bundle. Use this skill when the battery-pack question has moved beyond `SxP` math and into protection hardware. The goal is to turn pack voltage, chemistry, charge and discharge current, and cable length into a preliminary recommendation for BMS spec, DC fuse rating, and conductor cross-section. This is the bundle skill that covers BMS calculation explicitly.

## Safety Boundary

- Treat every result as preliminary engineering guidance only.
- Do not provide final approval for life-safety loads, mains wiring, grid interconnect, or code-compliant installation.
- Do not present wire ampacity or fuse ratings as universal truths. Final selection must still match insulation temperature rating, bundling, environment, local code, and manufacturer limits.
- Always call out that fuse interrupt rating, DC voltage rating, terminal temperature, and fault-current behavior still require verification.

## Workflow

1. Resolve the pack side first.
   - Exact `S` count
   - Or common bus class such as `12 V`, `24 V`, or `48 V`
   - Chemistry for nominal cell voltage and charging safeguards
2. Resolve real battery-side current.
   - Use direct charge and discharge current when available.
   - Otherwise derive battery current from power and pack voltage.
   - Include surge current if inverter or motor loads are involved.
3. Size the BMS.
   - Match chemistry and series count.
   - Add headroom to continuous charge and discharge current.
   - Add peak current headroom if surge is relevant.
   - Call out balancing, temperature sensing, low-temperature charge cutoff, and communication requirements.
4. Size wire by both thermal heuristic and voltage drop.
   - Voltage drop sets a minimum cross-section for a given current and cable length.
   - Current density heuristic sets a minimum cross-section for thermal sanity.
   - Use the larger result.
5. Size the fuse after the wire.
   - The fuse must be above expected operating current but still low enough to protect the conductor.
   - Prefer DC-rated protection close to the battery positive terminal.
6. Return a short decision report.
   - Recommended BMS spec
   - Recommended discharge-path wire and fuse
   - Recommended charge-path wire and fuse if relevant
   - Open checks that still need a real engineering review

## Calculator

Use the bundled calculator:

```bash
python3 scripts/protection_sizing_calc.py --help
```

Add `--json` if another agent needs machine-readable output.

### Common Examples

Size BMS, fuse, and battery lead for a `16S` LFP inverter pack with about `1500 W` AC load and `2500 W` surge:

```bash
python3 scripts/protection_sizing_calc.py \
  --series-count 16 \
  --chemistry lfp \
  --load-side ac \
  --load-w 1500 \
  --surge-w 2500 \
  --charge-current-a 40 \
  --discharge-length-m 1.5 \
  --charge-length-m 1.5 \
  --needs-comms
```

Use direct battery-side current for a DC backup pack:

```bash
python3 scripts/protection_sizing_calc.py \
  --bus-class 24 \
  --chemistry lfp \
  --discharge-current-a 60 \
  --charge-current-a 20 \
  --discharge-length-m 2 \
  --charge-length-m 2 \
  --pack-capacity-ah 100
```

Size a small `3S3P` NMC pack with short leads:

```bash
python3 scripts/protection_sizing_calc.py \
  --series-count 3 \
  --parallel-count 3 \
  --chemistry li-ion \
  --cell-capacity-ah 3 \
  --discharge-current-a 15 \
  --charge-current-a 6 \
  --discharge-length-m 0.4 \
  --charge-length-m 0.4
```

## Interpretation Rules

- The BMS current rating should not be chosen equal to the exact working current. Keep headroom.
- The fuse should protect the conductor, not just the load.
- Long low-voltage runs often become voltage-drop-limited before they become thermal-limited.
- LFP packs should explicitly call out low-temperature charge protection.
- Large inverter systems usually benefit from communication-capable BMS and precharge planning.

## References

- Read [references/sizing-formulas.md](references/sizing-formulas.md) for current, wire, and fuse calculations.
- Read [references/selection-checklist.md](references/selection-checklist.md) for BMS feature guidance and protection checks.

## Output Format

Use this default structure unless the user asks for something else:

```text
BMS recommendation
- Pack series support:
- Chemistry:
- Continuous discharge rating:
- Peak discharge rating:
- Continuous charge rating:
- Feature notes:

Protection path sizing
- Discharge current basis:
- Discharge wire recommendation:
- Discharge fuse recommendation:
- Charge wire recommendation:
- Charge fuse recommendation:
- Voltage-drop notes:

Open checks
- Fuse DC rating and interrupt rating:
- Terminal and lug temperature:
- BMS low-temp and balancing behavior:
- Installer or code review still required:
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
