"""Export a hollowed brain lamp model with a circular bottom aperture for a 60mm LED puck.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import time
import nibabel as nib
import numpy as np
from scipy import ndimage
from skimage import measure


def generate_hollow_lamp(nii_path: Path, out_stl: Path, led_diameter_mm: float = 60.0, wall_mm: float = 2.2) -> None:
    t0 = time.time()
    img = nib.load(str(nii_path))
    data = img.get_fdata()
    affine = img.affine
    zooms = img.header.get_zooms()[:3]

    mask = data > 80.0
    mask = ndimage.binary_fill_holes(mask)

    print("Computing Euclidean distance field...")
    dist = ndimage.distance_transform_edt(mask, sampling=zooms)

    grid_i, grid_j, grid_k = np.indices(mask.shape)
    homo = np.stack([grid_i.flatten(), grid_j.flatten(), grid_k.flatten(), np.ones(grid_i.size)], axis=0)
    world_coords = affine @ homo
    world_x = world_coords[0].reshape(mask.shape)
    world_y = world_coords[1].reshape(mask.shape)
    world_z = world_coords[2].reshape(mask.shape)

    # 1mm tolerance for puck fit
    radius_hole = (led_diameter_mm + 2.0) / 2.0
    center_x = 3.5
    center_y = -5.0
    z_cut = -18.0

    dist_axis = np.sqrt((world_x - center_x) ** 2 + (world_y - center_y) ** 2)
    in_cylinder = (dist_axis <= radius_hole) & (world_z <= z_cut)

    shell = (dist > 0) & (dist <= wall_mm)
    shell[in_cylinder] = False
    shell_float = ndimage.gaussian_filter(shell.astype(float), sigma=0.8)

    print("Extracting surface triangles...")
    verts, faces, normals, vals = measure.marching_cubes(shell_float, level=0.35)

    ones = np.ones((verts.shape[0], 1), dtype=verts.dtype)
    verts_world = (affine @ np.hstack([verts, ones]).T).T[:, :3]

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
        stream.write(b"Brain Lamp Hollow STL".ljust(80, b" "))
        stream.write(np.asarray([len(faces)], dtype="<u4").tobytes())
        stream.write(records.tobytes())

    dims = verts_world.max(axis=0) - verts_world.min(axis=0)
    print(f"Generated {out_stl} ({len(verts_world)} vertices, {len(faces)} triangles in {time.time() - t0:.2f}s)")
    print(f"Dimensions: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../T1_brain.nii.gz")
    parser.add_argument("--output", default="../output/ZBJ_brain_lamp_hollow_60mm_LED.stl")
    parser.add_argument("--led-diameter", type=float, default=60.0)
    parser.add_argument("--wall", type=float, default=2.2)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    in_path = (script_dir / args.input).resolve()
    out_path = (script_dir / args.output).resolve()
    generate_hollow_lamp(in_path, out_path, args.led_diameter, args.wall)


if __name__ == "__main__":
    main()
