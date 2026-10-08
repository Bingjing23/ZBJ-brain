# 3D Printing & Model Catalog Guide

This directory houses the curated, flagship 3D meshes generated from 3.0T structural MRI data via FreeSurfer 7.4.1 cortical reconstruction and topological geometric optimization.

Both models are verified **100% watertight manifolds** (`Watertight: True`) at **1:1 true anatomical human scale**, optimized for high-end 3D printing and physical manufacturing.

---

## 📁 Curated Flagship Models

### 💡 1. `01_lamp_shade_60mm_led/` (Functional Translucent Lampshade)
*Designed for ambient bedside nightstands and desk lamps.*

* **Files**:
  * [`ZBJ_lamp_cerebrum_60mm_hidden_bridge.stl`](./01_lamp_shade_60mm_led/ZBJ_lamp_cerebrum_60mm_hidden_bridge.stl) (Binary STL, 115.4 MB, 1.154M vertices, 2.308M faces)
  * [`ZBJ_lamp_cerebrum_60mm_hidden_bridge.obj`](./01_lamp_shade_60mm_led/ZBJ_lamp_cerebrum_60mm_hidden_bridge.obj) (Wavefront OBJ with smooth vertex normals, 97.6 MB)
* **Dimensions**: $136.7 \times 161.8 \times 114.4\text{ mm}$ ($X \times Y \times Z$)
* **Key Features**:
  * **Concealed Corpus Callosum Bridge**: Seamlessly fuses the two hemispheres from inside using the anatomical corpus callosum directly above the LED cavity. The dorsal view displays 100% natural, deep interhemispheric fissures without visible external weld seams.
  * **Translucent Diffusion**: Internal core is hollowed out with a smooth clearance wall (2.2~2.8mm thickness), providing warm, uniform light diffusion.
  * **Precision Lamp Socket**: Base features a circular cavity of **$\Phi 62\text{ mm} \times 45\text{ mm}$** (depth ceiling at $Z = +6.0\text{ mm}$), engineered to house standard 60mm circular LED puck lights ($15 \sim 22\text{ mm}$ height) with ample space for wiring.

---

### 🧠 2. `02_solid_whole_brain/` (Complete Anatomical Solid Sculpture)
*Designed for high-end artistic desktop sculptures, 3D printing, and anatomical display.*

* **Files**:
  * [`ZBJ_solid_whole_brain_ultra_subdivided.stl`](./02_solid_whole_brain/ZBJ_solid_whole_brain_ultra_subdivided.stl) (Binary STL, 114.3 MB, 1.143M vertices, 2.286M faces)
  * [`ZBJ_solid_whole_brain_ultra_subdivided.obj`](./02_solid_whole_brain/ZBJ_solid_whole_brain_ultra_subdivided.obj) (Wavefront OBJ with smooth vertex normals, 97.2 MB)
* **Dimensions**: $136.7 \times 161.8 \times 136.2\text{ mm}$ ($X \times Y \times Z$)
* **Key Features**:
  * **100% Solid & Watertight**: Completely solid throughout with zero apertures or cavities.
  * **Full Anatomical Integration**: Seamlessly unites cerebral cortex, cerebellum, brainstem, and corpus callosum.
  * **SDF Continuous Anti-Aliasing**: Completely eradicates 1mm voxel staircase artifacts from MRI segmentations using continuous Signed Distance Fields and Taubin smoothing.
  * **Biomimetic Folia & Fissures**: Features authentic human cerebellar folia curves, horizontal fissures, primary fissure, and median vermian sulcus without artificial mechanical banding.

---

## 🖨️ Recommended 3D Printing & Slicer Settings

| Setting | 💡 Lampshade (`01_lamp_shade_60mm_led`) | 🧠 Solid Sculpture (`02_solid_whole_brain`) |
| :--- | :--- | :--- |
| **Recommended Material** | White PLA / Semi-Translucent PLA / Resin | White Marble PLA / Matte PLA / Resin |
| **Infill Ratio** | **0% (Must be completely hollow for light diffusion)** | **10% ~ 15% (Gyroid infill pattern)** |
| **Wall Loops** | 3 ~ 4 loops (Wall thickness $\approx 1.2 \sim 1.6\text{ mm}$) | 3 ~ 4 loops |
| **Layer Height** | $0.12 \sim 0.16\text{ mm}$ | $0.12 \sim 0.16\text{ mm}$ (Adaptive layers recommended) |
| **Supports** | **Tree / Organic Supports (On build plate only)** | Tree / Organic Supports |
| **Print Orientation** | Flat circular base directly on build plate | Ventral side down (brainstem base facing build plate) |
