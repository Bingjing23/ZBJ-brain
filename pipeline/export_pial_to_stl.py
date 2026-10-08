"""Merge native left/right FreeSurfer pial surfaces into a binary STL."""
from __future__ import annotations

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np


def export(left_path: Path, right_path: Path, output_path: Path) -> None:
    left_vertices, left_faces = nib.freesurfer.read_geometry(left_path)
    right_vertices, right_faces = nib.freesurfer.read_geometry(right_path)
    vertices = np.vstack([left_vertices, right_vertices])
    faces = np.vstack([left_faces, right_faces + len(left_vertices)])
    triangles = vertices[faces].astype("<f4", copy=False)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals[lengths > 0] /= lengths[lengths > 0, None]
    records = np.empty(
        len(faces),
        dtype=np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]),
    )
    records["normal"] = normals
    records["vertices"] = triangles
    records["attribute"] = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        stream.write(b"Anonymous FreeSurfer pial surface".ljust(80, b" "))
        stream.write(np.asarray([len(faces)], dtype="<u4").tobytes())
        stream.write(records.tobytes())
    print(f"{output_path}: {len(vertices)} vertices, {len(faces)} triangles")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", default="work/freesurfer/subject01/surf/lh.pial")
    parser.add_argument("--right", default="work/freesurfer/subject01/surf/rh.pial")
    parser.add_argument("--output", default="work/brain_pial_merged.stl")
    args = parser.parse_args()
    export(Path(args.left), Path(args.right), Path(args.output))


if __name__ == "__main__":
    main()
