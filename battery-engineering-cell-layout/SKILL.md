---
name: battery-engineering-cell-layout
description: Battery engineering for SxP topology and physical cell layout. Use when Claude needs to convert target voltage, capacity, energy, or current into series and parallel arrangements, compare cylindrical formats such as 12700, 18650, 21700, or custom prismatic cells, include common 3.7V lithium-ion cells, and propose compact practical pack layouts.
---

# Battery Engineering Cell Layout

Part of the Battery Engineering Bundle. Use this skill when the user cares about both the electrical topology and the physical packing of the cells. The core question is usually some variation of: "I need this voltage and capacity, what `SxP` pack should I build, how many cells do I need, and how should they be arranged so the pack stays compact?" When the user also needs BMS current, fuse, or wire sizing, follow with the companion bundle skill `battery-engineering-protection`.

## Safety Boundary

- Treat every result as preliminary planning, not a build-ready mechanical or electrical drawing.
- Do not provide assembly steps that bypass insulation, cell matching, compression, fuse links, thermal sensing, spacing, or BMS protections.
- Escalate when the request crosses mains wiring, certified safety systems, or battery systems above 60 VDC nominal.
- State clearly that real pack size must still reserve room for busbars, holders, wiring, BMS, padding, compression frames, airflow, and enclosure tolerance.

## Workflow

1. Resolve the electrical target first.
   - Exact `S` count from the user, such as `3S`
   - Exact `P` count from the user, such as `3P`
   - Or infer `S` and `P` from target pack voltage, target Ah, target Wh, and target current
2. Resolve the cell geometry.
   - Cylindrical presets such as `12700`, `18650`, `21700`, `26650`, `32700`
   - Custom cylindrical dimensions
   - Custom prismatic dimensions
3. Compute the pack topology.
   - `series_count` controls pack nominal voltage
   - `parallel_count` controls pack Ah and current capability
   - `total_cells = S * P`
4. Search practical layouts.
   - Build a parallel cluster for each series group
   - Arrange series groups across one or more layers
   - Score candidates by compactness goal: `balanced`, `compact`, `footprint`, or `flat`
5. Return both electrical and physical conclusions.
   - Recommended `SxP`
   - Total cells
   - Achieved pack voltage, capacity, and energy
   - Estimated envelope dimensions
   - Notes about gaps between ideal math and real enclosure size

## Calculator

Use the bundled calculator:

```bash
python3 scripts/cell_pack_layout_calc.py --help
```

Add `--json` if another agent needs machine-readable output.

### Common Examples

Derive `P` from a `3S` pack that must reach about `9 Ah` using `18650` cells rated at `3 Ah`:

```bash
python3 scripts/cell_pack_layout_calc.py \
  --series-count 3 \
  --target-capacity-ah 9 \
  --cell-format 18650 \
  --chemistry li-ion \
  --cell-capacity-ah 3 \
  --layout-goal balanced
```

Lay out an explicit `13S4P` pack with `18650` cells:

```bash
python3 scripts/cell_pack_layout_calc.py \
  --series-count 13 \
  --parallel-count 4 \
  --cell-format 18650 \
  --chemistry li-ion \
  --cell-capacity-ah 3
```

Infer a `48 V` class LFP pack using `32700` cells:

```bash
python3 scripts/cell_pack_layout_calc.py \
  --bus-class 48 \
  --target-capacity-ah 40 \
  --cell-format 32700 \
  --chemistry lfp \
  --cell-capacity-ah 6 \
  --cell-continuous-a 10 \
  --layout-goal compact
```

Use custom prismatic cells:

```bash
python3 scripts/cell_pack_layout_calc.py \
  --series-count 16 \
  --target-capacity-ah 100 \
  --shape prismatic \
  --cell-width-mm 174 \
  --cell-depth-mm 72 \
  --cell-height-mm 207 \
  --chemistry lfp \
  --cell-capacity-ah 100 \
  --layout-goal footprint
```

## Interpretation Rules

- `S` is voltage-driven. Increasing `S` raises nominal pack voltage.
- `P` is capacity and current-driven. Increasing `P` raises pack Ah, Wh, and current capability.
- For cylindrical cells, the script estimates a rectangular envelope around grouped cells. Real dense honeycomb packing can be somewhat tighter.
- A mathematically minimal footprint is not always the most buildable layout. Use `balanced` when the user wants something compact but still practical.
- Real pack dimensions will exceed cell-only dimensions once protection, holders, insulation, and structure are added.

## References

- Read [references/sp-formulas.md](references/sp-formulas.md) for the `S`, `P`, Ah, Wh, and current equations.
- Read [references/layout-heuristics.md](references/layout-heuristics.md) for form-factor guidance and packing tradeoffs.

## Output Format

Use this default structure unless the user asks for something else:

```text
Electrical topology
- Recommended SxP:
- Total cells:
- Pack nominal voltage:
- Pack capacity:
- Pack nominal energy:
- Why S:
- Why P:

Physical layout
- Cell type and dimensions:
- Recommended layout candidate:
- Estimated envelope:
- Layer count:
- Parallel cluster shape:
- Series-group grid:

Checks
- Current headroom:
- Geometry caveats:
- Space still needed for structure, BMS, and wiring:
```

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
