"""Teste de fumaça da biblioteca de objetos (feature 009, T038; RF-06 a RF-10).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_009_library_smoke.py

- os 6 itens embutidos aparecem nas categorias, sem origem "3D Warehouse";
- inserir a Porta lisa 80: a folha gira até 90°;
- inserir a Mesa 120 x 80: o tampo entra no plano de corte com 1200 × 800 × 25 mm;
- retexturizar o tampo com um acabamento do plugin e com uma imagem própria (projeção em caixa, escala real);
- acrescentar a porta e um OBJ à biblioteca do usuário; nome repetido renomeia ou substitui;
- reabrir noutro Blender (mesma pasta do usuário) e inserir a porta salva: a folha continua de giro;
- remover um item do usuário; um embutido não sai.
"""

import math
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

USER = tempfile.mkdtemp(prefix="caffmob_009_user_")
os.environ.setdefault("CAFFMOB_TEST_USER_DIR", USER)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.cutting import part_extractor  # noqa: E402
from caffmob_draw.object_library import item_io, ops, retexture, store  # noqa: E402

FAILURES = []
SUBPROCESS = os.environ.get("CAFFMOB_009_SECOND") == "1"


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def key_of(name, user=False):
    items, _w = item_io.all_items()
    item = next(i for i in items if i.entry.name == name and i.user == user)
    return ops.item_key(item)


def leaf_of(root):
    return next(o for o in [root] + list(root.children_recursive)
                if getattr(o, 'btm_aggregate', None) is not None and o.btm_aggregate.kind == 'LEAF')


def swing_degrees(obj):
    obj.btm_aggregate.open_value = 0.0
    bpy.context.view_layer.update()
    closed = obj.matrix_world.to_euler().z
    obj.btm_aggregate.open_value = 1.0
    bpy.context.view_layer.update()
    return abs(math.degrees(obj.matrix_world.to_euler().z - closed))


def png(path):
    import struct
    import zlib
    raw = b"".join(b"\x00" + bytes((150, 100, 60)) * 4 for _ in range(4))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def second_blender():
    """No 2º Blender: a porta salva pelo usuário volta com a folha de giro (cena limpa: o cubo padrão barraria a folha)."""
    env.clean_scene()
    result = bpy.ops.caffmob.object_insert(key=key_of("Porta copiada", user=True))
    root = bpy.context.view_layer.objects.active
    check("2º Blender: a porta salva é inserida", result == {'FINISHED'} and root is not None)
    lf = leaf_of(root)
    degrees = swing_degrees(lf)
    check("2º Blender: a folha continua de giro até 90°", abs(degrees - 90.0) < 1.0,
          f"{degrees:.1f}° {lf.name} contato={lf.btm_aggregate.contact_name!r} {[o.name for o in item_io.tree(root)]}")


def main():
    env.clean_scene()
    items, warnings = item_io.all_items()
    bundled = [i for i in items if not i.user]
    check("6 itens embutidos, sem avisos", len(bundled) == 6 and not warnings, f"{len(bundled)} {warnings}")
    check("categorias dos embutidos", {i.entry.category for i in bundled} == {'DOORS', 'WINDOWS', 'COOKTOPS',
                                                                              'TABLES', 'DECOR'})
    check("nenhum embutido do 3D Warehouse", store.check_bundled([i.entry for i in bundled]) == [])

    bpy.context.scene.cursor.location = (2.0, 0.0, 0.0)
    result = bpy.ops.caffmob.object_insert(key=key_of("Porta lisa 80"))
    door = bpy.context.view_layer.objects.active
    check("insere a porta no cursor 3D", result == {'FINISHED'} and door is not None
          and abs(door.location.x - 2.0) < 1e-6)
    check("a folha da porta gira até 90°", abs(swing_degrees(leaf_of(door)) - 90.0) < 1.0)
    leaf_of(door).btm_aggregate.open_value = 0.0

    bpy.context.scene.cursor.location = (5.0, 0.0, 0.0)
    bpy.ops.caffmob.object_insert(key=key_of("Mesa 120 x 80"))
    table = bpy.context.view_layer.objects.active
    parts, _bad = part_extractor.extract_production_parts(bpy.context)
    tops = [p for p in parts if p.name.startswith("Tampo")]
    dims = sorted((round(tops[0].height), round(tops[0].width), round(tops[0].thickness))) if tops else None
    check("o tampo da mesa entra no plano de corte", dims == [25, 800, 1200], str(dims))

    top = next(o for o in item_io.tree(table) if o.name.startswith("Tampo"))
    finish = next(iter(retexture.library_materials()), None)
    changed = retexture.apply_finish([top], finish) if finish else 0
    check("acabamento do plugin no tampo", changed == 1 and top.data.materials[0].name == finish, str(finish))
    image = os.path.join(USER, "madeira.png")
    png(image)
    changed = retexture.apply_image([top], image, 600.0)
    mat = top.data.materials[0]
    tex = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'), None)
    mapping = next((n for n in mat.node_tree.nodes if n.type == 'MAPPING'), None)
    check("imagem própria em escala real (caixa)", changed == 1 and tex is not None and tex.projection == 'BOX'
          and mapping is not None and abs(mapping.inputs['Scale'].default_value[0] - 1 / 0.6) < 1e-6, mat.name)
    check("a mesma imagem e tamanho reaproveitam o material", retexture.image_material(image, 600.0) == mat)

    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    door.select_set(True)
    bpy.context.view_layer.objects.active = door
    result = bpy.ops.caffmob.object_library_add(name="Porta copiada", category='DOORS', source="Teste",
                                                license_text="Uso próprio")
    check("acrescenta a porta à biblioteca do usuário", result == {'FINISHED'}
          and "Porta copiada" in item_io.existing_names('DOORS'))
    obj_path = os.path.join(USER, "caixa.obj")
    bpy.ops.mesh.primitive_cube_add(size=0.3)
    cube = bpy.context.active_object
    bpy.ops.wm.obj_export(filepath=obj_path, export_selected_objects=True, export_materials=False)
    bpy.data.objects.remove(cube, do_unlink=True)
    for name, dup in (("Meu teste", 'RENAME'), ("Meu teste", 'RENAME'), ("Meu teste", 'REPLACE')):
        bpy.ops.caffmob.object_library_add(name=name, category='DECOR', filepath=obj_path, duplicate=dup)
    names = sorted(item_io.existing_names('DECOR'))
    check("OBJ acrescentado; repetido renomeia e substitui", names == ["Meu teste", "Meu teste 2"], str(names))

    path = os.path.join(USER, "projeto.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    run = subprocess.run([bpy.app.binary_path, "--background", "--factory-startup", "--python-exit-code", "1",
                          "--python", __file__], capture_output=True, text=True, timeout=600,
                         env=dict(os.environ, CAFFMOB_TEST_USER_DIR=USER, CAFFMOB_009_SECOND="1"))
    print(run.stdout[-1500:])
    check("2º Blender rodou", run.returncode == 0, run.stderr[-800:])

    result = bpy.ops.caffmob.object_library_remove(key=key_of("Meu teste 2", user=True))
    check("remove um item do usuário", result == {'FINISHED'} and "Meu teste 2" not in item_io.existing_names('DECOR'))
    try:
        bpy.ops.caffmob.object_library_remove(key=key_of("Quadro 60 x 80"))
        removed = "Quadro 60 x 80" not in [i.entry.name for i in item_io.all_items()[0]]
    except RuntimeError:
        removed = False
    check("um item embutido não sai", not removed)


try:
    second_blender() if SUBPROCESS else main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_009_library_smoke{' (2º)' if SUBPROCESS else ''}: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
