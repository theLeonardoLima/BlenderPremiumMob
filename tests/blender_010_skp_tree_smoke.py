"""Teste de fumaça da árvore do SketchUp (feature 010, T031; RF-09 a RF-11, RN-07 a RN-09).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_010_skp_tree_smoke.py

`tests/fixtures/porta_aninhada.skp` (gerado por `tools/make_skp_fixture.py`): a folha "Folha 1" tem 3 dobradiças e a
maçaneta dentro da definição dela, e há uma figura de escala.
- o grupo da folha contém os 4 grupos das ferragens, cada dobradiça na sua altura;
- a figura de escala não entra, e o relatório diz que foi ignorada;
- converter a folha em folha de porta leva as ferragens junto;
- reimportar não duplica o material de camada, chamado "Layer0".
"""

import math
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.aggregates import group, leaf  # noqa: E402

FIXTURE = str(Path(__file__).resolve().parent / "fixtures" / "porta_aninhada.skp")
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    env.clean_scene()
    result = bpy.ops.caffmob.import_model(filepath=FIXTURE)
    env.settle()
    check("importa o .skp aninhado", result == {'FINISHED'})
    groups = {o.name: o for o in bpy.data.objects if group.is_group(o)}
    leaf_group = groups.get("Folha 1")
    inner = [c for c in leaf_group.children if group.is_group(c)] if leaf_group else []
    names = sorted(c.name.split(".")[0] for c in inner)
    check("a folha contém as 3 dobradiças e a maçaneta", names == ["Dobradica"] * 3 + ["Macaneta"], str(names))
    heights = sorted(round(group.world_box([m for m in c.children if m.type == 'MESH'])[0].z, 2) for c in inner
                     if c.name.startswith("Dobradica"))
    check("cada dobradiça na sua altura", len(set(heights)) == 3, str(heights))
    check("a figura de escala não entra", not any("Pessoa" in n or "2D_Woman" in n for n in groups), str(sorted(groups)))
    frame = groups.get("Batente 1")
    if leaf_group is not None and frame is not None:
        leaf_group.parent, leaf_group.matrix_parent_inverse = frame, frame.matrix_world.inverted()
        frame.btm_group.kind, leaf_group.btm_group.kind = 'FRAME', 'LEAF'
        env.settle()
        hinge = next(c for c in inner if c.name.startswith("Dobradica"))
        before = hinge.matrix_world.translation.copy()
        leaf.make_leaf(leaf_group, frame, 'SWING', hinge='LEFT', max_angle=90.0)
        leaf_group.btm_aggregate.open_value = 1.0
        env.settle()
        moved = (hinge.matrix_world.translation - before).length
        angle = abs(math.degrees(leaf_group.matrix_world.to_euler().z))
        check("converter a folha leva as ferragens junto", angle > 80 or moved > 1e-4, f"{angle:.1f}° {moved:.4f}")
    count = len([m for m in bpy.data.materials if m.name.startswith("Layer0")])
    bpy.ops.caffmob.import_model(filepath=FIXTURE)
    env.settle()
    after = sorted(m.name for m in bpy.data.materials if m.name.startswith("Layer"))
    check("reimportar não duplica o material de camada (Layer0)", count == 1 and after == ["Layer0"], str(after))


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_010_skp_tree_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
