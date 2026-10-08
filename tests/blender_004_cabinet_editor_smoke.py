"""Teste de fumaça da feature 004, incremento I3 (T058): Editor de Armário, com janela.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    blender --factory-startup --enable-event-simulate --python tests/blender_004_cabinet_editor_smoke.py
(sem tela: `xvfb-run -a blender ...`)

Para um módulo de cada biblioteca (frameless, face frame, closets, `btm`):
- abrir o editor, mudar a largura e trocar a frente de um vão; Ctrl+Z no editor desfaz a frente sem mexer no desfazer
  da cena; Cancelar devolve a mesma vista frontal e as mesmas medidas;
- abrir de novo, mudar a largura e Confirmar; um único Ctrl+Z na cena devolve o módulo de antes do editor (nenhum
  passo intermediário entrou na pilha do Blender);
- largura abaixo do mínimo dá `DIM-003` e impede Confirmar.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.cabinet_editor import bridge, elevation, props  # noqa: E402
from caffmob_draw.cabinet_editor import window as cew  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def key(win, kind, x, y, ctrl=False, shift=False):
    win.event_simulate(kind, 'PRESS', x=int(x), y=int(y), ctrl=ctrl, shift=shift)
    win.event_simulate(kind, 'RELEASE', x=int(x), y=int(y), ctrl=ctrl, shift=shift)


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def signature(ctx, name):
    root = bpy.data.objects[name]
    # As bibliotecas recriam as frentes com outro nome (sufixo .001): compara tipo e caixa, não o nome.
    parts = sorted((p.kind, tuple(round(v, 4) for v in p.lo + p.hi)) for p in bridge.parts(ctx, root))
    dims = tuple(round(v, 4) for v in bridge.read_state(root).dimensions)
    return dims, parts


def make_modules(ctx):
    env.clean_scene()
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    ff = tff.BaseFaceFrameCabinet()
    ff.create("FaceFrame")
    ff.obj.location.x = 3.0
    starter = tc.BaseClosetStarter()
    starter.create_starter("Roupeiro", bay_qty=2)
    starter.obj.location.x = 6.0
    tc.recalculate_closet_starter(starter.obj)
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.cabinet_builder(width=0.6)
    quick = ctx.object
    quick.location.x = 9.0
    env.settle()
    return [base.obj.name, ff.obj.name, starter.obj.name, quick.name]


def open_editor(ctx, name):
    root = bpy.data.objects[name]
    for obj in ctx.selected_objects:
        obj.select_set(False)
    root.select_set(True)
    ctx.view_layer.objects.active = root
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region, active_object=root, object=root):
        result = bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')
    return result


def editor_window(ctx):
    ewin, _area, ereg = cew.editor_area(ctx)
    return ewin, ereg


def first_opening(s):
    return next((p.name for p in s.parts if p.kind == elevation.OPENING), None)


def run_library(ctx, name):
    before = signature(ctx, name)
    check(f"{name}: abre o editor", open_editor(ctx, name) == {'FINISHED'})
    yield 1.2
    s = props.session()
    check(f"{name}: sessão e janela", s is not None and editor_window(ctx)[0] is not None)
    if s is None:
        return
    ewin, ereg = editor_window(ctx)
    mx, my = ereg.x + 30, ereg.y + 30
    ewin.event_simulate('MOUSEMOVE', 'NOTHING', x=mx, y=my)
    width0 = s.draft.current.dimensions[0]
    s.push('dimension', ('width', width0 + 0.1))
    yield 0.6
    check(f"{name}: largura aplicada", abs(s.draft.current.dimensions[0] - (width0 + 0.1)) < 1e-4,
          str(s.draft.current.dimensions))
    opening = first_opening(s)
    if opening is not None:
        s.selected = opening
        path = bridge.opening_of(s.root(), opening)
        front_before = bridge.read_state(s.root()).spec['openings'][0]['front']
        wanted = 'DOUBLE_DOORS' if front_before in ('OPEN', '') else 'OPEN'
        s.push('edit', ('FRONT', {'path': path, 'front': wanted, 'targets': [opening]}))
        yield 0.8
        front_after = bridge.read_state(s.root()).spec['openings'][0]['front']
        key(ewin, 'Z', mx, my, ctrl=True)
        yield 0.8
        front_undo = bridge.read_state(s.root()).spec['openings'][0]['front']
        check(f"{name}: Ctrl+Z no editor desfaz a frente", front_after == wanted and front_undo == front_before,
              f"{front_before} → {front_after} → {front_undo}")
    s.request = 'cancel'
    yield 1.0
    check(f"{name}: Cancelar fecha o editor", props.session() is None)
    after = signature(ctx, name)
    check(f"{name}: Cancelar devolve medidas e vista frontal", after == before,
          "" if after == before else f"{before[0]} → {after[0]}; "
          f"só antes: {sorted(set(before[1]) - set(after[1]))[:4]}; só depois: {sorted(set(after[1]) - set(before[1]))[:4]}")

    # Confirmar: um Ctrl+Z na cena volta ao módulo de antes do editor.
    open_editor(ctx, name)
    yield 1.2
    s = props.session()
    if s is None:
        check(f"{name}: reabre o editor", False)
        return
    s.push('dimension', ('width', width0 + 0.05))
    yield 0.6
    s.push('dimension', ('width', width0 + 0.15))
    yield 0.6
    s.push('dimension', ('width', 0.005))
    yield 0.6
    check(f"{name}: DIM-003 impede Confirmar", s.blocking() and any(m.code == 'DIM-003' for m in s.messages))
    s.push('dimension', ('width', width0 + 0.15))
    yield 0.6
    check(f"{name}: medida válida libera Confirmar", not s.blocking(), str([m.code for m in s.messages]))
    s.request = 'ok'
    yield 1.0
    confirmed = signature(ctx, name)
    check(f"{name}: Confirmar aplica", abs(confirmed[0][0] - round(width0 + 0.15, 4)) < 1e-3, str(confirmed[0]))
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    yield 0.8
    undone = signature(ctx, name)
    check(f"{name}: um Ctrl+Z na cena volta ao anterior", undone[0] == before[0], f"{before[0]} → {undone[0]}")


def script():
    ctx = bpy.context
    names = make_modules(ctx)
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo_push(message="Módulos de teste")
    yield 0.5
    for name in names:
        yield from run_library(ctx, name)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_004_cabinet_editor_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}",
          flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
