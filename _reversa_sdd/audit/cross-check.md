# Audit Report: System Audit & Wall Editor Feature Specification

**Date:** 2026-08-01  
**Feature:** Python System Audit (Medidas, Configurações Globais, Compatibilidade Blender) & Algoritmo Editor de Parede 🧱  
**Analyzed Scope:** `/home/theleoinfo/www/BlenderToMob` and `/home/theleoinfo/Downloads/python-skills-main/skills/python`

---

## 📊 Executive Summary

| Severity | Count | Primary Impact Area |
|----------|-------|----------------------|
| **CRITICAL** | 2 | Blender 5.0.2 / 4.x legacy API compatibility & GN modifier access; Catalog gallery items missing assembly specs |
| **HIGH** | 3 | Dimensions not applied across non-standard furniture items; Global cabinet assembly settings un-propagated to gallery items; Missing interactive Wall Editor algorithm |
| **MEDIUM** | 2 | Multi-unit conversion precision in UI; GPU overlay shader fallback across Blender 3.6 - 5.2 |
| **LOW** | 1 | UI icon fallback for Blender version differences |

---

## 📋 Audit Findings Table

| ID | Severity | Axis | Description | Location |
|----|----------|------|-------------|----------|
| `A001` | **CRITICAL** | Legacy Coherence | Blender 5.0.2 / 4.x compatibility errors in Geometry Nodes modifier inputs access (`mod[identifier]` vs `mod.properties.inputs[identifier].value`) and `interface.items_tree` lookup breaking legacy Blender builds. | [hb_utils.py](file:///home/theleoinfo/www/BlenderToMob/hb_utils.py#L10-L40), [compat.py](file:///home/theleoinfo/www/BlenderToMob/blendertomob/compat.py#L1-L88) |
| `A002` | **CRITICAL** | Coverage | Catalog gallery items (`catalog_data.py`) using `_todo(...)` placeholders for Floating Base, Pie Cut, Appliance cabinets, Vanities, Bookcases, etc. fail to instantiate real cabinet classes or apply global assembly configs when placed. | [catalog_data.py](file:///home/theleoinfo/www/BlenderToMob/catalog/catalog_data.py#L80-L345), [ops_catalog.py](file:///home/theleoinfo/www/BlenderToMob/catalog/ops_catalog.py#L20-L55) |
| `A003` | **HIGH** | Functionality | Dimensions (`width`, `height`, `depth`) are not applied to all furniture items (standalone parts, catalog placeholders, appliances) due to missing `apply_placement_width` / `update_dim` property callbacks. | [hb_props.py](file:///home/theleoinfo/www/BlenderToMob/hb_props.py#L330-L425), [types_face_frame.py](file:///home/theleoinfo/www/BlenderToMob/product_libraries/face_frame/types_face_frame.py#L8100-L8200) |
| `A004` | **HIGH** | Consistency | Global cabinet assembly configurations (`hb_face_frame` / `hb_frameless` door style, material, carcass construction, toe kick, molding packages) are not synced when placing gallery items or when global settings are changed. | [ops_placement.py](file:///home/theleoinfo/www/BlenderToMob/product_libraries/face_frame/operators/ops_placement.py#L3680-L3695), [props_hb_face_frame.py](file:///home/theleoinfo/www/BlenderToMob/product_libraries/face_frame/props_hb_face_frame.py#L500-L600) |
| `A005` | **HIGH** | Feature Gap | New Wall Editor feature (`Editor de Parede` 🧱 button, interactive draw mode with endpoint snap, real-time dynamic dimensions in mm/cm/m/in/ft, vector angle indicator, TAB input switching, properties panel) is not yet implemented. | [operators/walls.py](file:///home/theleoinfo/www/BlenderToMob/operators/walls.py#L940-L1000), [ui/view3d_sidebar.py](file:///home/theleoinfo/www/BlenderToMob/ui/view3d_sidebar.py#L1-L100) |
| `A006` | **MEDIUM** | Consistency | Dynamic unit converter (`mm`, `cm`, `m`, `in`, `ft`) requires consistent bi-directional formatting across 3D viewport overlays and property panels during modal placement and editing. | [units.py](file:///home/theleoinfo/www/BlenderToMob/units.py#L1-L60), [hb_placement.py](file:///home/theleoinfo/www/BlenderToMob/hb_placement.py#L1650-L1700) |
| `A007` | **MEDIUM** | Legacy Coherence | GPU overlay shaders (`UNIFORM_COLOR` vs `3D_UNIFORM_COLOR` / `POLYLINE_UNIFORM_COLOR`) require fallback handling to prevent viewport draw crashes on Blender 3.6 / 4.x / 5.0.2 / 5.1+. | [hb_placement.py](file:///home/theleoinfo/www/BlenderToMob/hb_placement.py#L1651), [hb_gpu_draw.py](file:///home/theleoinfo/www/BlenderToMob/hb_gpu_draw.py#L1-L100) |
| `A008` | **LOW** | UI Polish | UI icon for Wall Editor button should fall back gracefully if custom emojis/icons `🧱` are not rendered natively in older Blender UI fonts. | [operators/viewport_hud.py](file:///home/theleoinfo/www/BlenderToMob/operators/viewport_hud.py#L500-L600) |
| `A009` | **CRITICAL** | API Registration | `HB_Wall_Editor_Props` FloatProperty registration error on `angle_absolute`, `angle_relative`, `step_angular` due to invalid `unit='ANGLE'` instead of `unit='ROTATION'`, `subtype='ANGLE'`. | [hb_props.py](file:///home/theleoinfo/www/BlenderToMob/hb_props.py#L876-L916), [blendertomob/hb_props.py](file:///home/theleoinfo/www/BlenderToMob/blendertomob/hb_props.py#L876-L916) |

---

## 🔍 Detailed Analysis of Findings & Impact

### A001 [CRITICAL]: Blender 5.0.2 & Legacy Version Compatibility
- **Impact:** Blender 5.0.2 (and versions < 5.2.0) throw `AttributeError` if `mod.properties.inputs` is accessed directly. Furthermore, `node_group.interface.items_tree` access in Blender 4.0 - 5.0.2 requires fallback checks against `node_group.inputs` (Blender < 4.0) and safe exception handling.
- **Resolution Path:** Enhance `hb_utils.py` and `blendertomob/compat.py` with robust version-agnostic helpers (`get_gn_input`, `set_gn_input`, `try_get_gn_input`, `get_builtin_shader`), update `bl_info` in `__init__.py` to declare `"blender": (3, 6, 0)`, and adjust `blender_manifest.toml`.

### A002 & A004 [CRITICAL / HIGH]: Gallery Items & Global Assembly Configs
- **Impact:** Gallery items in `catalog/catalog_data.py` currently point to `_todo(...)` or trigger operators without initializing full cabinet assembly properties. Consequently, changing global styles (door style, finish wood/color, toe kick height, frame thickness) does not propagate to gallery furniture.
- **Resolution Path:** Wire all catalog entries to concrete cabinet classes in `product_libraries/face_frame` / `frameless` (or universal catalog dispatcher), and ensure `assign_style_to_cabinet` and global scene assembly defaults are unconditionally applied upon creation and on global property updates.

### A003 [HIGH]: Dimensions Application across Furniture Items
- **Impact:** Furniture objects (such as appliances, standalone parts, catalog items) do not update their geometry node inputs or object bounding dimensions when `width`, `height`, or `depth` are modified in the UI or typed during placement.
- **Resolution Path:** Implement universal dimension update callbacks (`update_dimensions_callback`) across `Face_Frame_Cabinet_Props`, `Frameless_Cabinet_Props`, appliance types, and part types, forcing geometry node inputs (`Dim X`, `Dim Y`, `Dim Z`) and recalculation solver updates.

### A005 [HIGH]: Interactive Wall Editor Algorithmic Requirements
- **Impact:** Feature gap for the user's interactive wall builder.
- **Resolution Path:** Build `home_builder_walls_OT_interactive_wall_editor` modal operator and UI button/dropdown `🧱 Editor de Parede` with:
  1. Interactive mouse snapping to wall endpoints and vertices.
  2. Real-time dynamic distance gauge overlay with unit selection (`mm`, `cm`, `m`, `in`, `ft`).
  3. Vector angle indicator (0°, 90°, 180°, 270°, 360°) with 45° magnetic angle step.
  4. Direct keyboard typing for length input and `TAB` key field cycling.
  5. Graphical Properties Panel for dimensions (length, height, thickness, elevation), angles (absolute/relative), orientation (left/right), step increments (linear 50mm, angular 45°), wall type (Normal/Drywall), and `Utilizar valores como padrão`.

---

## 🟢 Verified Passing Items

- ✅ Core Face Frame cabinet solver (`solver_face_frame.py`) supports dynamic bay recalculation.
- ✅ Unit conversion utilities (`units.py`) support inch, meter, mm, cm, ft.
- ✅ Viewport HUD registration mechanism (`viewport_hud.py`) supports interactive overlay buttons.
- ✅ Base wall geometry generation (`operators/walls.py`) supports curve & mesh wall creation.

---

> Digite **CONTINUAR** para prosseguir com a geração das especificações executáveis (`/reversa-writer`).
