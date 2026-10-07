"""Reprodução com janela dos bugs #8 (Ctrl+Z no editor) e #9 (medida do trecho no painel)."""
import os, sys, traceback, types
from pathlib import Path
import bpy
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob")
import caffmob_draw as addon
addon.register()
type(bpy.context.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0), door_window_color=(0.3, 0.3, 0.3, 1.0))
from caffmob_draw.walls2d import apply, model, ops_editor, props, panels
from caffmob_draw.walls2d import window as w2d

def ev(win, kind, value='PRESS', x=0, y=0, ctrl=False, shift=False, char=''):
    kw = dict(x=int(x), y=int(y), ctrl=ctrl, shift=shift)
    if char: kw['unicode'] = char
    win.event_simulate(kind, value, **kw)

def tap(win, x, y):
    ev(win, 'MOUSEMOVE', 'NOTHING', x, y); yield 0.05
    ev(win, 'LEFTMOUSE', 'PRESS', x, y); ev(win, 'LEFTMOUSE', 'RELEASE', x, y)

class Rec:
    def __init__(self): self.props = []; self.labels = []
    def __getattr__(self, n):
        def f(*a, **k):
            if n == 'prop' and len(a) >= 2: self.props.append(a[1])
            if n == 'label': self.labels.append(k.get('text', ''))
            return self
        return f
    def __setattr__(self, k, v):
        if k in ('props', 'labels'): object.__setattr__(self, k, v)

def panel_content(ctx, earea, ui, ewin=None):
    rec = Rec()
    ewin = w2d.editor_area(ctx)[0]
    with ctx.temp_override(window=ewin, area=earea, region=ui):
        try:
            panels.BTM_PT_WallEditorSegment.draw(types.SimpleNamespace(layout=rec), bpy.context)
        except Exception as exc:
            return f"ERRO {exc!r}"
    return rec.props or rec.labels

def script():
    ctx = bpy.context
    for o in list(ctx.scene.objects): bpy.data.objects.remove(o, do_unlink=True)
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 1.5
    s = props.session(); ewin, earea, ereg = w2d.editor_area(ctx)
    ui = next(r for r in earea.regions if r.type == 'UI')
    print("ABERTO sel", s.selected, "tool", ctx.window_manager.btm_wall_editor.tool, "ui", ui.width, ui.height, "show_ui", earea.spaces.active.show_region_ui, flush=True)
    print("PAINEL ao abrir:", panel_content(ctx, earea, ui), flush=True)
    view = s.view
    chain = s.plan.chains[0]
    (a, b) = chain.endpoints(1)
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    p = view.to_screen(mid)
    s.selected = None
    yield from tap(ewin, ereg.x + p[0], ereg.y + p[1]); yield 0.3
    print("CLIQUE no trecho 1 -> sel", s.selected, "linha", s.line, flush=True)
    print("PAINEL depois do clique:", panel_content(ctx, earea, ui), flush=True)
    yield 0.5
    with ctx.temp_override(window=ewin, area=earea):
        bpy.ops.screen.screenshot_area(filepath="/tmp/claude-1000/-home-theleoinfo-www-BlenderToMob/885d8680-540f-422b-be2b-a2f95c2f8efd/scratchpad/editor_painel.png")
    with ctx.temp_override(window=ewin):
        bpy.ops.screen.screenshot(filepath="/tmp/claude-1000/-home-theleoinfo-www-BlenderToMob/885d8680-540f-422b-be2b-a2f95c2f8efd/scratchpad/editor_janela.png")
    print("PRINT ok", flush=True)
    st = ctx.window_manager.btm_wall_editor
    print("campo length", round(st.length, 4), "trecho", round(chain.face_length(1, s.line), 4), flush=True)
    # #8: mudar medida e Ctrl+Z
    before = model.plan_signature(s.plan)
    st.length = st.length + 0.5
    after = model.plan_signature(s.plan)
    print("medida mudou", before != after, flush=True)
    mx, my = ereg.x + 40, ereg.y + 40
    ev(ewin, 'MOUSEMOVE', 'NOTHING', mx, my); yield 0.05
    ev(ewin, 'Z', 'PRESS', mx, my, ctrl=True); ev(ewin, 'Z', 'RELEASE', mx, my, ctrl=True); yield 0.5
    s2 = props.session()
    print("CTRL+Z -> sessão viva", s2 is not None, "desfez", s2 is not None and model.plan_signature(s2.plan) == before, flush=True)
    if s2: s2.request = 'cancel'
    yield 1.0

_gen = script()
def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
    print("FIM", flush=True); os._exit(0)
bpy.app.timers.register(tick, first_interval=2.0)
