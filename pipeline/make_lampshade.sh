#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Helper Script: Generate Translucent Concealed-Bridge Brain Lampshade
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default FreeSurfer paths (can be overridden via environment or arguments)
SUBJECTS_DIR="${FREESURFER_WORK_DIR:-$HOME/brain_freesurfer_work}/work/freesurfer"
SUBJECT_ID="${SUBJECT_ID:-ZBJ_brain}"

SURF_DIR="${1:-$SUBJECTS_DIR/$SUBJECT_ID/surf}"
RIBBON_MGZ="${2:-$SUBJECTS_DIR/$SUBJECT_ID/mri/ribbon.mgz}"
OUT_DIR="${3:-$REPO_ROOT/output/01_lamp_shade_60mm_led}"
LED_DIA="${4:-60.0}"
PYTHON_EXEC="${PYTHON_EXEC:-python3}"

echo "================================================================="
echo " Generating Translucent Concealed-Bridge Brain Lampshade..."
echo " Surf Directory: $SURF_DIR"
echo " Ribbon File:    $RIBBON_MGZ"
echo " Output Target:  $OUT_DIR"
echo " LED Socket Dia: ${LED_DIA}mm"
echo "================================================================="

"$PYTHON_EXEC" "$SCRIPT_DIR/export_lamp_hidden_bridge.py" \
  --surf-dir "$SURF_DIR" \
  --ribbon "$RIBBON_MGZ" \
  --out-dir "$OUT_DIR" \
  --led-dia "$LED_DIA"

echo ""
echo "================================================================="
echo " [SUCCESS] Lampshade STL and OBJ are ready for 3D printing:"
ls -lh "$OUT_DIR"
echo "================================================================="
