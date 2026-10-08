#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Pipeline: ZBJ-brain T1 MRI to FreeSurfer Pial STL Mesh
# Based on: https://github.com/Neuro-biology/mri-dicom-to-freesurfer-pial-stl
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN_DATA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Find input NIfTI volume
if [ -n "${1:-}" ]; then
    INPUT_NII="$1"
elif [ -f "$BRAIN_DATA_DIR/Bing_T1W_3D.nii" ]; then
    INPUT_NII="$BRAIN_DATA_DIR/Bing_T1W_3D.nii"
elif [ -f "$BRAIN_DATA_DIR/T1_brain.nii.gz" ]; then
    INPUT_NII="$BRAIN_DATA_DIR/T1_brain.nii.gz"
else
    INPUT_NII="$BRAIN_DATA_DIR/T1.nii.gz"
fi
OUTPUT_DIR="$BRAIN_DATA_DIR/output"

# Local workspace outside cloud storage to avoid sync file locks during FreeSurfer execution
WORK_BASE="${FREESURFER_WORK_DIR:-$HOME/brain_freesurfer_work}"
WORK_DIR="$WORK_BASE/work"
SUBJECTS_DIR="$WORK_DIR/freesurfer"
SUBJECT_ID="ZBJ_brain"
THREADS="${THREADS:-8}"
PYTHON_EXEC="${PYTHON_EXEC:-$(which python3)}"

mkdir -p "$WORK_DIR" "$SUBJECTS_DIR" "$OUTPUT_DIR"

echo "================================================================="
echo " Starting MRI -> FreeSurfer -> STL Pipeline for: $SUBJECT_ID"
echo " Time: $(date)"
echo " Workspace: $WORK_DIR"
echo " OneDrive Target: $OUTPUT_DIR"
echo "================================================================="

# ------------------------------------------------------------------------------
# 1. License Check
# ------------------------------------------------------------------------------
LICENSE_PATH=""
for cand in "$BRAIN_DATA_DIR/../license.txt" "$WORK_BASE/license.txt" "$HOME/license.txt" "${FREESURFER_HOME:-}/license.txt" "$SCRIPT_DIR/license.txt"; do
    if [ -f "$cand" ]; then
        LICENSE_PATH="$cand"
        break
    fi
done

if [ -z "$LICENSE_PATH" ]; then
    echo ""
    echo " [ERROR] FreeSurfer license file (license.txt) not found!"
    echo " FreeSurfer requires a valid license file to run."
    echo " You can obtain a free license in seconds by filling out:"
    echo "   👉 https://surfer.nmr.mgh.harvard.edu/registration.html"
    echo ""
    echo " Once received, save the 3-4 line license file to:"
    echo "   👉 $WORK_BASE/license.txt"
    echo ""
    echo " Then re-run this script."
    exit 1
fi
echo " [OK] Using FreeSurfer license: $LICENSE_PATH"
cp "$LICENSE_PATH" "$WORK_DIR/license.txt"
cp "$LICENSE_PATH" "$WORK_BASE/license.txt" 2>/dev/null || true

# ------------------------------------------------------------------------------
# 2. Input NIfTI Preparation
# ------------------------------------------------------------------------------
T1_GZ="$WORK_DIR/T1.nii.gz"
if [ ! -f "$T1_GZ" ]; then
    if [ ! -f "$INPUT_NII" ]; then
        echo " [ERROR] Input file not found: $INPUT_NII"
        exit 1
    fi
    echo " [INFO] Compressing $INPUT_NII -> $T1_GZ ..."
    gzip -c "$INPUT_NII" > "$T1_GZ"
    echo " [OK] T1.nii.gz prepared successfully."
else
    echo " [OK] Found existing $T1_GZ ($(ls -lh "$T1_GZ" | awk '{print $5}'))"
fi

# ------------------------------------------------------------------------------
# 3. FreeSurfer recon-all Execution
# ------------------------------------------------------------------------------
LH_PIAL="$SUBJECTS_DIR/$SUBJECT_ID/surf/lh.pial"
RH_PIAL="$SUBJECTS_DIR/$SUBJECT_ID/surf/rh.pial"

if [ -f "$LH_PIAL" ] && [ -f "$RH_PIAL" ]; then
    echo " [INFO] FreeSurfer surfaces already exist at $LH_PIAL and $RH_PIAL."
    echo " Skipping recon-all computation."
else
    echo " [INFO] Initiating FreeSurfer recon-all (estimated 4-8 hours)..."
    if command -v recon-all >/dev/null 2>&1; then
        echo " [INFO] Using native FreeSurfer installation..."
        export FREESURFER_HOME="${FREESURFER_HOME:-/usr/local/freesurfer/7.4.1}"
        export SUBJECTS_DIR
        source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
        recon-all \
          -subjid "$SUBJECT_ID" \
          -i "$T1_GZ" \
          -all \
          -3T \
          -parallel \
          -threads "$THREADS" \
          -sd "$SUBJECTS_DIR" \
          -clean 2>&1 | tee "$WORK_DIR/recon-all.log"
    else
        echo " [INFO] Native FreeSurfer not in PATH. Using Docker container freesurfer/freesurfer:7.4.1..."
        if ! docker ps >/dev/null 2>&1; then
            echo " [ERROR] Docker daemon is not running! Please start Docker Desktop and retry."
            exit 1
        fi

        docker run --rm --platform linux/amd64 \
          -v "$WORK_DIR:/work" \
          -v "$WORK_DIR/license.txt:/opt/freesurfer/license.txt:ro" \
          -v "$WORK_DIR/license.txt:/opt/freesurfer/.license:ro" \
          -v "$WORK_DIR/license.txt:/usr/local/freesurfer/7.4.1/license.txt:ro" \
          -v "$WORK_DIR/license.txt:/usr/local/freesurfer/7.4.1/.license:ro" \
          -e FS_LICENSE="/work/license.txt" \
          freesurfer/freesurfer:7.4.1 \
          recon-all \
            -subjid "$SUBJECT_ID" \
            -i "/work/T1.nii.gz" \
            -all \
            -3T \
            -parallel \
            -threads "$THREADS" \
            -sd "/work/freesurfer" \
            -clean 2>&1 | tee "$WORK_DIR/recon-all.log"
    fi
fi

# ------------------------------------------------------------------------------
# 4. Export Surfaces to STL & Sync to OneDrive
# ------------------------------------------------------------------------------
echo ""
echo " [INFO] Exporting reconstructed pial surfaces to binary STL..."

"$PYTHON_EXEC" "$SCRIPT_DIR/export_all_surfaces.py" \
  --subjects-dir "$SUBJECTS_DIR" \
  --subject-id "$SUBJECT_ID" \
  --output-dir "$WORK_DIR" \
  --sync-to "$OUTPUT_DIR"

echo "================================================================="
echo " Pipeline Complete!"
echo " Exported STL files are in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"
echo "================================================================="
