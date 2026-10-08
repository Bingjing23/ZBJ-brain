"""Generate a fast brain envelope 3D STL from skull-stripped brain NIfTI (T1_brain.nii.gz).
Uses marching cubes on the brain volume and aligns to real-world scanner coordinates (mm).
"""
from __future__ import annotations

import argparse
from pathlib import Path
import time
import nibabel as nib
import numpy as np
from skimage import measure


def export_envelope(nii_path: Path, out_stl: Path, threshold: float = 100.0) -> None:
    t0 = time.time()
    print(f"Loading {nii_path} ...")
    img = nib.load(str(nii_path))
    data = img.get_fdata()
    affine = img.affine

    print(f"Running Marching Cubes (threshold={threshold}) ...")
    verts, faces, normals, values = measure.marching_cubes(data, level=threshold)

    # Affine transformation to scanner RAS mm space
    ones = np.ones((verts.shape[0], 1), dtype=verts.dtype)
    verts_homo = np.hstack([verts, ones])
    verts_world = (affine @ verts_homo.T).T[:, :3]

    # Calculate face normals in world space
    triangles = verts_world[faces].astype("<f4", copy=False)
    face_normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(face_normals, axis=1)
    valid = lengths > 0
    face_normals[valid] /= lengths[valid, None]

    records = np.empty(
        len(faces),
        dtype=np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]),
    )
    records["normal"] = face_normals
    records["vertices"] = triangles
    records["attribute"] = 0

    out_stl.parent.mkdir(parents=True, exist_ok=True)
    with out_stl.open("wb") as stream:
        stream.write(b"Fast Brain Envelope STL".ljust(80, b" "))
        stream.write(np.asarray([len(faces)], dtype="<u4").tobytes())
        stream.write(records.tobytes())

    dims = verts_world.max(axis=0) - verts_world.min(axis=0)
    print(f"Exported: {out_stl} ({len(verts_world)} vertices, {len(faces)} triangles in {time.time() - t0:.2f}s)")
    print(f"Dimensions: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../T1_brain.nii.gz", help="Path to skull-stripped T1_brain.nii.gz")
    parser.add_argument("--output", default="../output/ZBJ_brain_fast_envelope.stl", help="Output STL path")
    parser.add_argument("--threshold", type=float, default=100.0, help="Iso-surface intensity threshold")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    in_path = (script_dir / args.input).resolve()
    out_path = (script_dir / args.output).resolve()
    export_envelope(in_path, out_path, args.threshold)


if __name__ == "__main__":
    main()
