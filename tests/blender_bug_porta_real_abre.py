"""Regressão: abrir a porta real pela inspeção (Abrir/Fechar Frentes, clique na folha) gira a folha real, e não uma
folha cinza criada pela "porta de ambiente" da 005 dentro da caixa.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_porta_real_abre.py
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.inspection import fronts, room_door_leaf  # noqa: E402
from caffmob_draw.openings import sync  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def real_leaves(cage):
    return [o for o in cage.btm_opening_real.assembly.children_recursive
            if o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF']


def gray_leaves(cage):
    return [o for o in cage.children_recursive if o.get(room_door_leaf.LEAF_TAG)]


try:
    env.clean_scene()
    for kind, x in (('DOOR', 0.0), ('DOUBLE_DOOR', 6.0)):
        cage = oe.make_cage(kind, location=(x, 0.0, 0.0))
        sync.sync(ctx, cage, force=True)
        env.settle()
        sashes = real_leaves(cage)
        body = next(o for o in sashes[0].children_recursive if o.type == 'MESH')
        front = fronts.front_for_object(body, ctx.scene)
        check(f"{kind}: o clique na folha real acha a folha real",
              front is not None and front.library == 'AGGREGATE', getattr(front, 'library', None))
        all_fronts = [f for f in fronts.iter_fronts(ctx.scene) if f.module_root == cage or f.obj == cage]
        check(f"{kind}: a caixa não vira porta de ambiente", all(f.library != 'ROOM' for f in all_fronts),
              [f.library for f in all_fronts])
        for f in fronts.iter_fronts(ctx.scene):
            f.commit(f.open_value(90.0))
        env.settle()
        check(f"{kind}: a folha real abriu", all(s.btm_aggregate.open_value > 0.5 for s in sashes),
              [round(s.btm_aggregate.open_value, 3) for s in sashes])
        check(f"{kind}: nenhuma folha cinza criada", not gray_leaves(cage), [o.name for o in gray_leaves(cage)])

    # Arquivo antigo: a porta de ambiente já tinha criado a folha cinza; a porta real a remove ao montar.
    cage = oe.make_cage('DOOR', location=(12.0, 0.0, 0.0))
    for spec, pivot in room_door_leaf.ensure_leaves(cage):
        pivot.rotation_euler.z = 1.0
    check("antigo: folha cinza existe antes da montagem", bool(gray_leaves(cage)))
    sync.sync(ctx, cage, force=True)
    check("antigo: folha cinza removida ao montar a porta real", not gray_leaves(cage),
          [o.name for o in gray_leaves(cage)])
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHOU " + ", ".join(FAILURES) if FAILURES else "TUDO OK", flush=True)
sys.exit(1 if FAILURES else 0)
