# 3D Printing & Model Catalog Guide

This directory contains the 3D meshes derived from high-resolution 3D T1 MRI structural neuroimaging using FreeSurfer 7.4.1 cortical reconstruction and topological geometric optimizations. All final models have been verified as watertight manifolds (`Watertight: True`) and are ready for 3D printing and computer graphics rendering.

> 📌 **Neuroanatomical Normative Report & Demographics**: Refer to the project root [**`../README.md`**](../README.md) for full quantitative metrics, cortical thickness, volumetric benchmarks, and anthropological cephalic ratios.

---

## 📁 Directory Structure & Model Classification

### `01_lamp_models_60mm_led` (Functional Lampshade Models)
Designed for illuminating brain nightstands and desk lamps. Features a precision bottom cylindrical cavity: **$\Phi 62\text{ mm} \times 45\text{ mm}$** (ceiling at $Z = +6.0\text{ mm}$), engineered to securely fit standard $60\text{ mm}$ diameter ($15 \sim 22\text{ mm}$ thick) LED puck lights while preserving the internal anatomical arch of the ventral cerebrum.

- **`01_cerebrum_only`**:
  - `ZBJ_lamp_cerebrum_60mm_hidden_bridge.stl` (**Top Recommendation for 3D Printing**): 2.31M faces. Integrates the authentic anatomical Corpus Callosum across both hemispheres internally. Completely eliminates artificial bridge seams visible from the dorsal view, providing continuous, natural sulcal contours down into the corpus callosum vault. Highly rigid and impact-resistant.
  - `ZBJ_lamp_cerebrum_60mm_hidden_bridge.obj`: High-poly OBJ edition with smooth vertex normals for real-time PBR shading.
  - `ZBJ_lamp_cerebrum_60mm_ultra_subdivided.stl` (Deep Fissure Baseline): 2.33M faces. 45mm bottom socket. The longitudinal fissure cuts deeply down without middle structural reinforcement.
  - `ZBJ_lamp_cerebrum_60mm_smooth.stl` (Lightweight Hollow Edition): 800K faces. Uniform 2.8mm thin shell wall with circular bottom aperture.
  - `ZBJ_lamp_cerebrum_60mm_smooth.obj`: Lightweight hollow lampshade in OBJ format.

- **`02_whole_brain_with_cerebellum`**:
  - `ZBJ_lamp_whole_brain_60mm_smooth.stl` (Whole Brain Lampshade): Integrates cortical folds with organic cerebellum envelope, free of voxel block artifacts.
  - `ZBJ_lamp_whole_brain_60mm_smooth.obj`: Whole-brain lampshade in OBJ format.

---

### `02_solid_display_models` (Display Sculptures & Solid Artworks)
Designed for artistic desktop sculptures, anatomical teaching models, and solid/hollow display prints.

- **`01_cerebrum_only`**:
  - `ZBJ_display_cerebrum_ultra_hollow_closed.stl` (Ultra-High-Res Closed Hollow): 2.24M faces. Seamless 360° exterior without holes. Internal core hollowed out by 60% (wall thickness: 2.8mm). Ideal for FDM printing to minimize filament usage.
  - `ZBJ_display_cerebrum_ultra_hollow_drain_hole.stl` (Resin Hollow with Drain Port): 2.24M faces. Internal cavity with a concealed $\Phi 15\text{ mm}$ drainage port on the base (essential for SLA resin drainage).
  - `ZBJ_solid_cerebrum_ultra_subdivided.stl` (Ultra-High-Res Solid): 2.09M faces. 100% solid cerebrum.
  - `ZBJ_solid_cerebrum_smooth.stl`: Standard 520K face solid model.

- **`02_whole_brain_with_cerebellum`**:
  - `ZBJ_solid_whole_brain_ultra_subdivided.stl` (**Top Recommendation for Solid Sculpture**): 2.286M faces. 100% solid, closed watertight manifold. Cerebrum with ultra-subdivided micro-folds. Cerebellum anti-aliased with continuous Signed Distance Fields (SDF) to eliminate 1mm voxel staircases, with biomimetic horizontal fissures, primary fissure, median vermian notch, and rounded cerebellar hemispheres. 1:1 true anatomical human scale.
  - `ZBJ_solid_whole_brain_ultra_subdivided.obj`: High-poly OBJ with smooth vertex normals for instant macOS Finder QuickLook preview and Blender/Maya rendering.

---

### `03_scientific_raw_surfaces` (Scientific Raw Meshes)
Unmodified anatomical pial surfaces directly reconstructed via FreeSurfer `recon-all`.
- `brain_pial_merged.stl`: Bilateral hemispheres merged surface (total area: $2,248.9\text{ cm}^2$).
- `ZBJ_brain_lh_pial.stl` / `ZBJ_brain_rh_pial.stl`: Left and right hemisphere independent meshes.
- `ZBJ_brain_pial_mesh_report.json`: Detailed geometric and metric audit report (volume, surface areas, bounding boxes).

---

### `04_minimal_envelope` (Convex/Smooth Hull)
- `ZBJ_brain_fast_envelope.stl`: Simplified brain envelope hull with smoothed sulci, ideal for rapid prototyping.

---

### `05_archive` (Historical Iterations)
Archive of intermediate design milestones and earlier test iterations.

---

## 🖨️ Recommended 3D Printing & Slicer Settings

### 1. Lampshade Edition (Optimized for Translucent Diffusion)
- **Process**: FDM (Bambu Lab, Creality, Prusa) or SLA Stereolithography
- **Filament**: White PLA / Semi-Translucent PLA / Frosted Resin (provides soft, warm diffusion)
- **Infill**: **0%** (Must be completely hollow inside to allow light to penetrate)
- **Wall Loops**: **3 ~ 4 loops** (Wall thickness $\approx 1.2 \sim 1.6\text{ mm}$)
- **Supports**: Enable **Tree / Organic Supports**, set placement to **"On build plate only"** (prevents internal supports from blocking light)
- **Orientation**: Flat base opening down directly on the build plate.

### 2. Solid Sculpture Edition
- **Infill**: $10\% \sim 15\%$ (Gyroid infill pattern provides high rigidity while saving filament)
- **Wall Loops**: 3 loops
- **Layer Height**: $0.12 \sim 0.16\text{ mm}$ (Adaptive layer height recommended for fine sulcal slopes)
