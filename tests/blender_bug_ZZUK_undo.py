"""Reprodução e regressão do BUG-20261007-ZZUK com janela: Ctrl+Z dentro do editor de paredes.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    blender --factory-startup --enable-event-simulate --python tests/blender_bug_ZZUK_undo.py
"""

import os
import sys
import traceback
import types
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
type(bpy.context.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0), door_window_color=(0.3, 0.3, 0.3, 1.0))

from caffmob_draw.walls2d import apply, model, props  # noqa: E402
from caffmob_draw.walls2d import window as w2d  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def key(win, kind, x, y, ctrl=False, shift=False):
    win.event_simulate(kind, 'PRESS', x=int(x), y=int(y), ctrl=ctrl, shift=shift)
    win.event_simulate(kind, 'RELEASE', x=int(x), y=int(y), ctrl=ctrl, shift=shift)


def tap(win, x, y):
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=int(x), y=int(y))
    yield 0.05
    win.event_simulate('LEFTMOUSE', 'PRESS', x=int(x), y=int(y))
    win.event_simulate('LEFTMOUSE', 'RELEASE', x=int(x), y=int(y))


def script():
    ctx = bpy.context
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 1.5
    s = props.session()
    ewin, _earea, ereg = w2d.editor_area(ctx)
    mx, my = ereg.x + 40, ereg.y + 40
    ewin.event_simulate('MOUSEMOVE', 'NOTHING', x=mx, y=my)
    yield 0.1

    # 1. Reprodução: mudar o comprimento pelo painel e Ctrl+Z volta a medida; Ctrl+Shift+Z refaz.
    s.selected, s.line = (0, 0), model.INNER
    state = ctx.window_manager.btm_wall_editor
    original = round(state.length, 6)
    state.length = original + 0.5
    ewin.event_simulate('MOUSEMOVE', 'NOTHING', x=mx + 2, y=my)
    yield 0.1
    key(ewin, 'Z', mx, my, ctrl=True)
    yield 0.3
    s = props.session()
    check("Ctrl+Z desfaz a medida mudada no painel", s is not None and round(s.plan.chains[0].length(0), 6) == original,
          str(s and s.plan.chains[0].length(0)))
    key(ewin, 'Z', mx, my, ctrl=True, shift=True)
    yield 0.3
    check("Ctrl+Shift+Z refaz", s is not None and round(s.plan.chains[0].length(0), 6) == round(original + 0.5, 6),
          str(s and s.plan.chains[0].length(0)))

    # 2. Reprodução: desenhar 2 trechos a lápis e 2× Ctrl+Z apaga os dois.
    state.tool = 'DRAW'
    view = s.view

    def scr(pt):
        p = view.to_screen(pt)
        return ereg.x + p[0], ereg.y + p[1]

    chains_before = len(s.plan.chains)
    for pt in ((1.0, 1.0), (2.0, 1.0), (2.0, 2.0)):
        yield from tap(ewin, *scr(pt))
        yield 0.15
    drawn = s.plan.chains[-1].segment_count() if len(s.plan.chains) > chains_before else 0
    key(ewin, 'ESC', mx, my)
    yield 0.2
    key(ewin, 'Z', mx, my, ctrl=True)
    yield 0.2
    key(ewin, 'Z', mx, my, ctrl=True)
    yield 0.3
    s = props.session()
    left = s.plan.chains[-1].segment_count() if s and len(s.plan.chains) > chains_before else 0
    check("2× Ctrl+Z apaga os 2 trechos desenhados", drawn == 2 and left == 0, f"desenhados={drawn} restam={left}")
    check("o editor continua aberto e o 3D não mudou", s is not None and
          sum(1 for o in ctx.scene.objects if o.get('IS_WALL_BP')) == 4)
    if s is not None:
        s.request = 'cancel'
    yield 1.0


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_bug_ZZUK_undo: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
