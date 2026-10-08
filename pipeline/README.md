# Brain MRI to 3D Print Modeling Pipeline

Complete end-to-end Python & FreeSurfer pipeline for transforming high-resolution T1 MRI neuroimaging scans into 3D-printable solid sculptures and functional LED lampshades.

---

## 🛠️ Pipeline Architecture

1. **Cortical Reconstruction & Subcortical Segmentation (`run_pipeline.sh`)**:
   - Executes FreeSurfer `recon-all` (`-subjid ZBJ_brain -i T1.nii.gz -all -3T -parallel -threads 8`).
   - Extracts pial cortical surfaces (`lh.pial`, `rh.pial`), subcortical anatomical segmentation (`aseg.mgz`), and cortical ribbon (`ribbon.mgz`).

2. **Scientific Pial Surface Extraction (`export_all_surfaces.py`)**:
   - Extracts and joins bilateral hemispheres (`brain_pial_merged.stl`, `ZBJ_brain_lh_pial.stl`, `ZBJ_brain_rh_pial.stl`).
   - Calculates vertex counts, facet counts, bounding dimensions, and cortical surface area into `ZBJ_brain_pial_mesh_report.json`.

3. **Solid Whole Brain with Biomimetic Cerebellar Folia (`export_solid_whole_brain.py`)**:
   - Applies Loop subdivision to pial surfaces for ultra-smooth rendering.
   - Extracts Cerebellum and Brainstem from `aseg.mgz`. Uses a continuous Signed Distance Field (SDF) level set to eliminate 1mm voxel block staircases.
   - Modulates natural cerebellar folia ripples, primary fissure, horizontal fissure, and vermis notch.
   - Extracts and incorporates anatomical Corpus Callosum.
   - Computes watertight Boolean union via `manifold3d` to output full-anatomy solid STL & OBJ models.

4. **Concealed-Bridge LED Lampshade (`export_lamp_hidden_bridge.py`)**:
   - Incorporates a concealed interhemispheric structural bridge around the Corpus Callosum level directly above the LED cavity.
   - Preserves deep natural dorsal longitudinal fissures from the exterior view.
   - Generates a smooth internal cavity and 62mm circular base aperture for standard 60mm LED puck bases.

---

## 💻 Environment Setup

```bash
conda create -n MRI python=3.10 -y
conda activate MRI
pip install -r requirements.txt
```

---

## 📂 Script Catalog

| Script | Purpose | Output Format |
| :--- | :--- | :--- |
| `run_pipeline.sh` | Master pipeline execution script (FreeSurfer recon-all + surface export) | Mesh / Logs |
| `export_solid_whole_brain.py` | Complete solid whole brain with biomimetic cerebellar folia & corpus callosum | STL / OBJ |
| `export_lamp_hidden_bridge.py` | Concealed-bridge LED lampshade with 60mm bottom socket | STL / OBJ |
| `export_all_surfaces.py` | High-fidelity scientific pial surface exporter and geometry auditor | STL / JSON |
| `export_fast_envelope.py` | Rapid alpha-shape brain envelope extraction | STL |
| `cut_lamp_base.py` | Flat base plane trimmer and cylindrical socket cutter | STL |
