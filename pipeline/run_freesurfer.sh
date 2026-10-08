#!/usr/bin/env bash
set -euo pipefail

FREESURFER_HOME="${FREESURFER_HOME:-/usr/local/freesurfer/7.4.1}"
SUBJECTS_DIR="${SUBJECTS_DIR:-$PWD/work/freesurfer}"
SUBJECT_ID="${SUBJECT_ID:-subject01}"
T1_INPUT="${T1_INPUT:-$PWD/work/T1.nii.gz}"
THREADS="${THREADS:-7}"

export FREESURFER_HOME SUBJECTS_DIR
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
mkdir -p "$SUBJECTS_DIR"

recon-all \
  -subjid "$SUBJECT_ID" \
  -i "$T1_INPUT" \
  -all \
  -3T \
  -parallel \
  -threads "$THREADS" \
  -sd "$SUBJECTS_DIR" \
  -clean
