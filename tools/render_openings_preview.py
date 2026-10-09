"""Prévias da porta e da janela reais no estilo da `blender-product-polish` (feature 010, T027; D-15).

Uso:
    blender --background --factory-startup --python tools/render_openings_preview.py

A skill original (`~/.agent/skills/product-polish`) roda pelo Blender MCP com um GLB; aqui os mesmos valores são
aplicados por script: preset `studio` (luz principal 350 W, preenchimento 250 W, recorte 250 W, rebatida 100 W),
EEVEE e fundo neutro. Saída: `caffmob_draw/openings/assets/previa_porta.png` e `previa_janela.png`, para comparar com a
`docs/porta_realista_080x210/previa.png` do gerador original.
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()

from caffmob_draw.openings import build, door_core, window_core  # noqa: E402

OUT = ROOT / "caffmob_draw" / "openings" / "assets"
STUDIO = (("Luz principal", (-2.0, -3.0, 4.0), 350.0), ("Preenchimento", (3.0, -1.0, 2.8), 250.0),
          ("Recorte", (0.0, 2.0, 3.8), 250.0), ("Rebatida", (1.0, -2.0, 0.2), 100.0))


def point(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def render(parts, target, size, ortho, name):
    scene = bpy.context.scene
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    build.build(parts, scene.collection)
    for label, loc, power in STUDIO:
        light = bpy.data.lights.new(label, 'AREA')
        light.energy, light.size, light.shape = power, 2.0, 'DISK'
        obj = bpy.data.objects.new(label, light)
        scene.collection.objects.link(obj)
        obj.location = loc
        point(obj, target)
    world = bpy.data.worlds.get("Estúdio") or bpy.data.worlds.new("Estúdio")
    world.color = (0.55, 0.62, 0.72)
    background = world.node_tree.nodes.get("Background") if world.node_tree else None
    if background is not None:
        background.inputs[0].default_value = (0.55, 0.62, 0.72, 1.0)
        background.inputs[1].default_value = 0.35
    scene.world = world
    cam_data = bpy.data.cameras.new("Câmera")
    cam = bpy.data.objects.new("Câmera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = Vector(target) + Vector((2.6, -4.6, 1.6))
    point(cam, target)
    cam_data.type, cam_data.ortho_scale = 'ORTHO', ortho
    scene.camera = cam
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.film_transparent = False
    scene.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)


OUT.mkdir(parents=True, exist_ok=True)
render(door_core.door_parts(0.80, 2.10, 0.15), (0.45, 0.075, 1.08), (880, 1100), 2.6, "previa_porta.png")
render(window_core.window_parts(1.20, 1.00, 0.15), (0.6, 0.075, 0.5), (1000, 860), 1.9, "previa_janela.png")
