"""Reprodução e regressão do BUG-20261007-TBY3: todo objeto era tratado como parede (`object_kind` padrão `WALL`).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TBY3_walls.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.geometry.mesh_gen import generate_wall_from_segments  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402
from caffmob_draw.walls2d import scene_io  # noqa: E402

ctx = bpy.context
env.clean_scene()


def opening_poll():
    return bpy.types.Operator.bl_rna_get_subclass_py('CAFFMOB_OT_insert_opening').poll(ctx)


def layer_wall(name):
    pts = [(0, 0), (3, 0), (3, 2)]
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    ctx.collection.objects.link(obj)
    obj.btm_plane.object_kind = 'WALL'
    obj["btm_wall_segments"] = json.dumps([{'start': list(a), 'end': list(b), 'thickness': 0.15, 'height': 2.6,
                                            'offset': 0.0} for a, b in zip(pts, pts[1:])])
    generate_wall_from_segments(obj, [{'start': Vector(a), 'end': Vector(b), 'thickness': 0.15, 'height': 2.6,
                                       'offset': 0.0} for a, b in zip(pts, pts[1:])])
    return obj


# 1. Reprodução: um cubo comum (sem marcação) não é parede em nenhum lugar.
bpy.ops.mesh.primitive_cube_add()
cube = ctx.object
info = classify.classify(cube)
assert info.kind != classify.WALL, info
assert not scene_io.is_other_layer_wall(cube)
assert not opening_poll(), "inserir abertura não deve ficar disponível sem parede"

# 2. Regressão: a parede da camada nova (tipo gravado de propósito) continua sendo parede.
wall = layer_wall("ParedeNova")
info = classify.classify(wall)
assert (info.kind, info.library) == (classify.WALL, 'BTM'), info
assert scene_io.is_other_layer_wall(wall)
assert opening_poll()

# 3. Regressão: salvar e abrir o arquivo mantém a parede como parede e o cubo como não parede.
path = os.path.join(tempfile.mkdtemp(), "tby3.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
env.addon.load_file_post(None)
cube, wall = bpy.data.objects["Cube"], bpy.data.objects["ParedeNova"]
assert classify.classify(cube).kind != classify.WALL
assert classify.classify(wall).kind == classify.WALL
assert scene_io.is_other_layer_wall(wall) and not scene_io.is_other_layer_wall(cube)
print("blender_bug_TBY3_walls: OK")
