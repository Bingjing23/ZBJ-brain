"""Extract and integrate Cerebellum + Brainstem from FreeSurfer aseg.mgz with Cerebrum pial surface.
Generates:
1. ZBJ_whole_brain_with_cerebellum.stl (Complete anatomical whole brain)
2. ZBJ_whole_brain_lamp_60mm_LED_base.stl (Whole brain with 60mm LED socket and flat table base)
"""
from __future__ import annotations

import argparse
from pathlib import Path
import time
import manifold3d as m3d
import nibabel as nib
import numpy as np
from scipy import ndimage
from skimage import measure
import trimesh


def export_whole_brain(cerebrum_stl: Path, aseg_mgz: Path, out_dir: Path, led_dia_mm: float = 62.0) -> None:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Cerebrum pial mesh
    print(f"Loading Cerebrum pial surface from {cerebrum_stl} ...")
    tri_c = trimesh.load(str(cerebrum_stl))
    mesh_m3d = m3d.Mesh(vert_properties=tri_c.vertices.astype(np.float32), tri_verts=tri_c.faces.astype(np.uint32))
    man_cerebrum = m3d.Manifold(mesh_m3d)

    # 2. Extract Cerebellum + Brainstem from aseg.mgz
    print(f"Extracting Cerebellum and Brainstem from {aseg_mgz} ...")
    aseg_img = nib.load(str(aseg_mgz))
    aseg_data = np.asarray(aseg_img.dataobj)
    vox2ras_tkr = aseg_img.header.get_vox2ras_tkr()

    # Labels: 7 (L-WM), 8 (L-Cortex), 46 (R-WM), 47 (R-Cortex), 16 (Brain-Stem)
    cb_mask = np.isin(aseg_data, [7, 8, 46, 47, 16])
    cb_mask = ndimage.binary_fill_holes(cb_mask)
    cb_float = ndimage.gaussian_filter(cb_mask.astype(float), sigma=0.8)
    v, f, n, vals = measure.marching_cubes(cb_float, level=0.5)

    # Map to FreeSurfer Surface RAS space
    ones = np.ones((v.shape[0], 1), dtype=v.dtype)
    cb_world = (vox2ras_tkr @ np.hstack([v, ones]).T).T[:, :3]

    man_cb = m3d.Manifold(m3d.Mesh(vert_properties=cb_world.astype(np.float32), tri_verts=f.astype(np.uint32)))

    # 3. Boolean Union: Cerebrum + Cerebellum + Brainstem
    print("Computing Boolean Union of Cerebrum + Cerebellum + Brainstem...")
    man_whole = man_cerebrum + man_cb

    def write_stl(manifold_obj: m3d.Manifold, path: Path, header: str) -> None:
        mesh = manifold_obj.to_mesh()
        verts = np.asarray(mesh.vert_properties)
        faces = np.asarray(mesh.tri_verts)
        triangles = verts[faces].astype("<f4", copy=False)
        normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        lengths = np.linalg.norm(normals, axis=1)
        valid = lengths > 0
        normals[valid] /= lengths[valid, None]
        records = np.empty(len(faces), dtype=np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]))
        records["normal"] = normals
        records["vertices"] = triangles
        records["attribute"] = 0
        with open(path, "wb") as f_out:
            f_out.write(header.encode("ascii", "replace")[:80].ljust(80, b" "))
            f_out.write(np.asarray([len(faces)], dtype="<u4").tobytes())
            f_out.write(records.tobytes())
        dims = verts.max(axis=0) - verts.min(axis=0)
        print(f"Exported {path.name}: {len(verts)} verts, {len(faces)} faces, Dims: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm")

    # Save Solid Whole Brain
    solid_path = out_dir / "ZBJ_whole_brain_with_cerebellum.stl"
    write_stl(man_whole, solid_path, "Whole Brain with Cerebellum Solid STL")

    # Save Whole Brain Lamp with 60mm LED base aperture
    lamp_path = out_dir / "ZBJ_whole_brain_lamp_60mm_LED_base.stl"
    z_flat = -48.0
    radius = led_dia_mm / 2.0
    box = m3d.Manifold.cube([300.0, 300.0, 50.0], center=True).translate([0, 0, z_flat - 25.0])
    cyl = m3d.Manifold.cylinder(height=55.0, radius_low=radius, radius_high=radius, circular_segments=72).translate([0.0, -25.0, z_flat - 1.0])
    man_whole_lamp = man_whole - box - cyl
    write_stl(man_whole_lamp, lamp_path, "Whole Brain Lamp 60mm LED Base STL")
    print(f"Finished in {time.time() - t0:.2f}s!")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Export basic whole brain model from FreeSurfer aseg and pial mesh.")
    parser.add_argument("--cerebrum", type=Path, default=repo_root / "output" / "03_科研原始表面" / "brain_pial_merged.stl")
    parser.add_argument("--aseg", type=Path, default=Path.home() / "brain_freesurfer_work" / "work" / "freesurfer" / "ZBJ_brain" / "mri" / "aseg.mgz")
    parser.add_argument("--out-dir", type=Path, default=repo_root / "output")
    args = parser.parse_args()

    export_whole_brain(args.cerebrum, args.aseg, args.out_dir)


if __name__ == "__main__":
    main()
