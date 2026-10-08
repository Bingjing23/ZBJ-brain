# ZBJ-Brain 3D 打印与建模模型库指南

本项目基于个人 3D T1 MRI 核磁共振扫描数据，通过 FreeSurfer 7.4.1 高精度皮层重建与图形学几何优化生成，所有模型均已完成水密（Watertight Manifold）闭合校验，可直接用于 3D 打印与三维渲染。

> 📌 **完整生理档案与神经解剖常模报告**：详见根目录 [**`../README.md`**](../README.md)，包含脑体积、皮层厚度、记忆海马体常模对比及东亚头型比例深度分析。

---

## 📁 目录架构与模型分类

### `01_灯罩版_60mm_LED底孔` (Lamp Models)
专为制作大脑台灯/小夜灯设计。底部垂直开有 **$\Phi 62\text{ mm}$ 圆槽**（深度精调优化为 **$45\text{ mm}$**，顶端位于 $Z = +6.0\text{ mm}$），既能从容卡入市面常见的 $15 \sim 22\text{ mm}$ 厚度 $60\text{ mm}$ 直径 LED 圆盘小夜灯，又完整保留了脑底内部的中央解剖拱门。
- **`01_无小脑_端脑皮层灯罩`**：
  - `ZBJ_lamp_cerebrum_60mm_hidden_bridge.stl`：**【⭐⭐3D打印首选·真实胼胝体解剖连接版】** 231万面，提取真实核磁共振胼胝体（Corpus Callosum）全连续解剖结构有机桥接两半球；彻底消除点焊连桥在俯视时的断续人工缝隙，脑沟自然平滑过渡到底部胼胝体，外表 100% 原始形态无疙瘩，力学刚性极强；45mm 底孔。
  - `ZBJ_lamp_cerebrum_60mm_hidden_bridge.obj`：带平滑法线 OBJ 版本。
  - `ZBJ_lamp_cerebrum_60mm_ultra_subdivided.stl`：**【解剖纯深沟原版】** 233万面，45mm 底孔，左右半球纵裂完全深切到底部，中段无加固连接。
  - `ZBJ_lamp_cerebrum_60mm_smooth.stl`：**【轻量空心灯罩】** 80万面版，具备 2.8mm 均匀薄壁内腔与底部开孔。
  - `ZBJ_lamp_cerebrum_60mm_smooth.obj`：轻量空心灯罩带平滑法线 OBJ 版本。
- **`02_含小脑_全脑结构灯罩`**：
  - `ZBJ_lamp_whole_brain_60mm_smooth.stl`：**【全脑主力灯罩】** 大脑皮层与有机小脑一体化成型，小脑无方块感。
  - `ZBJ_lamp_whole_brain_60mm_smooth.obj`：全脑带平滑法线 OBJ 版本。

---

### `02_实心版_完整艺术摆件` (Solid & Hollow Display Models)
针对雕刻、手办摆件、解剖教学或实心/中空 3D 打印。
- **`01_无小脑_端脑皮层实心`**：
  - `ZBJ_display_cerebrum_ultra_hollow_closed.stl`：**【超高精·全封闭中空版】** 224万面，外表 360° 无孔完整大脑，内部挖空 60%（壁厚2.8mm），FDM 打印首选，轻便省料。
  - `ZBJ_display_cerebrum_ultra_hollow_drain_hole.stl`：**【超高精·排液孔中空版】** 224万面，内部中空，底部预留 Φ15mm 隐蔽小排液孔（光敏树脂 SLA 打印必备）。
  - `ZBJ_solid_cerebrum_ultra_subdivided.stl`：**【超高精·纯实心版】** 209万面，从内到外 100% 纯实心。
  - `ZBJ_solid_cerebrum_smooth.stl`：52万面标准实心版本。
- **`02_含小脑_全脑结构实心`**：
  - `ZBJ_solid_whole_brain_ultra_subdivided.stl`：**【⭐⭐全脑实心摆件首选·超高精自然解剖小叶与裂隙版】** 228.6万面，端脑+小脑+脑干+胼胝体100%水密一体实心模型，无任何开孔或挖空；彻底消除 1mm 体素阶梯方块，摈弃机械条纹与同心圆，真实呈现神经解剖学大体形态（小脑水平裂、原裂、正中蚓部纵沟与圆润小脑半球）；端脑达 ultra_subdivided 级高精微曲面，1:1 真人真实解剖尺寸。
  - `ZBJ_solid_whole_brain_ultra_subdivided.obj`：带平滑顶点法线（Smooth Vertex Normals）的超高精 OBJ 版本，支持 macOS 空格键 QuickLook 预览及 Blender/Maya 渲染。

---

### `03_科研原始表面` (Scientific Raw)
FreeSurfer `recon-all` 重构输出的 1:1 未做几何形变修改的原始解剖曲面。
- `brain_pial_merged.stl`：左右双半球合并曲面（总面积 $2,248.9\text{ cm}^2$）。
- `ZBJ_brain_lh_pial.stl` / `ZBJ_brain_rh_pial.stl`：左、右半球独立曲面。
- `ZBJ_brain_pial_mesh_report.json`：详细解剖几何统计报告（体积、表面积、Bounding Box）。

---

### `04_极简外包络版` (Minimal Envelope)
- `ZBJ_brain_fast_envelope.stl`：脑沟完全平滑闭合的极简外轮廓块，适合作为快速打样或外壳基底。

---

### `05_历史迭代归档` (Archive)
开发过程中的中间测试文件与早期版本备份。

---

## 🖨️ 3D 打印与切片建议

### 1. 灯罩版打印配置（透光效果最佳）
- **打印工艺**：FDM 打印（推荐拓竹 Bambu Lab / 创想三维等）或 SLA 光敏树脂
- **材料选择**：**白色 PLA** / **半透明 PLA**（透光漫反射最佳）
- **填充率 (Infill)**：**0%**（完全中空，切勿内部填充）
- **外壁层数 (Wall Loops)**：**3 ~ 4 层**（壁厚约 $1.2 \sim 1.6\text{ mm}$）
- **支撑类型**：开启 **树状支撑 (Tree / Organic Supports)**，位置设为 **“仅接触构建板 (On build plate only)”**，防止内部长出支撑影响透光。
- **打印朝向**：底部圆孔朝下、平放在热床上打印。

### 2. 实心摆件版打印配置
- **填充率**：$10\% \sim 15\%$（配合 Gyroid 陀螺仪填充，手感扎实且节省耗材）
- **外壁层数**：3 层
- **层高**：$0.12\text{ mm} \sim 0.16\text{ mm}$（开启自适应层高更佳）
