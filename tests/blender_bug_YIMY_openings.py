"""Reprodução e regressão do BUG-20261007-YIMY: porta e janela saem da parede quando o editor reaplica a parede.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_YIMY_openings.py
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_types  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context
METHODS = ('create_placed_object', 'set_position_on_wall', 'get_placed_object', 'get_placed_object_width',
           'set_placed_object_width', 'get_placed_object_height', 'set_placed_object_height',
           'set_placed_object_depth', 'get_two_point_z_offset')
CONFIG = ('OBJECT_NAME', 'OBJECT_LABEL', 'BP_FLAG', 'MENU_ID', 'WIDTH_PROP_NAME', 'HEIGHT_PROP_NAME',
          'Z_OFFSET_PROP_NAME', 'TEXT_KIND', 'TEXT_NAME', 'HAS_SWING', 'SWING_LIST', 'INITIAL_SWING_INPUTS', 'OPENING_KIND')


def placer(op_class):
    """Os métodos do operador modal do botão, sem o modal (mesmo caminho de criação e de posição)."""
    attrs = {name: getattr(op_class, name) for name in METHODS + CONFIG}
    return type('Placer', (dw.WallObjectPlacementMixin,), attrs)()


def place(op_class, wall_obj, x):
    op = placer(op_class)
    op.init_placement(ctx)
    op.placed_obj = None
    op.init_two_point_state()
    op.create_placed_object(ctx)
    op.selected_wall = wall_obj
    op.hit_location = wall_obj.matrix_world @ Vector((x, 0.0, 0.0))
    op.set_position_on_wall()
    if op.placed_obj.obj in op.placement_objects:
        op.placement_objects.remove(op.placed_obj.obj)
    op.delete_placement_dimensions()
    op.cut_wall(wall_obj, op.placed_obj.obj)
    env.settle()
    return op.placed_obj.obj


def span(obj, ref):
    """Caixa da malha avaliada de `obj` nos eixos de `ref` (None = mundo), arredondada ao mm."""
    ev = obj.evaluated_get(ctx.evaluated_depsgraph_get())
    m = obj.matrix_world if ref is None else ref.matrix_world.inverted() @ obj.matrix_world
    pts = [m @ v.co for v in ev.to_mesh().vertices]
    ev.to_mesh_clear()
    return tuple((round(min(p[i] for p in pts), 3), round(max(p[i] for p in pts), 3)) for i in range(3))


def through(wall, opening):
    """O raio no meio do vão, de uma face à outra da parede, passa sem bater na parede."""
    cage = hb_types.GeoNodeCage(opening)
    center = Vector((cage.get_input('Dim X') / 2.0, 0.0, cage.get_input('Dim Z') / 2.0))
    local = wall.matrix_world.inverted() @ (opening.matrix_world @ center)
    start = wall.matrix_world @ Vector((local.x, -1.0, local.z))
    end = wall.matrix_world @ Vector((local.x, 2.0, local.z))
    opening.hide_set(True)
    hit, _loc, _n, _i, obj, _m = ctx.scene.ray_cast(ctx.evaluated_depsgraph_get(), start, (end - start).normalized(),
                                                    distance=3.0)
    opening.hide_set(False)
    return not (hit and obj == wall)


def along(obj, axis):
    """Vão no mundo, medido ao longo da linha da parede (`axis` fixo)."""
    ev = obj.evaluated_get(ctx.evaluated_depsgraph_get())
    values = [(obj.matrix_world @ v.co).dot(axis) for v in ev.to_mesh().vertices]
    ev.to_mesh_clear()
    return round(min(values), 3), round(max(values), 3)


def swing(door):
    child = next(c for c in door.children if 'Door Swing' in c.name)
    node = hb_types.GeoNodeObject(child)
    return node.get_input('Swing Inside'), node.get_input('Is Left')


def inside(wall, opening, thickness):
    (_x0, _x1), (y0, y1), _z = span(opening, wall)
    return abs(y0) < 1e-3 and abs(y1 - thickness) < 1e-3 and through(wall, opening)


def flip(plan):
    chain = plan.chains[0]
    chain.side = 'LEFT' if chain.side == 'RIGHT' else 'RIGHT'
    apply.apply_plan(ctx, plan)
    env.settle()


def room():
    env.clean_scene()
    plan = model.WallPlan([model.rectangle(4.0, 3.0)])
    apply.apply_plan(ctx, plan)
    env.settle()
    walls = sorted((o for o in ctx.scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)
    return plan, walls[0]


# 1. Reprodução: Direção trocada no editor → a porta continua no vão, dentro da espessura, e o arco do mesmo lado.
plan, wall = room()
door = place(dw.home_builder_doors_windows_OT_place_door, wall, 1.0)
assert inside(wall, door, 0.15), span(door, wall)
axis, before = wall.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0)), swing(door)
gap = along(door, axis)
flip(plan)
assert door.parent == wall and inside(wall, door, 0.15), span(door, wall)
assert along(door, axis) == gap, (along(door, axis), gap)
assert swing(door) == (not before[0], not before[1]), (swing(door), before)

# 2. Reprodução: espessura 0,15 → 0,25 no editor → a porta acompanha e o furo atravessa.
plan, wall = room()
door = place(dw.home_builder_doors_windows_OT_place_door, wall, 1.0)
for seg in plan.chains[0].segments:
    seg.thickness = 0.25
apply.apply_plan(ctx, plan)
env.settle()
assert inside(wall, door, 0.25), span(door, wall)

# 3. Regressão: janela (peitoril) e porta dupla, Direção trocada duas vezes → voltam ao lugar e ao arco de origem.
plan, wall = room()
window = place(dw.home_builder_doors_windows_OT_place_window, wall, 0.3)
double = place(dw.home_builder_doors_windows_OT_place_double_door, wall, 1.6)
origin = {o.name: (span(o, None), o.location.z) for o in (window, double)}
double_swing = swing(double)
flip(plan)
for obj in (window, double):
    assert inside(wall, obj, 0.15), (obj.name, span(obj, wall))
    assert abs(obj.location.z - origin[obj.name][1]) < 1e-6, obj.name
flip(plan)
for obj in (window, double):
    assert span(obj, None) == origin[obj.name][0], (obj.name, span(obj, None), origin[obj.name][0])
    assert inside(wall, obj, 0.15), obj.name
assert swing(double) == double_swing

# 4. Regressão: um módulo filho da parede continua parado no mundo quando a Direção vira.
plan, wall = room()
module = bpy.data.objects.new("Modulo", bpy.data.meshes.new("Modulo"))
ctx.collection.objects.link(module)
module.parent = wall
module.location = (0.5, 0.2, 0.0)
env.settle()
matrix = module.matrix_world.copy()
flip(plan)
assert all(abs(a - b) < 1e-5 for ra, rb in zip(module.matrix_world, matrix) for a, b in zip(ra, rb))

print("blender_bug_YIMY_openings: OK")
