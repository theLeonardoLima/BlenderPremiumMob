"""Teste de fumaça da feature 005 com janela (T034): barra lateral única e conversa com a viewport.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    blender --factory-startup --enable-event-simulate --python tests/blender_005_viewport_smoke.py
(sem tela: `xvfb-run -a blender ...`)

Cobre: só o painel hospedeiro na aba (nenhum painel legado registrado); desenho de todas as seções com todos os grupos
abertos sem erro de Python; Selecionado abre sozinho ao selecionar e Construir lembra que estava recolhido; menu do
botão direito do balcão e da parede; linha de ações do item no HUD; prévia do ímã durante um G a 30 mm (aparece), a
80 mm (não aparece) e com Esc (some, nada gruda). Gera capturas da barra lateral na pasta temporária.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_types, hb_utils  # noqa: E402
from caffmob_draw.operators import viewport_hud  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.stick import magnet_preview  # noqa: E402
from caffmob_draw.ui import context_menu, layout_probe  # noqa: E402

FAILURES = []
DRAW_ERRORS = []
SHOTS = tempfile.mkdtemp(prefix="caffmob_005_")
_hook = sys.excepthook


def _record(exc_type, exc, tb):
    DRAW_ERRORS.append("".join(traceback.format_exception(exc_type, exc, tb))[-400:])
    _hook(exc_type, exc, tb)


sys.excepthook = _record


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = max((a for a in win.screen.areas if a.type == 'VIEW_3D'), key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def box_mesh(name, lo, hi, location):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(tuple(lo[i] if v.co[i] < 0 else hi[i] for i in range(3)))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    return obj


def select(ctx, obj):
    for o in ctx.view_layer.objects:
        o.select_set(False)
    ctx.view_layer.objects.active = obj
    if obj is not None:
        obj.select_set(True)


def redraw(ctx):
    for window in ctx.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def shot(ctx, name):
    win = ctx.window_manager.windows[0]
    with ctx.temp_override(window=win):
        bpy.ops.screen.screenshot(filepath=os.path.join(SHOTS, name))


def menu_ops(ctx):
    rec = layout_probe.Recorder()
    proxy = type('P', (), {'layout': layout_probe.Probe(rec)})()
    context_menu.draw_context_menu(proxy, ctx)
    return [(r['name'], r['args'].get('mode')) for r in rec.operators()]


def script():
    ctx = bpy.context
    env.clean_scene()
    win, area, region = view3d(ctx)
    win.event_simulate('ESC', 'PRESS', x=10, y=10)       # fecha a tela de boas-vindas
    win.event_simulate('ESC', 'RELEASE', x=10, y=10)
    area.spaces.active.show_region_ui = True
    yield 0.5
    ui = next(r for r in area.regions if r.type == 'UI')
    ui.active_panel_category = "CAFFMob Draw"

    # 1. Só o painel hospedeiro na aba.
    registered = [c for c in bpy.types.Panel.__subclasses__() if getattr(c, 'bl_category', '') == "CAFFMob Draw"
                  and getattr(c, 'is_registered', False) and getattr(c, 'bl_space_type', '') == 'VIEW_3D']
    names = sorted(getattr(c, 'bl_idname', c.__name__) for c in registered)
    check("só o painel hospedeiro na aba", names == ['BTM_PT_sidebar'], str(names))

    # Cena: parede, balcão, roupeiro-alvo para o ímã e um aéreo solto.
    wall = hb_types.GeoNodeWall()
    wall.create("Parede")
    wall.set_input('Length', 4.0)
    wall.set_input('Thickness', 0.15)
    wall.set_input('Height', 2.6)
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    base.obj.location = (0.5, -1.5, 0.0)
    placa = box_mesh("Lateral", (-0.5, -0.009, 0.0), (0.5, 0.009, 2.0), (6.0, -1.0, 0.0))
    aereo = tf.UpperCabinet()
    aereo.create("Aereo")
    hb_utils.run_calc_fix_until_stable(ctx, aereo.obj)
    from caffmob_draw.stick import magnet
    original_prefs = magnet.preferences
    magnet.preferences = lambda: (False, 0.05)                # a preparação não pode grudar o aéreo
    aereo.obj.location = (5.8, -1.009 - 0.030, 1.0)          # fundo a 30 mm da face −Y da lateral
    env.settle()
    yield 0.8                                                  # o assentar trata (sem ímã) e guarda a posição
    magnet.preferences = original_prefs

    # 2. Todas as seções e grupos abertos, desenho real sem erro.
    st = ctx.window_manager.btm_sidebar
    for prop in st.bl_rna.properties:
        if prop.identifier.startswith('open_'):
            setattr(st, prop.identifier, True)
    for obj in (None, wall.obj, base.obj):
        select(ctx, obj)
        redraw(ctx)
        yield 0.4
    shot(ctx, "barra_tudo_aberto.png")
    check("desenho real de todas as seções sem erro de Python", not DRAW_ERRORS, "\n".join(DRAW_ERRORS[:3]))

    # 3. Selecionado abre sozinho; Construir lembra que estava recolhido.
    st.open_selected = False
    st.open_build = False
    select(ctx, None)
    yield 0.3
    select(ctx, base.obj)
    redraw(ctx)
    yield 0.5
    check("Selecionado abre ao selecionar", st.open_selected)
    check("Construir continua recolhido", not st.open_build)
    shot(ctx, "barra_selecionado.png")

    # 4. Menu do botão direito: balcão com as ações; parede só com as dela.
    ops = menu_ops(ctx)
    wanted = {'caffmob.stick_to_face', 'caffmob.move_over_toggle', 'caffmob.cabinet_editor',
              'caffmob.check_collisions', 'caffmob.fronts_set_open', 'caffmob.set_insertion_plane'}
    check("menu do balcão com as ações frequentes", wanted <= {o for o, _m in ops}, str(ops))
    select(ctx, wall.obj)
    yield 0.2
    wall_ops = {o for o, _m in menu_ops(ctx)}
    check("menu da parede sem ações de item", not (wall_ops & {'caffmob.stick_to_face', 'caffmob.cabinet_editor'}),
          str(wall_ops))

    # 5. HUD: linha de ações do balcão.
    select(ctx, base.obj)
    yield 0.2
    with ctx.temp_override(window=win, area=area, region=region):
        placed = viewport_hud.compute_layout(ctx, area)
    item_buttons = [w for w, _r in placed if isinstance(w, viewport_hud._ItemActionButton)]
    labels = [w._label(ctx) for w in item_buttons]
    check("HUD mostra até 4 ações do item", 1 <= len(item_buttons) <= 4 and "Grudar" in labels, str(labels))

    # 6. Prévia do ímã durante um G a 30 mm; Esc cancela e nada gruda.
    select(ctx, aereo.obj)
    before = aereo.obj.matrix_world.translation.copy()
    cx, cy = region.x + region.width // 2, region.y + region.height // 2
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=cx, y=cy)
    yield 0.2
    win.event_simulate('G', 'PRESS', x=cx, y=cy)
    win.event_simulate('G', 'RELEASE', x=cx, y=cy)
    yield 0.3
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=cx + 1, y=cy)
    yield 0.3
    with ctx.temp_override(window=win, area=area, region=region):
        preview = magnet_preview.compute(ctx)
    check("prévia do ímã aparece a 30 mm", preview is not None and preview[0] == placa, str(preview and preview[0]))
    # Sem captura aqui: o operador de captura de tela encerraria o G antes do cancelamento.
    win.event_simulate('ESC', 'PRESS', x=cx + 1, y=cy)
    win.event_simulate('ESC', 'RELEASE', x=cx + 1, y=cy)
    yield 0.8
    with ctx.temp_override(window=win, area=area, region=region):
        after = magnet_preview.compute(ctx)
    check("prévia some ao cancelar", after is None)
    moved = (aereo.obj.matrix_world.translation - before).length
    check("nada gruda ao cancelar", not aereo.obj.btm_stick.is_stuck and moved < 1e-4,
          f"grudado={aereo.obj.btm_stick.is_stuck} deslocamento={moved:.6f}")

    # 7. A 80 mm (ímã de 50 mm) não há prévia.
    magnet.preferences = lambda: (False, 0.05)
    aereo.obj.location.y = -1.009 - 0.080
    env.settle()
    yield 0.8
    magnet.preferences = original_prefs
    win.event_simulate('G', 'PRESS', x=cx, y=cy)
    win.event_simulate('G', 'RELEASE', x=cx, y=cy)
    yield 0.3
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=cx + 1, y=cy)
    yield 0.3
    with ctx.temp_override(window=win, area=area, region=region):
        far = magnet_preview.compute(ctx)
    check("sem prévia a 80 mm", far is None)
    win.event_simulate('ESC', 'PRESS', x=cx + 1, y=cy)
    win.event_simulate('ESC', 'RELEASE', x=cx + 1, y=cy)
    yield 0.5
    print(f"capturas em {SHOTS}", flush=True)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_005_viewport_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
