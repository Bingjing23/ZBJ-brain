"""Extended FreeSurfer surface to STL exporter.
Exports merged pial surface (brain_pial_merged.stl) and individual hemisphere STLs,
calculates bounding boxes and surface areas, and copies final meshes to target destination.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np


def write_stl(vertices: np.ndarray, faces: np.ndarray, output_path: Path, header_text: str = "FreeSurfer pial surface") -> None:
    triangles = vertices[faces].astype("<f4", copy=False)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    valid_normals = lengths > 0
    normals[valid_normals] /= lengths[valid_normals, None]

    records = np.empty(
        len(faces),
        dtype=np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]),
    )
    records["normal"] = normals
    records["vertices"] = triangles
    records["attribute"] = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as stream:
        header_bytes = header_text.encode("ascii", errors="replace")[:80].ljust(80, b" ")
        stream.write(header_bytes)
        stream.write(np.asarray([len(faces)], dtype="<u4").tobytes())
        stream.write(records.tobytes())


def compute_mesh_stats(vertices: np.ndarray, faces: np.ndarray) -> dict:
    triangles = vertices[faces]
    cross_prod = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    surface_area = 0.5 * np.sum(np.linalg.norm(cross_prod, axis=1))
    min_coords = vertices.min(axis=0).tolist()
    max_coords = vertices.max(axis=0).tolist()
    size_dims = (vertices.max(axis=0) - vertices.min(axis=0)).tolist()

    return {
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "surface_area_mm2": float(surface_area),
        "bounding_box_min_mm": min_coords,
        "bounding_box_max_mm": max_coords,
        "dimensions_mm": {
            "width_x_LR": float(size_dims[0]),
            "length_y_PA": float(size_dims[1]),
            "height_z_IS": float(size_dims[2]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FreeSurfer surfaces to STL")
    parser.add_argument("--subjects-dir", default="work/freesurfer", help="FreeSurfer SUBJECTS_DIR")
    parser.add_argument("--subject-id", default="ZBJ_brain", help="Subject ID")
    parser.add_argument("--output-dir", default="work", help="Output directory for generated STLs")
    parser.add_argument("--sync-to", default="", help="Optional directory to copy final STLs and reports")
    args = parser.parse_args()

    surf_dir = Path(args.subjects_dir) / args.subject_id / "surf"
    lh_path = surf_dir / "lh.pial"
    rh_path = surf_dir / "rh.pial"

    if not lh_path.exists() or not rh_path.exists():
        raise FileNotFoundError(
            f"Could not find pial surfaces at:\n  {lh_path}\n  {rh_path}\n"
            f"Please verify that FreeSurfer recon-all completed successfully."
        )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading surfaces for subject '{args.subject_id}'...")
    lh_verts, lh_faces = nib.freesurfer.read_geometry(lh_path)
    rh_verts, rh_faces = nib.freesurfer.read_geometry(rh_path)

    # 1. Export Left Hemisphere
    lh_stl = out_dir / f"{args.subject_id}_lh_pial.stl"
    write_stl(lh_verts, lh_faces, lh_stl, f"{args.subject_id} lh.pial")
    lh_stats = compute_mesh_stats(lh_verts, lh_faces)
    print(f"Exported LH: {lh_stl} ({lh_stats['vertices']} vertices, {lh_stats['triangles']} triangles)")

    # 2. Export Right Hemisphere
    rh_stl = out_dir / f"{args.subject_id}_rh_pial.stl"
    write_stl(rh_verts, rh_faces, rh_stl, f"{args.subject_id} rh.pial")
    rh_stats = compute_mesh_stats(rh_verts, rh_faces)
    print(f"Exported RH: {rh_stl} ({rh_stats['vertices']} vertices, {rh_stats['triangles']} triangles)")

    # 3. Export Merged Surface (brain_pial_merged.stl)
    merged_verts = np.vstack([lh_verts, rh_verts])
    merged_faces = np.vstack([lh_faces, rh_faces + len(lh_verts)])
    merged_stl = out_dir / "brain_pial_merged.stl"
    write_stl(merged_verts, merged_faces, merged_stl, f"{args.subject_id} merged pial")
    merged_stats = compute_mesh_stats(merged_verts, merged_faces)
    print(f"Exported Merged: {merged_stl} ({merged_stats['vertices']} vertices, {merged_stats['triangles']} triangles)")
    print(f"Merged Dimensions (mm): {merged_stats['dimensions_mm']}")

    # Save summary report
    report = {
        "subject_id": args.subject_id,
        "merged": merged_stats,
        "left_hemisphere": lh_stats,
        "right_hemisphere": rh_stats,
    }
    report_file = out_dir / f"{args.subject_id}_pial_mesh_report.json"
    with report_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Sync to user folder if specified
    if args.sync_to:
        target_dir = Path(args.sync_to)
        target_dir.mkdir(parents=True, exist_ok=True)
        for src in [merged_stl, lh_stl, rh_stl, report_file]:
            dst = target_dir / src.name
            shutil.copy2(src, dst)
            print(f"Copied {src.name} -> {dst}")

    print("All STL exports and reports successfully finished!")


if __name__ == "__main__":
    main()
