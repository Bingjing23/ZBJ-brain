"""Export Ultra-High Resolution Solid Whole Brain 3D Model with Natural Cerebellar Folia.

Integrates:
1. Cerebrum pial cortical surface (with Loop subdivision for ultra-smooth high-poly rendering)
2. Cerebellum and Brainstem from FreeSurfer segmentation (with SDF continuous level-set anti-aliasing
   and biomimetic anatomical folia / fissure ripple textures)
3. Anatomical Corpus Callosum connecting the hemispheres
All combined into a single watertight manifold 3D mesh (STL & OBJ formats).
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


def load_cerebrum(surf_dir: Path, subdivide: bool = True) -> m3d.Manifold:
    """Load left and right pial surfaces and optionally apply Loop subdivision."""
    lh_file = surf_dir / "lh.pial.smooth3" if (surf_dir / "lh.pial.smooth3").exists() else surf_dir / "lh.pial"
    rh_file = surf_dir / "rh.pial.smooth3" if (surf_dir / "rh.pial.smooth3").exists() else surf_dir / "rh.pial"
    print(f"Loading cerebrum surfaces: {lh_file.name}, {rh_file.name}")
    vl, fl = nib.freesurfer.read_geometry(str(lh_file))
    vr, fr = nib.freesurfer.read_geometry(str(rh_file))

    if subdivide:
        print("Subdividing cortical mesh (Loop subdivision, 1 iteration)...")
        vl, fl = trimesh.remesh.subdivide_loop(vl, fl, iterations=1)
        vr, fr = trimesh.remesh.subdivide_loop(vr, fr, iterations=1)

    v_c = np.vstack([vl, vr])
    f_c = np.vstack([fl, fr + len(vl)])
    return m3d.Manifold(m3d.Mesh(vert_properties=v_c.astype(np.float32), tri_verts=f_c.astype(np.uint32)))


def extract_cerebellum_and_stem(aseg_path: Path, add_folia: bool = True) -> m3d.Manifold:
    """Extract Cerebellum & Brainstem with SDF anti-aliasing and anatomical folia ripples."""
    print(f"Extracting Cerebellum & Brainstem from {aseg_path}...")
    aseg_img = nib.load(str(aseg_path))
    aseg_data = np.asarray(aseg_img.dataobj)
    vox2ras = aseg_img.header.get_vox2ras_tkr()

    # Labels: 7 (L-WM), 8 (L-Cortex), 46 (R-WM), 47 (R-Cortex), 16 (Brain-Stem)
    cb_mask = np.isin(aseg_data, [7, 8, 46, 47, 16])
    cb_mask = ndimage.binary_fill_holes(cb_mask)

    idx = np.argwhere(cb_mask)
    pad = 8
    min_c = np.maximum(0, idx.min(axis=0) - pad)
    max_c = np.minimum(aseg_data.shape, idx.max(axis=0) + pad + 1)
    crop_mask = cb_mask[min_c[0]:max_c[0], min_c[1]:max_c[1], min_c[2]:max_c[2]]

    # Continuous Signed Distance Field (SDF) eliminates 1mm voxel staircases
    print("Computing SDF level set for smooth anti-aliased reconstruction...")
    pos_dist = ndimage.distance_transform_edt(crop_mask)
    neg_dist = ndimage.distance_transform_edt(~crop_mask)
    sdf = pos_dist - neg_dist
    sdf_flt = ndimage.gaussian_filter(sdf, sigma=1.2)
    v_s, f_s, _, _ = measure.marching_cubes(sdf_flt, level=0.0)
    v_s = (vox2ras @ np.hstack([v_s + min_c, np.ones((len(v_s), 1))]).T).T[:, :3]

    m_base = trimesh.Trimesh(v_s, f_s)
    trimesh.smoothing.filter_taubin(m_base, lamb=0.5, nu=0.53, iterations=10)

    if add_folia:
        print("Modulating biomimetic cerebellar folia ripples and primary/horizontal fissures...")
        v_sub, f_sub = trimesh.remesh.subdivide_loop(m_base.vertices, m_base.faces, iterations=1)
        m_folia = trimesh.Trimesh(v_sub, f_sub)

        v = m_folia.vertices
        n = m_folia.vertex_normals
        stem_dist = np.maximum(np.abs(v[:, 0]) - 14, 0) + np.maximum(-v[:, 1] - 34, 0)
        stem_weight = np.clip(stem_dist / 8.0, 0, 1)
        top_fade = np.clip((-v[:, 2] - 12.0) / 10.0, 0, 1)
        post_fade = np.clip((-v[:, 1] - 14.0) / 15.0, 0, 1)
        cb_weight = top_fade * post_fade * stem_weight

        arch = -0.0028 * (v[:, 0] ** 2) + 0.10 * (v[:, 1] + 55.0)
        z_folia = v[:, 2] + arch

        wavelength = 3.0
        k1 = 2 * np.pi / wavelength
        w1 = np.sin(z_folia * k1)
        w2 = 0.20 * np.sin(z_folia * 2 * k1 + 0.5)
        fissure_prim = -0.75 * np.exp(-((v[:, 2] - (-24.0)) / 2.8) ** 2)
        fissure_horiz = -0.90 * np.exp(-((v[:, 2] - (-36.0)) / 3.2) ** 2)
        vermis_notch = -0.45 * np.exp(-((v[:, 0] / 5.0) ** 2)) * np.clip((-v[:, 1] - 35) / 25.0, 0, 1)
        drift = 0.15 * np.sin(v[:, 0] * 0.1 + v[:, 1] * 0.08)

        disp = cb_weight * (w1 * 0.65 + w2 + fissure_prim + fissure_horiz + vermis_notch + drift)
        m_folia.vertices += n * disp[:, None]
        return m3d.Manifold(m3d.Mesh(vert_properties=m_folia.vertices.astype(np.float32), tri_verts=m_folia.faces.astype(np.uint32)))

    return m3d.Manifold(m3d.Mesh(vert_properties=m_base.vertices.astype(np.float32), tri_verts=m_base.faces.astype(np.uint32)))


def extract_corpus_callosum(aseg_path: Path) -> m3d.Manifold:
    """Extract and smooth Corpus Callosum (labels 251-255)."""
    print(f"Extracting Corpus Callosum from {aseg_path}...")
    aseg_img = nib.load(str(aseg_path))
    aseg_data = np.asarray(aseg_img.dataobj)
    vox2ras = aseg_img.header.get_vox2ras_tkr()

    cc_mask = np.isin(aseg_data, [251, 252, 253, 254, 255])
    struct = ndimage.generate_binary_structure(3, 1)
    cc_dil = ndimage.binary_dilation(cc_mask, structure=struct, iterations=2)
    cc_flt = ndimage.gaussian_filter(cc_dil.astype(float), sigma=0.8)
    v_cc, f_cc, _, _ = measure.marching_cubes(cc_flt, level=0.5)
    v_cc_w = (vox2ras @ np.hstack([v_cc, np.ones((len(v_cc), 1))]).T).T[:, :3]

    tri_cc = trimesh.Trimesh(vertices=v_cc_w, faces=f_cc)
    trimesh.smoothing.filter_taubin(tri_cc, lamb=0.5, nu=0.53, iterations=6)
    return m3d.Manifold(m3d.Mesh(vert_properties=tri_cc.vertices.astype(np.float32), tri_verts=tri_cc.faces.astype(np.uint32)))


def generate_solid_whole_brain(surf_dir: Path, aseg_path: Path, out_dir: Path, base_name: str = "ZBJ_solid_whole_brain_ultra_subdivided") -> None:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)

    man_cerebrum = load_cerebrum(surf_dir, subdivide=True)
    man_cb = extract_cerebellum_and_stem(aseg_path, add_folia=True)
    man_cc = extract_corpus_callosum(aseg_path)

    print("Computing Boolean Union of Cerebrum + Cerebellum/Brainstem + Corpus Callosum...")
    man_whole = man_cerebrum + man_cb + man_cc
    mesh_whole = man_whole.to_mesh()
    tri_whole = trimesh.Trimesh(vertices=mesh_whole.vert_properties, faces=mesh_whole.tri_verts)
    bodies = tri_whole.split(only_watertight=False)
    main_whole = max(bodies, key=lambda b: len(b.faces))
    print(f"Main body: {len(main_whole.vertices)} vertices, {len(main_whole.faces)} faces, Watertight: {main_whole.is_watertight}")

    man_final = m3d.Manifold(m3d.Mesh(
        vert_properties=np.ascontiguousarray(main_whole.vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(main_whole.faces, dtype=np.uint32),
    ))

    p_stl = out_dir / f"{base_name}.stl"
    p_obj = out_dir / f"{base_name}.obj"
    write_stl(man_final, p_stl, "Complete Solid Whole Brain Ultra Subdivided (Anatomical Folia)")
    write_obj(man_final, p_obj)
    print(f"Successfully finished solid whole brain model in {time.time() - t0:.2f}s!")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Export ultra-high resolution solid whole brain 3D model.")
    parser.add_argument("--surf-dir", type=Path, default=Path.home() / "brain_freesurfer_work" / "work" / "freesurfer" / "ZBJ_brain" / "surf")
    parser.add_argument("--aseg", type=Path, default=Path.home() / "brain_freesurfer_work" / "work" / "freesurfer" / "ZBJ_brain" / "mri" / "aseg.mgz")
    parser.add_argument("--out-dir", type=Path, default=repo_root / "output" / "02_solid_display_models" / "02_whole_brain_with_cerebellum")
    parser.add_argument("--name", type=str, default="ZBJ_solid_whole_brain_ultra_subdivided")
    args = parser.parse_args()

    generate_solid_whole_brain(args.surf_dir, args.aseg, args.out_dir, args.name)


if __name__ == "__main__":
    main()
