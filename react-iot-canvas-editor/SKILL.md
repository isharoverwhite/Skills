---
name: react-iot-canvas-editor
description: Design and refactor React drag-drop canvas editors built with react-rnd and react-zoom-pan-pinch, especially the IoT dashboard and automation block canvases in <PROJECT_ROOT>/webapp. Use when Claude needs to redesign IoT blocks, add drag or resize behavior, tune snap and bounds rules, or debug pan-versus-drag conflicts on a zoomable canvas.
---

# React IoT Canvas Editor

Use this skill for React editors where blocks are arranged visually on a canvas and must be saved back to app state.

## Workflow

1. Run `bash scripts/scan_canvas_usage.sh [repo]`.
2. Read the files that own the current interaction model before editing:
   - Dashboard card canvas: `src/app/page.tsx`
   - Automation graph canvas: `src/app/automation/[id]/page.tsx`
   - Shared graph geometry: `src/lib/automation-utils.ts`
   - Graph types: `src/types/automation.ts`
3. Choose one interaction model early:
   - Use controlled `Rnd` blocks for rectangular cards that need drag, resize, snap, and bounds.
   - Use manual drag inside a pan/zoom surface for graph nodes that also own ports, edges, or context menus.
   - Do not default to HTML5 Drag and Drop API for editor-style canvases.
4. Preserve the repo's serialization format and coordinate system.
5. Verify drag behavior at multiple zoom levels and after reload.

## Project Default

Default target repo: `<PROJECT_ROOT>/webapp`.

Read [references/webapp-canvas-map.md](references/webapp-canvas-map.md) when the task is for that repo.
Read [references/drag-drop-research.md](references/drag-drop-research.md) when changing drag math, pan/zoom behavior, or interaction architecture.

## Implementation Rules

- Keep one source of truth for layout state.
  - Dashboard canvas persists `Record<string, { x, y, w, h }>` keyed by `device_id`.
  - Automation graph persists `node.config.ui` plus explicit edge objects.
- Normalize drag math by zoom scale.
  - With `react-rnd`, pass `scale={canvasScale}` when the parent is transformed.
  - With manual dragging, divide client-space deltas by current canvas scale.
- Separate canvas pan from node drag.
  - Exclude draggable nodes and ports from parent panning.
  - Stop propagation on handles, ports, and context-menu triggers.
- Use snapping, bounds, and minimum sizes intentionally.
  - Snap on stop if live snapping feels jittery.
  - Clamp to canvas bounds if blocks must remain visible.
- Keep rendering layers separate.
  - Background grid
  - Edges or guides
  - Nodes
  - Floating HUD and context menus
- Do not mix uncontrolled DOM transforms with serialized application coordinates.
- Preserve existing desktop or mobile behavior unless the task explicitly changes it.

## Decision Guide

### Dashboard-style block layout

Use the existing `react-rnd` pattern when:

- blocks are cards
- resize handles are needed
- collision checks happen after drag or resize
- layout is stored as a rectangle per block

### Automation-style graph editor

Use the existing transform plus manual drag pattern when:

- nodes have input or output ports
- edges are drawn in SVG
- right-click menus depend on canvas coordinates
- zoom, pan, and graph geometry must share the same coordinate system

## Verification

Check all of the following after edits:

- Empty canvas still pans and zooms.
- Dragging a node or card does not also pan the canvas.
- Movement distance stays correct at 50%, 100%, and max supported zoom.
- Snap, collision, and min-size rules still hold.
- Saved positions survive refresh.
- Edge endpoints or overlays stay aligned after a move or zoom change.

## Useful Commands

```bash
bash scripts/scan_canvas_usage.sh
bash scripts/scan_canvas_usage.sh /path/to/other/repo
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
