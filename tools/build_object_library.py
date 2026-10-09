"""Gera os itens embutidos da biblioteca de objetos (feature 009, T021; RF-07, D-13).

Uso:
    blender --background --factory-startup --python tools/build_object_library.py

Modelados pelo projeto (origem "CAFFMob Draw", licença GPL-3.0-or-later), em BMesh e metros, sem imagens:
- Porta lisa 80: batente (esquadria) + folha de giro de 90°;
- Janela de correr 120: esquadria + 2 folhas de correr;
- Cooktop 4 bocas; Mesa 120 × 80 (tampo como peça de produção); Vaso; Quadro.
Saída: `caffmob_draw/object_library/items/<CATEGORIA>/<item_id>.blend|.json|.png`.
"""

import shutil
import sys
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
bpy.context.preferences.view.use_translate_new_dataname = False

import caffmob_draw as addon  # noqa: E402

addon.register()

from caffmob_draw.aggregates import convert, group, leaf  # noqa: E402
from caffmob_draw.object_library import catalog, item_io, store  # noqa: E402

LICENSE = "GPL-3.0-or-later"
COLORS = {"Branco Neve": (0.92, 0.92, 0.9, 1), "Carvalho": (0.55, 0.38, 0.22, 1), "Vidro": (0.6, 0.75, 0.8, 0.35),
          "Alumínio": (0.7, 0.72, 0.75, 1), "Preto": (0.04, 0.04, 0.045, 1), "Inox": (0.6, 0.6, 0.62, 1),
          "Terracota": (0.62, 0.3, 0.18, 1), "Folhagem": (0.16, 0.38, 0.17, 1), "Tela": (0.85, 0.82, 0.74, 1)}


def material(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = COLORS[name]
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = COLORS[name]
        bsdf.inputs['Alpha'].default_value = COLORS[name][3]
    return mat


def mesh(name, mat, *shapes):
    """Malha com caixas `('box', lo, hi)` e cilindros `('cyl', centro, raio, altura)`, em metros."""
    bm = bmesh.new()
    for shape in shapes:
        if shape[0] == 'box':
            (x0, y0, z0), (x1, y1, z1) = shape[1], shape[2]
            geom = bmesh.ops.create_cube(bm, size=1.0)['verts']
            bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=geom)
            bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=geom)
        else:
            (cx, cy, cz), radius, height = shape[1], shape[2], shape[3]
            geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=radius, radius2=shape[4]
                                         if len(shape) > 4 else radius, depth=height)['verts']
            bmesh.ops.translate(bm, vec=(cx, cy, cz + height / 2), verts=geom)
    data = bpy.data.meshes.new(name)
    bm.to_mesh(data)
    bm.free()
    data.materials.append(material(mat))
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def leaf_group(frame, part, name):
    bpy.context.view_layer.update()
    sash = group.create_group([part], 'LEAF', name)
    world = sash.matrix_world.copy()
    sash.parent = frame
    sash.matrix_parent_inverse = frame.matrix_world.inverted()
    sash.matrix_world = world
    bpy.context.view_layer.update()
    return sash


def door():
    jamb, depth = 0.07, 0.035
    frame_mesh = mesh("Batente", "Branco Neve", ('box', (0, 0, 0), (jamb, depth, 2.17)),
                      ('box', (0.8 + jamb, 0, 0), (0.8 + 2 * jamb, depth, 2.17)),
                      ('box', (0, 0, 2.1), (0.8 + 2 * jamb, depth, 2.17)))
    part = mesh("Folha", "Branco Neve", ('box', (jamb + 0.002, 0.0, 0.005), (0.8 + jamb - 0.002, depth, 2.098)),
                ('cyl', (0.8 + jamb - 0.07, -0.03, 1.0), 0.012, 0.03))
    bpy.context.view_layer.update()
    frame = group.create_group([frame_mesh], 'FRAME', "Porta lisa 80")
    sash = leaf_group(frame, part, "Folha da porta")
    leaf.make_leaf(sash, frame, 'SWING', hinge='LEFT', swing_sign='OUT', max_angle=90.0)
    return frame


def window():
    w, h, depth, bar = 1.2, 1.0, 0.06, 0.04
    frame_mesh = mesh("Esquadria", "Alumínio", ('box', (0, 0, 0), (bar, depth, h)), ('box', (w - bar, 0, 0), (w, depth, h)),
                      ('box', (bar, 0, 0), (w - bar, depth, bar)), ('box', (bar, 0, h - bar), (w - bar, depth, h)))
    frame = None
    sashes = []
    leaf_w = (w - 2 * bar) / 2 + 0.02
    for i, (x0, y0) in enumerate(((bar, 0.008), (w - bar - leaf_w, 0.032))):
        part = mesh(f"Folha {i + 1}", "Vidro", ('box', (x0, y0, bar), (x0 + leaf_w, y0 + 0.02, h - bar)))
        sashes.append(part)
    bpy.context.view_layer.update()
    frame = group.create_group([frame_mesh], 'FRAME', "Janela de correr 120")
    for i, part in enumerate(sashes):
        sash = leaf_group(frame, part, f"Folha de correr {i + 1}")
        leaf.make_leaf(sash, frame, 'SLIDE', slide_dir='POS_X' if i == 0 else 'NEG_X', travel=0.5)
    return frame


def cooktop():
    plate = mesh("Mesa de vidro", "Preto", ('box', (0, 0, 0), (0.58, 0.51, 0.006)))
    burners = mesh("Queimadores", "Inox", *[('cyl', (x, y, 0.006), r, 0.012) for x, y, r in
                                           ((0.15, 0.14, 0.05), (0.43, 0.14, 0.04), (0.15, 0.37, 0.04),
                                            (0.43, 0.37, 0.06))])
    bpy.context.view_layer.update()
    return group.create_group([plate, burners], 'PLAIN', "Cooktop 4 bocas")


def table():
    legs = mesh("Pés", "Preto", *[('box', (x, y, 0), (x + 0.05, y + 0.05, 0.725)) for x, y in
                                  ((0.05, 0.05), (1.1, 0.05), (0.05, 0.7), (1.1, 0.7))])
    top = mesh("Tampo", "Carvalho", ('box', (0, 0, 0.725), (1.2, 0.8, 0.75)))
    bpy.context.view_layer.update()
    root = group.create_group([legs], 'PLAIN', "Mesa 120 x 80")
    convert.convert(top, legs)
    top.btm_aggregate.production_part = True
    return root


def vase():
    pot = mesh("Vaso", "Terracota", ('cyl', (0.15, 0.15, 0), 0.11, 0.3, 0.15))
    plant = mesh("Planta", "Folhagem", ('cyl', (0.15, 0.15, 0.3), 0.2, 0.45, 0.04))
    bpy.context.view_layer.update()
    return group.create_group([pot, plant], 'PLAIN', "Vaso com planta")


def frame_picture():
    border = mesh("Moldura", "Preto", ('box', (0, 0, 0), (0.6, 0.03, 0.025)), ('box', (0, 0, 0.775), (0.6, 0.03, 0.8)),
                  ('box', (0, 0, 0), (0.025, 0.03, 0.8)), ('box', (0.575, 0, 0), (0.6, 0.03, 0.8)))
    canvas = mesh("Tela", "Tela", ('box', (0.025, 0.01, 0.025), (0.575, 0.02, 0.775)))
    bpy.context.view_layer.update()
    return group.create_group([border, canvas], 'PLAIN', "Quadro 60 x 80")


ITEMS = (("porta-lisa-80", "Porta lisa 80", 'DOORS', door), ("janela-correr-120", "Janela de correr 120", 'WINDOWS',
                                                              window),
         ("cooktop-4-bocas", "Cooktop 4 bocas", 'COOKTOPS', cooktop), ("mesa-120x80", "Mesa 120 x 80", 'TABLES', table),
         ("vaso-com-planta", "Vaso com planta", 'DECOR', vase), ("quadro-60x80", "Quadro 60 x 80", 'DECOR', frame_picture))


def main():
    if Path(store.BUNDLED_DIR).exists():
        shutil.rmtree(store.BUNDLED_DIR)
    entries = []
    for item_id, name, category, build in ITEMS:
        for obj in list(bpy.context.scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        root = build()
        bpy.context.view_layer.update()
        item, errors = item_io.save(bpy.context, root, name, category, source=catalog.BUNDLED_SOURCE,
                                    license_text=LICENSE, folder=store.BUNDLED_DIR, item_id=item_id)
        if errors:
            raise SystemExit(f"{name}: {errors}")
        entries.append(item.entry)
        print("ITEM", item_id, item.entry.size_mm, item.entry.features)
    if store.check_bundled(entries):
        raise SystemExit("origem proibida na biblioteca embutida")


main()
