"""Teste de fumaça da feature 004, incremento I1 (T056): grudar em parede, painel e superfície plana.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_004_stick_smoke.py

Cobre: migração dos módulos que já estão na parede (frente e trás); espessura 150 → 200 mm com o aéreo de trás
encostado; grudar num painel e girar o painel; item movido para fora do plano volta a ele ao assentar; ímã ligado,
desligado e com outra distância; item fora da face; apagar o hospedeiro pelo operador e direto; desgrudar; salvar e
reabrir com o vínculo.
"""

import math
import os
import sys
import tempfile
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_types, hb_utils  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.stick import apply, frame, link, magnet, migrate  # noqa: E402

ctx = bpy.context
scene = ctx.scene
env.clean_scene()


def settle():
    """Atualiza a cena e roda o assentar (o temporizador não corre em segundo plano)."""
    env.settle()
    if apply._pending:
        apply._settle_timer()
    env.settle()


def box_mesh(name, lo, hi):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(tuple(lo[i] if v.co[i] < 0 else hi[i] for i in range(3)))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return obj


def resize_mesh(obj, lo, hi):
    for v in obj.data.vertices:
        v.co = Vector(tuple(lo[i] if v.co[i] < (lo[i] + hi[i]) / 2 else hi[i] for i in range(3)))
    obj.data.update()


def distance_to(item):
    fr, _ext = apply.face_of(item)
    return frame.params(fr, apply.item_corners(item, item.btm_stick.host))[2]


# 1. Parede de 4 m × 150 mm com um balcão na frente e um aéreo atrás (como o posicionamento frameless faz).
wall = hb_types.GeoNodeWall()
wall.create("Parede")
wall.set_input('Length', 4.0)
wall.set_input('Thickness', 0.15)
wall.set_input('Height', 2.6)
env.settle()
base = tf.BaseCabinet()
base.create("Balcao")
hb_utils.run_calc_fix_until_stable(ctx, base.obj)
base.obj.parent = wall.obj
base.obj.location = (0.5, 0.0, 0.0)
upper = tf.UpperCabinet()
upper.create("Aereo")
hb_utils.run_calc_fix_until_stable(ctx, upper.obj)
upper.obj.parent = wall.obj
width = upper.obj.dimensions.x
upper.obj.location = (1.0 + width, 0.15, 1.5)
upper.obj.rotation_euler = (0.0, 0.0, math.pi)
env.settle()
assert migrate.run(scene) == 2
assert scene.btm_settings.stick_migrated
assert base.obj.btm_stick.is_stuck and base.obj.btm_stick.face == 'NEG_Y'
assert upper.obj.btm_stick.is_stuck and upper.obj.btm_stick.face == 'POS_Y'
assert abs(distance_to(upper.obj)) < 1e-4 and abs(distance_to(base.obj)) < 1e-4
assert migrate.run(scene) == 0, "idempotente"
assert link.face_label(upper.obj).endswith("trás"), link.face_label(upper.obj)
world_before = base.obj.matrix_world.copy()

# 2. A parede engrossa: o aéreo de trás continua encostado; o balcão da frente não se move.
wall.set_input('Thickness', 0.20)
settle()
y_back = min(c[1] for c in apply.item_corners(upper.obj, wall.obj))
assert abs(y_back - 0.20) <= 1e-4, y_back
assert (base.obj.matrix_world.translation - world_before.translation).length < 1e-6
for t in (0.10, 0.12, 0.18, 0.25, 0.15):
    wall.set_input('Thickness', t)
    settle()
assert abs(min(c[1] for c in apply.item_corners(upper.obj, wall.obj)) - 0.15) <= 1e-4

# 2b. O aéreo vai parar do outro lado da parede (como quando o editor de paredes inverte a direção): o vínculo
# passa para a face da frente em vez de puxá-lo através da parede.
depth = upper.obj.dimensions.y
upper.obj.location.y = -depth - 0.001        # girado 180°: o corpo vai de y a y + profundidade
settle()
assert upper.obj.btm_stick.face == 'NEG_Y', upper.obj.btm_stick.face
assert max(c[1] for c in apply.item_corners(upper.obj, wall.obj)) <= 0.0 + 1e-6
upper.obj.location.y = 0.15
settle()
assert upper.obj.btm_stick.face == 'POS_Y', upper.obj.btm_stick.face

# 3. Grudar um nicho na lateral (+X) de um painel de 18 mm e girar o painel.
panel = box_mesh("Painel", (0.0, -0.3, 0.0), (0.018, 0.3, 2.0))
panel.location = (3.0, -1.5, 0.0)
nicho = box_mesh("Nicho", (-0.15, -0.1, -0.15), (0.15, 0.1, 0.15))
nicho.location = (3.4, -1.5, 1.0)
env.settle()
host, face = link.stick(nicho, panel, Vector((3.018, -1.5, 1.2)), Vector((1.0, 0.0, 0.0)))
assert host == panel and face == 'POS_X' and nicho.parent == panel
assert abs(distance_to(nicho)) < 1e-6
assert "Painel" in link.face_label(nicho)
panel.rotation_euler.z = math.radians(90)
settle()
assert abs(distance_to(nicho)) < 1e-6
assert abs(nicho.matrix_world.translation.y - (panel.matrix_world @ Vector((0.018, 0, 0))).y) < 0.2

# 4. Mover o nicho para fora do plano (como o G nativo): ao assentar, volta à face no lugar em que foi solto.
nicho.btm_stick.u                                                    # noqa: B018
u_before = nicho.btm_stick.u
offset = panel.matrix_world.to_3x3() @ Vector((0.05, 0.0, 0.10))     # 5 cm para fora e 10 cm para cima (local)
nicho.matrix_world.translation += offset
settle()
assert abs(distance_to(nicho)) < 1e-6
assert abs(nicho.btm_stick.u - u_before) > 0.09 or abs(nicho.btm_stick.v) > 0, "a posição no plano segue o solto"

# 5. Ímã: um balcão solto com o fundo a 30 mm da face −Y de uma placa gruda nela ao assentar.
placa = box_mesh("Placa", (-0.5, -0.009, 0.0), (0.5, 0.009, 2.0))
placa.location = (6.0, -1.0, 0.0)
livre = tf.BaseCabinet()
livre.create("Livre")
hb_utils.run_calc_fix_until_stable(ctx, livre.obj)
env.settle()
apply._pending.clear()
_original_prefs = magnet.preferences
magnet.preferences = lambda: (False, 0.05)
livre.obj.location = (5.8, -1.009 - 0.030, 0.0)
settle()
assert not livre.obj.btm_stick.is_stuck, "ímã desligado"
magnet.preferences = lambda: (True, 0.02)
livre.obj.location.x += 0.001
settle()
assert not livre.obj.btm_stick.is_stuck, "30 mm > 20 mm"
magnet.preferences = _original_prefs
livre.obj.location.x += 0.001
settle()
assert livre.obj.btm_stick.is_stuck and livre.obj.btm_stick.host == placa, "ímã de 50 mm"
assert abs(distance_to(livre.obj)) < 1e-4

# 6. A placa encolhe e o balcão fica fora da face: continua no lugar, com o aviso.
where = livre.obj.matrix_world.translation.copy()
resize_mesh(placa, (-0.5, -0.009, 1.5), (0.5, 0.009, 2.0))
settle()
assert livre.obj.btm_stick.out_of_face and livre.obj.btm_stick.is_stuck
assert (livre.obj.matrix_world.translation - where).length < 1e-6

# 7. Apagar o hospedeiro pelo operador: o balcão fica no mesmo lugar, sem vínculo.
for obj in scene.objects:
    obj.select_set(False)
placa.select_set(True)
ctx.view_layer.objects.active = placa
assert bpy.ops.caffmob.delete_with_aggregates('EXEC_DEFAULT') == {'FINISHED'}
assert "Placa" not in bpy.data.objects
assert not livre.obj.btm_stick.is_stuck and livre.obj.parent is None
assert (livre.obj.matrix_world.translation - where).length < 1e-6

# 8. Apagar direto (sem o operador): o handler solta o item no lugar.
outro = box_mesh("Outro", (-0.2, -0.009, 0.0), (0.2, 0.009, 1.0))
outro.location = (8.0, 0.0, 0.0)
caixa = box_mesh("Caixa", (-0.1, -0.1, -0.1), (0.1, 0.1, 0.1))
caixa.location = (8.0, -0.3, 0.5)
env.settle()
link.stick(caixa, outro, Vector((8.0, -0.009, 0.5)), Vector((0.0, -1.0, 0.0)))
env.settle()
spot = caixa.matrix_world.translation.copy()
bpy.data.objects.remove(outro, do_unlink=True)
apply.invalidate()
settle()
assert not caixa.btm_stick.is_stuck
assert (caixa.matrix_world.translation - spot).length < 1e-6, (caixa.matrix_world.translation, spot)

# 9. Desgrudar: o nicho fica e não acompanha mais o painel.
spot = nicho.matrix_world.translation.copy()
assert link.release(nicho)
assert nicho.parent is None and (nicho.matrix_world.translation - spot).length < 1e-6
panel.location.x += 1.0
settle()
assert (nicho.matrix_world.translation - spot).length < 1e-6

# 10. Salvar e reabrir: o vínculo do aéreo continua e a parede ainda o leva.
path = os.path.join(tempfile.mkdtemp(), "grudar.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
aereo = bpy.data.objects["Aereo"]
parede = bpy.data.objects["Parede"]
assert aereo.btm_stick.is_stuck and aereo.btm_stick.host == parede and aereo.btm_stick.face == 'POS_Y'
hb_types.GeoNodeWall(parede).set_input('Thickness', 0.22)
settle()
assert abs(min(c[1] for c in apply.item_corners(aereo, parede)) - 0.22) <= 1e-4

print("OK blender_004_stick_smoke")
