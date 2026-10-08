"""Precision Boolean cut on FreeSurfer pial surface for lamp mounting.
Preserves 100% of original sulcal folds while adding a flat table base and a 62mm LED aperture.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import time
import manifold3d as m3d
import numpy as np
import trimesh


def cut_lamp_base(in_stl: Path, out_stl: Path, led_dia_mm: float = 62.0, z_flat_mm: float = -28.0) -> None:
    t0 = time.time()
    print(f"Loading {in_stl} ...")
    tri = trimesh.load(str(in_stl))
    mesh_m3d = m3d.Mesh(vert_properties=tri.vertices.astype(np.float32), tri_verts=tri.faces.astype(np.uint32))
    man_brain = m3d.Manifold(mesh_m3d)

    # 1. Flat bottom cut box
    box = m3d.Manifold.cube([300.0, 300.0, 50.0], center=True).translate([0, 0, z_flat_mm - 25.0])

    # 2. LED cylinder
    radius = led_dia_mm / 2.0
    cyl = m3d.Manifold.cylinder(height=58.0, radius_low=radius, radius_high=radius, circular_segments=72).translate([2.2, -10.6, z_flat_mm - 1.0])

    cut_brain = man_brain - box - cyl
    out_mesh = cut_brain.to_mesh()
    verts = np.asarray(out_mesh.vert_properties)
    faces = np.asarray(out_mesh.tri_verts)

    triangles = verts[faces].astype("<f4", copy=False)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    valid = lengths > 0
    normals[valid] /= lengths[valid, None]

    records = np.empty(
        len(faces),
        dtype=np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]),
    )
    records["normal"] = normals
    records["vertices"] = triangles
    records["attribute"] = 0

    out_stl.parent.mkdir(parents=True, exist_ok=True)
    with out_stl.open("wb") as stream:
        stream.write(b"Brain Lamp Pial 60mm LED Base STL".ljust(80, b" "))
        stream.write(np.asarray([len(faces)], dtype="<u4").tobytes())
        stream.write(records.tobytes())

    dims = verts.max(axis=0) - verts.min(axis=0)
    print(f"Saved {out_stl} in {time.time() - t0:.2f}s ({len(verts)} verts, {len(faces)} tris)")
    print(f"Dimensions: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Precision Boolean cut on FreeSurfer pial surface for lamp mounting.")
    parser.add_argument("--input", type=Path, default=repo_root / "output" / "03_科研原始表面" / "brain_pial_merged.stl")
    parser.add_argument("--output", type=Path, default=repo_root / "output" / "brain_lamp_pial_60mm_LED_base.stl")
    parser.add_argument("--led-dia", type=float, default=62.0)
    parser.add_argument("--z-flat", type=float, default=-28.0)
    args = parser.parse_args()

    cut_lamp_base(args.input, args.output, led_dia_mm=args.led_dia, z_flat_mm=args.z_flat)


if __name__ == "__main__":
    main()
