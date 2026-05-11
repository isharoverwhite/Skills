# Drag And Drop Research

Use this reference when drag behavior, zoom math, or interaction architecture is the risky part of the task.

## Library-Specific Notes

### `react-rnd`

Relevant local docs:

- `<PROJECT_ROOT>/webapp/node_modules/react-rnd/README.md`

Important behaviors:

- Use controlled `position` and `size` for persisted layouts.
- `dragGrid` and `resizeGrid` give deterministic snap increments.
- `bounds` can target `parent`, `window`, `body`, a selector, or an element.
- `scale` must match the active zoom when the parent canvas uses transforms, otherwise drag and resize deltas will be wrong.

### `react-zoom-pan-pinch`

Relevant local docs:

- `<PROJECT_ROOT>/webapp/node_modules/react-zoom-pan-pinch/README.md`
- `<PROJECT_ROOT>/webapp/node_modules/react-zoom-pan-pinch/dist/index.d.ts`

Important behaviors:

- `TransformWrapper` and `TransformComponent` are suitable for large fixed-size editors.
- `panning.excluded` allows child selectors to opt out of viewport dragging.
- `onTransformed` exposes `{ scale, positionX, positionY }` so the editor can keep drag math in sync with zoom.
- `limitToBounds={false}` is useful when the canvas should behave larger than the viewport.

## Interaction Design Rules

- Prefer custom pointer or mouse-driven interactions over the HTML Drag and Drop API for node editors and block canvases.
- Keep positions in canvas space. Convert from client space only at the input boundary.
- If you rewrite manual dragging, prefer Pointer Events plus `setPointerCapture()` so drag continues even when the pointer leaves the node.
- If drag updates become heavy, move temporary drag state to refs or batch visual updates with `requestAnimationFrame()` before committing final coordinates to React state.
- Separate hit targets clearly:
  - node shell starts drag
  - ports start link creation
  - resize handles start resize
  - HUD buttons must stop propagation
- Draw connections in a dedicated SVG or canvas layer. Do not bake edge geometry into node DOM.
- Snap on drop when precision matters more than continuous magnetic behavior.
- Use explicit min sizes and bounds. Do not rely on visual overflow to hide invalid geometry.

## Recommended Default For This Project

- Device cards: keep using `react-rnd`.
- Zoomable automation blocks: keep using manual drag inside `react-zoom-pan-pinch`.
- Future touch support: migrate manual mouse handlers to Pointer Events rather than native HTML5 drag-and-drop.

## External Sources

- [react-rnd Storybook](http://bokuweb.github.io/react-rnd/stories)
- [react-zoom-pan-pinch Props Docs](https://BetterTyped.github.io/react-zoom-pan-pinch/?path=/story/docs-props--page)
- [MDN: Element.setPointerCapture()](https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture)
- [MDN: HTML Drag and Drop API](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API)
- [MDN: Window.requestAnimationFrame()](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)
