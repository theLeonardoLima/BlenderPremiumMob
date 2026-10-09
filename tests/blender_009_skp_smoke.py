"""Teste de fumaça do SketchUp (feature 009, T039; RF-11, RF-12, RN-13, RN-14).

Roda em segundo plano, em qualquer plataforma (o leitor é o OpenSKP, Python puro, pelas wheels da extensão):
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_009_skp_smoke.py

- `tests/fixtures/porta_teste.skp` (gerado por `tools/make_skp_fixture.py`) entra pelo "Importar modelo" com os grupos
  "Batente 1" e "Folha 1", em pé e na escala do arquivo (batente 863,6 × 2133,6 mm), com os materiais "Branco" e
  "Madeira" e a imagem da textura carregada e empacotada;
- a folha importada vira folha de giro e abre até 90°;
- um `.skp` corrompido não cria nada e o relatório diz o motivo e a alternativa.
"""

import math
import os
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.aggregates import group, leaf  # noqa: E402

FIXTURE = str(Path(__file__).resolve().parent / "fixtures" / "porta_teste.skp")
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    env.clean_scene()
    result = bpy.ops.caffmob.import_model(filepath=FIXTURE)
    env.settle()
    groups = {o.name: o for o in bpy.data.objects if group.is_group(o)}
    check("importa o .skp", result == {'FINISHED'}, str(result))
    check("grupos com os nomes das instâncias", {"Batente 1", "Folha 1"} <= set(groups), str(sorted(groups)))
    frame = groups.get("Batente 1")
    meshes = [o for o in frame.children if o.type == 'MESH'] if frame else []
    dims = tuple(round(v * 1000, 1) for v in meshes[0].dimensions) if meshes else None
    check("em pé e na escala do arquivo", dims == (863.6, 38.1, 2133.6), str(dims))
    used = {m.name for o in bpy.data.objects if o.type == 'MESH' for m in o.data.materials if m}
    check("materiais com os nomes do SketchUp", {"Branco", "Madeira"} <= used, str(sorted(used)))
    wood = bpy.data.materials.get("Madeira")
    images = [n.image for n in wood.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image] if wood else []
    check("textura carregada e empacotada", bool(images) and images[0].packed_file is not None
          and images[0].size[0] > 0, str([i.name for i in images]))

    sash = groups.get("Folha 1")
    if frame is not None and sash is not None:
        sash.parent, sash.matrix_parent_inverse = frame, frame.matrix_world.inverted()
        frame.btm_group.kind, sash.btm_group.kind = 'FRAME', 'LEAF'
        env.settle()
        leaf.make_leaf(sash, frame, 'SWING', hinge='LEFT', max_angle=90.0)
        sash.btm_aggregate.open_value = 1.0
        env.settle()
        angle = abs(math.degrees(sash.matrix_world.to_euler().z))
        check("a folha do SketchUp vira folha de giro e abre até 90°", abs(angle - 90.0) < 1.0, f"{angle:.1f}°")

    before = set(bpy.data.objects)
    bad = os.path.join(tempfile.mkdtemp(), "quebrado.skp")
    Path(bad).write_bytes(b"isto nao e um sketchup")
    try:
        result = bpy.ops.caffmob.import_model(filepath=bad)
        message = ""
    except RuntimeError as exc:                   # o relatório de erro vira exceção no modo de script
        result, message = {'CANCELLED'}, str(exc)
    check("arquivo corrompido não cria nada", result == {'CANCELLED'} and set(bpy.data.objects) == before)
    check("e diz o motivo e a alternativa", "SketchUp" in message and "glTF" in message, message[:160])


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_009_skp_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
