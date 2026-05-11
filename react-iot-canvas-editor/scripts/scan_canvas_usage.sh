#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${1:-<PROJECT_ROOT>/webapp}"

if [[ ! -d "$REPO_PATH" ]]; then
  echo "Repo not found: $REPO_PATH" >&2
  exit 1
fi

echo "Repo: $REPO_PATH"

echo
echo "== Canvas dependencies =="
if [[ -f "$REPO_PATH/package.json" ]]; then
  rg -n '"react-rnd"|"react-zoom-pan-pinch"|"react-dnd"|"dnd-kit"|"konva"|"fabric"' "$REPO_PATH/package.json" || true
else
  echo "package.json not found"
fi

echo
echo "== Canvas hotspots =="
if [[ -d "$REPO_PATH/src" ]]; then
  rg -n 'react-rnd|TransformWrapper|TransformComponent|dragGrid|resizeGrid|bounds=|scale=|onTransformed|panning=|data-automation-port|data-automation-node|onDragStop|onResizeStop|canvasLayouts|NODE_WIDTH|NODE_HEIGHT|setPointerCapture|onDrop|dragstart|dataTransfer|dropzone' "$REPO_PATH/src" || true
else
  echo "src directory not found"
fi
