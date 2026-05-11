# Webapp Canvas Map

Use this reference when the task targets `<PROJECT_ROOT>/webapp`.

## Package Snapshot

- `react-rnd@10.5.3` handles dashboard drag and resize.
- `react-zoom-pan-pinch@3.7.0` handles automation canvas pan and zoom.

## 1. Dashboard Device Layout

Primary file: `<PROJECT_ROOT>/webapp/src/app/page.tsx`

Key facts:

- `CanvasLayout` is a rectangle per device: `{ x, y, w, h }`.
- Defaults and grid:
  - `DEFAULT_CARD_WIDTH = 320`
  - `DEFAULT_CARD_HEIGHT = 350`
  - `CANVAS_GRID_STEP = 20`
- `normalizeCanvasLayouts()` discards legacy widget payloads and snaps imported values.
- `findFirstCanvasSlot()` auto-places cards into the first free rectangle.
- Customize mode wraps each card in controlled `<Rnd>`.
- Current `Rnd` behavior:
  - controlled `size` and `position`
  - `dragGrid` and `resizeGrid`
  - `bounds="parent"`
  - `enableResizing={isCustomizeMode}`
  - overlap rejection after drag or resize
- When overlap is detected, the code bumps `layoutVersion` to force `Rnd` back to the last valid rectangle.

Implication:

- This canvas is rectangle-layout driven.
- If a future redesign adds parent zoom, `Rnd` should receive the active scale.

## 2. Automation Block Editor

Primary file: `<PROJECT_ROOT>/webapp/src/app/automation/[id]/page.tsx`

Key facts:

- `TransformWrapper` and `TransformComponent` own the zoomable surface.
- `panning={{ excluded: ["nodrag"] }}` prevents child drag targets from also panning the viewport.
- `onTransformed` stores `{ scale, positionX, positionY }` and currently updates `canvasScale`.
- `resolveCanvasPoint()` converts viewport client coordinates into canvas coordinates.
- Node dragging is manual:
  - capture the initial client position
  - capture initial `node.config.ui`
  - divide deltas by current scale
  - clamp to the canvas bounds
- Ports use `data-automation-port="true"` to distinguish link creation from general node drag.
- Edges render in an absolute SVG layer below nodes.
- Context menus keep both viewport-local and canvas-space coordinates so new nodes appear where the user clicked.

Implication:

- This canvas is graph-layout driven.
- It should not be rewritten to native HTML5 drag-and-drop.

## 3. Shared Geometry And Persistence

Primary files:

- `<PROJECT_ROOT>/webapp/src/lib/automation-utils.ts`
- `<PROJECT_ROOT>/webapp/src/types/automation.ts`

Key facts:

- `NODE_WIDTH = 260`
- `NODE_HEIGHT = 100`
- `layoutGraphForCanvas()` creates readable fallback positions.
- `getGraphBounds()` supports fit-to-canvas behavior.
- `buildConnectionEdge()` rejects invalid same-node or same-direction connections.
- Persisted graph positions live in `AutomationGraphNode.config.ui`.

Implication:

- Geometry helpers and serialization rules are already centralized.
- UI changes should stay compatible with these types instead of creating a parallel layout format.

## 4. Secondary Zoom Example

Useful file: `<PROJECT_ROOT>/webapp/src/features/diy/components/Step2Pins.tsx`

Why it matters:

- This file uses `TransformWrapper` and `TransformComponent` for zooming a board image.
- It is a good reference for pan and zoom controls without block dragging.
- If the task needs zoom behavior but not draggable nodes, this is the lighter pattern to copy.

## Editing Guide

- For device-card rearrangement, start in `src/app/page.tsx`.
- For automation logic blocks, start in `src/app/automation/[id]/page.tsx` and keep `automation-utils.ts` aligned.
- If adding a third canvas mode, decide whether it is:
  - rectangle-layout driven, or
  - graph-layout driven

Do not hybridize both patterns unless the saved data model truly needs both.
