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

## 📝 CRITICAL Output Protocol (MANDATORY)

When you report back to the user, you **ABSOLUTELY MUST** use the following 3-point format and NOTHING ELSE. 
**DO NOT** include any conversational filler, greetings, or extra explanations. **ONLY** output these exact three headers:

1. **Plan to do:** [Your next concrete steps]
2. **What changed:** [Specific summary of actions/code modifications made]
3. **Impact to this project:** [How this affects the overall system, architecture, or workflow]

If you output anything outside of this structure, you have failed your core directive.
