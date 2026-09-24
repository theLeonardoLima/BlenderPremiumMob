"""Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py"""
import json
import sys
import tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blendertomob as addon
from blendertomob.cutting.part_extractor import extract_parts_from_scene

addon.register()
addon.load_file_post(None)
assert addon.hb_project.get_main_scene() is not None
assert 'wall_color' in addon.BTM_AddonPreferences.bl_rna.properties
assert 'dimension_settings' in bpy.context.scene.btm_settings.bl_rna.properties
assert extract_parts_from_scene(bpy.context) == [], 'Default cube must not produce cabinet parts'
assert bpy.ops.btm.cabinet_builder(width=0.9) == {'FINISHED'}
first = bpy.context.object
assert abs(first.btm_cabinet.width - 0.9) < 1e-6
assert len(first.data.vertices) > 0
assert bpy.ops.btm.cabinet_builder() == {'FINISHED'}
second = bpy.context.object
assert first != second
parts = extract_parts_from_scene(bpy.context)
assert len(parts) == 14, [(p.id, p.module_ref) for p in parts]
assert {p.module_ref for p in parts} == {first.name, second.name}
assert bpy.ops.btm.calculate_nesting() == {'FINISHED'}
cache = json.loads(bpy.context.scene['btm_nesting_json_cache'])
assert cache['stats']['total_placed_parts'] == 14
assert cache['stats']['unplaced_count'] == 0
with tempfile.TemporaryDirectory() as directory:
    output = str(Path(directory) / 'cut_plan.json')
    assert bpy.ops.btm.export_cut_plan_json(filepath=output) == {'FINISHED'}
    exported = json.loads(Path(output).read_text())
    assert len(exported['parts_catalog']) == 14
    assert exported['project']['placed_parts_count'] == 14
addon.unregister()
assert not hasattr(bpy.types.Scene, 'btm_settings')
addon.register()
addon.load_file_post(None)
addon.unregister()
print('BLENDER_SMOKE_OK', flush=True)
