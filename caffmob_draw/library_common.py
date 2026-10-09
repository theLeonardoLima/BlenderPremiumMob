"""Funções comuns às bibliotecas do usuário: caixa dos objetos e miniatura (feature 009, T003).

Vieram de `customize/library_io.py` (feature 003) sem mudança de comportamento, para a biblioteca de objetos
(`object_library/`) usar a mesma mecânica.
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore


def world_box(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = []
    for obj in objects:
        if obj.type != 'MESH' or obj.hide_get():
            continue
        evaluated = obj.evaluated_get(depsgraph)
        corners += [obj.matrix_world @ Vector(c) for c in evaluated.bound_box]
    if not corners:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    return (Vector([min(c[i] for c in corners) for i in range(3)]),
            Vector([max(c[i] for c in corners) for i in range(3)]))


def thumbnail(context, objects, filepath):
    scene = context.scene
    saved = (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage,
             scene.render.engine, scene.render.filepath, scene.render.film_transparent)
    cam_data = bpy.data.cameras.new("Miniatura")
    cam_obj = bpy.data.objects.new("Miniatura", cam_data)
    scene.collection.objects.link(cam_obj)
    try:
        lo, hi = world_box(objects)
        center, size = (lo + hi) / 2.0, max((hi - lo).length, 0.1)
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = size * 1.1
        cam_obj.location = center + Vector((size, -size, size * 0.8))
        cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()
        scene.camera = cam_obj
        scene.render.resolution_x = scene.render.resolution_y = 256
        scene.render.resolution_percentage = 100
        scene.render.engine = 'BLENDER_WORKBENCH'
        scene.render.film_transparent = True
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return True
    except (RuntimeError, OSError) as exc:
        print(f"CAFFMob Draw: miniatura não gerada ({exc})")
        return False
    finally:
        (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage,
         scene.render.engine, scene.render.filepath, scene.render.film_transparent) = saved
        bpy.data.objects.remove(cam_obj)
        bpy.data.cameras.remove(cam_data)
