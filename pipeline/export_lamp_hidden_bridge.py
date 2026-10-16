"""Export Cerebrum Lamp Shade with Concealed Inter-Hemispheric Bridge (Corpus Callosum) & 60mm LED Base Aperture.

Key Features:
1. Retains natural deep dorsal interhemispheric fissure from the top view (no visible lumps or bridges).
2. Connects left and right hemispheres firmly from the inside around the Corpus Callosum level directly above the LED lamp cavity.
3. Hollows internal cerebrum with smooth clearance wall for soft, uniform translucent illumination.
4. Cuts a precision circular aperture (default 62.0mm diameter for 60.0mm standard LED lamp base pucks).
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


def write_stl(manifold_obj: m3d.Manifold, path: Path, header: str) -> None:
    mesh = manifold_obj.to_mesh()
    verts = np.asarray(mesh.vert_properties)
    faces = np.asarray(mesh.tri_verts)
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f_out:
        f_out.write(header.encode("ascii", "replace")[:80].ljust(80, b" "))
        f_out.write(np.asarray([len(faces)], dtype="<u4").tobytes())
        f_out.write(records.tobytes())
    dims = verts.max(axis=0) - verts.min(axis=0)
    print(f"Exported STL: {path.name} ({len(verts)} verts, {len(faces)} faces, {dims[0]:.1f}x{dims[1]:.1f}x{dims[2]:.1f}mm, {path.stat().st_size/1e6:.1f}MB)")


def write_obj(manifold_obj: m3d.Manifold, path: Path) -> None:
    mesh = manifold_obj.to_mesh()
    verts = np.asarray(mesh.vert_properties)
    faces = np.asarray(mesh.tri_verts)
    tri = trimesh.Trimesh(vertices=verts, faces=faces)
    path.parent.mkdir(parents=True, exist_ok=True)
    tri.export(str(path))
    print(f"Exported OBJ: {path.name} ({path.stat().st_size/1e6:.1f}MB)")


def load_cerebrum_mesh(solid_cerebrum_path: Path | None = None, surf_dir: Path | None = None) -> m3d.Manifold:
    """Load cerebrum mesh either from an existing STL file or directly from FreeSurfer pial surfaces."""
    if solid_cerebrum_path and solid_cerebrum_path.exists() and solid_cerebrum_path.is_file():
        print(f"1. Loading outer cerebrum mesh from STL: {solid_cerebrum_path}...")
        tri_outer = trimesh.load(str(solid_cerebrum_path))
        return m3d.Manifold(m3d.Mesh(vert_properties=tri_outer.vertices.astype(np.float32), tri_verts=tri_outer.faces.astype(np.uint32)))

    if surf_dir and surf_dir.exists():
        lh_file = surf_dir / "lh.pial.smooth3" if (surf_dir / "lh.pial.smooth3").exists() else surf_dir / "lh.pial"
        rh_file = surf_dir / "rh.pial.smooth3" if (surf_dir / "rh.pial.smooth3").exists() else surf_dir / "rh.pial"
        if lh_file.exists() and rh_file.exists():
            print(f"1. Loading and subdividing cerebrum from FreeSurfer surfaces: {lh_file.name}, {rh_file.name}...")
            vl, fl = nib.freesurfer.read_geometry(str(lh_file))
            vr, fr = nib.freesurfer.read_geometry(str(rh_file))
            print("   Subdividing cortical mesh (Loop subdivision, 1 iteration)...")
            vl_sub, fl_sub = trimesh.remesh.subdivide_loop(vl, fl, iterations=1)
            vr_sub, fr_sub = trimesh.remesh.subdivide_loop(vr, fr, iterations=1)
            v_c = np.vstack([vl_sub, vr_sub])
            f_c = np.vstack([fl_sub, fr_sub + len(vl_sub)])
            return m3d.Manifold(m3d.Mesh(vert_properties=v_c.astype(np.float32), tri_verts=f_c.astype(np.uint32)))

    raise FileNotFoundError(
        "Could not load cerebrum mesh. Please provide a valid --solid-cerebrum STL path "
        "or a FreeSurfer --surf-dir containing lh.pial and rh.pial."
    )


def generate_hidden_bridge_lamp(
    solid_cerebrum_path: Path | None,
    ribbon_path: Path,
    out_dir: Path,
    surf_dir: Path | None = None,
    led_dia_mm: float = 60.0,
    aperture_margin_mm: float = 2.0,
    base_name: str = "ZBJ_lamp_cerebrum_60mm_hidden_bridge",
) -> None:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)

    man_outer = load_cerebrum_mesh(solid_cerebrum_path=solid_cerebrum_path, surf_dir=surf_dir)

    print(f"2. Generating localized central bridge from {ribbon_path}...")
    rib_img = nib.load(str(ribbon_path))
    rib_data = np.asarray(rib_img.dataobj)
    vox2ras_tkr = rib_img.header.get_vox2ras_tkr()
    mask = ndimage.binary_fill_holes(rib_data > 0)

    # Localized interhemispheric connection strictly above LED cylinder (k in [113, 123], j in [104, 114])
    fissure_fill_local = np.zeros_like(mask, dtype=bool)
    for k in range(113, 124):
        slice_k = mask[:, :, k]
        if not slice_k.any():
            continue
        for j in range(104, 115):
            row = slice_k[:, j]
            if not row.any():
                continue
            if row[128:].any() and row[:128].any():
                i_right = np.where(row[:128])[0].max()
                i_left = 128 + np.where(row[128:])[0].min()
                if i_left - i_right <= 14:
                    fissure_fill_local[i_right : i_left + 1, j, k] = True

    bridge_dil = ndimage.binary_dilation(fissure_fill_local, structure=ndimage.generate_binary_structure(3, 1), iterations=2)
    bridge_flt = ndimage.gaussian_filter(bridge_dil.astype(float), sigma=1.0)
    v_br, f_br, _, _ = measure.marching_cubes(bridge_flt, level=0.5)
    ones = np.ones((v_br.shape[0], 1), dtype=v_br.dtype)
    v_br_w = (vox2ras_tkr @ np.hstack([v_br, ones]).T).T[:, :3]
    tri_br = trimesh.Trimesh(vertices=v_br_w, faces=f_br)
    trimesh.smoothing.filter_taubin(tri_br, lamb=0.5, nu=0.53, iterations=6)
    man_bridge = m3d.Manifold(m3d.Mesh(vert_properties=tri_br.vertices.astype(np.float32), tri_verts=tri_br.faces.astype(np.uint32)))

    print("3. Unioning outer mesh with localized bridge...")
    man_outer_bridged = man_outer + man_bridge

    print("4. Generating hollow inner cavity cutter from ribbon distance field...")
    dist = ndimage.distance_transform_edt(mask)
    cavity_mask = dist > 2.5
    cavity_flt = ndimage.gaussian_filter(cavity_mask.astype(float), sigma=1.0)
    v_cav, f_cav, _, _ = measure.marching_cubes(cavity_flt, level=0.5)
    ones = np.ones((v_cav.shape[0], 1), dtype=v_cav.dtype)
    v_cav_w = (vox2ras_tkr @ np.hstack([v_cav, ones]).T).T[:, :3]
    tri_cav = trimesh.Trimesh(vertices=v_cav_w, faces=f_cav)
    man_cav = m3d.Manifold(m3d.Mesh(vert_properties=tri_cav.vertices.astype(np.float32), tri_verts=tri_cav.faces.astype(np.uint32)))

    # Cylindrical opening at base for standard puck
    radius_aperture = (led_dia_mm + aperture_margin_mm) / 2.0
    cyl = m3d.Manifold.cylinder(height=58.0, radius_low=radius_aperture, radius_high=radius_aperture, circular_segments=72).translate([2.2, -10.6, -42.0])
    cutter = man_cav + cyl

    print("5. Performing boolean difference to hollow lampshade and create base aperture...")
    man_lamp_final = man_outer_bridged - cutter

    print("6. Cleaning mesh components...")
    mesh_raw = man_lamp_final.to_mesh()
    tri_raw = trimesh.Trimesh(vertices=mesh_raw.vert_properties, faces=mesh_raw.tri_verts)
    bodies = tri_raw.split(only_watertight=False)
    main_body = max(bodies, key=lambda b: len(b.faces))
    print(f"Main body: {len(main_body.vertices)} vertices, {len(main_body.faces)} faces, Watertight: {main_body.is_watertight}")

    man_main = m3d.Manifold(m3d.Mesh(
        vert_properties=np.ascontiguousarray(main_body.vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(main_body.faces, dtype=np.uint32),
    ))

    p_stl = out_dir / f"{base_name}.stl"
    p_obj = out_dir / f"{base_name}.obj"
    print(f"\n7. Exporting {base_name} models...")
    write_stl(man_main, p_stl, f"Lamp Cerebrum Hidden Bridge {led_dia_mm:.0f}mm")
    write_obj(man_main, p_obj)
    print(f"All operations completed in {time.time() - t0:.2f}s!")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Export cerebrum lamp with hidden bridge and LED socket.")
    parser.add_argument(
        "--surf-dir",
        type=Path,
        default=Path.home() / "brain_freesurfer_work" / "work" / "freesurfer" / "ZBJ_brain" / "surf",
        help="Path to FreeSurfer surf directory (containing lh.pial and rh.pial)",
    )
    parser.add_argument(
        "--solid-cerebrum",
        type=Path,
        default=None,
        help="Optional path to pre-existing solid cerebrum STL mesh",
    )
    parser.add_argument(
        "--ribbon",
        type=Path,
        default=Path.home() / "brain_freesurfer_work" / "work" / "freesurfer" / "ZBJ_brain" / "mri" / "ribbon.mgz",
        help="Path to FreeSurfer ribbon.mgz",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "01_lamp_shade_60mm_led",
        help="Output directory for generated lamp STL and OBJ files",
    )
    parser.add_argument("--led-dia", type=float, default=60.0, help="Diameter of circular LED lamp base in mm (default: 60.0)")
    parser.add_argument("--name", type=str, default="ZBJ_lamp_cerebrum_60mm_hidden_bridge", help="Base filename without extension")
    args = parser.parse_args()

    generate_hidden_bridge_lamp(
        solid_cerebrum_path=args.solid_cerebrum,
        ribbon_path=args.ribbon,
        out_dir=args.out_dir,
        surf_dir=args.surf_dir,
        led_dia_mm=args.led_dia,
        base_name=args.name,
    )


if __name__ == "__main__":
    main()
