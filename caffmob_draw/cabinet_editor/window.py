"""Janela do Editor de Armário e o desenho da vista frontal (feature 004, T043; RF-02, D-20, D-23).

A janela é a mesma mecânica do Editor de Paredes (`canvas2d/window.py`): uma janela nova com um Image Editor sem
imagem, os painéis na aba "Editor de Armário" e um handler `POST_PIXEL` global que só desenha na área do editor.

O desenho mostra o módulo de frente (x, z): estrutura, vãos tracejados, prateleiras e divisórias, frentes por cima, o
componente selecionado destacado, os componentes com mensagem marcados em vermelho e as medidas do módulo.
"""

import bpy  # type: ignore

from ..canvas2d import draw
from ..canvas2d import window as _window
from ..canvas2d.view import View2D
from ..data import units
from ..data.i18n import tr
from . import elevation, props

_draw_handle = []

FILL = {
    elevation.STRUCTURE: (0.55, 0.42, 0.28, 0.55),
    elevation.SHELF: (0.62, 0.50, 0.34, 0.75),
    elevation.DIVIDER: (0.62, 0.50, 0.34, 0.75),
    elevation.FRONT: (0.82, 0.82, 0.86, 0.35),
    elevation.AGGREGATE: (0.35, 0.65, 0.95, 0.45),
    elevation.PART: (0.6, 0.6, 0.6, 0.4),
}
EDGE = (0.95, 0.95, 0.95, 0.85)
OPENING_EDGE = (0.6, 0.6, 0.65, 0.7)
SELECTED = (1.0, 0.75, 0.2, 1.0)
FLAGGED = (1.0, 0.3, 0.25, 1.0)
BACKGROUND = (0.13, 0.13, 0.14, 1.0)


def session():
    return props.session()


def editor_area(context):
    return _window.editor_area(context, session())


def is_editor_area(context):
    return _window.is_editor_area(context, session())


def open_editor(context):
    return _window.open_window(context, session(), tr("O Editor de Armário precisa de uma janela do Blender aberta."))


def focus_tab(area):
    return _window.focus_tab(area, props.EDITOR_CATEGORY)


def close_later(s):
    _window.close_later(s.window_ptr, s.area_ptr, s.restore_area_type)


def window_alive(context):
    return _window.window_alive(context, session())


def over_side_panel(area, x, y):
    return _window.over_side_panel(area, x, y)


def _rect(region, area):
    return (0.0, 0.0, _window.visible_width(area, region), float(region.height))


def ensure_view(region, area):
    """Vista 2D da área; reenquadra quando o tamanho da área ou do módulo muda."""
    s = session()
    rect = _rect(region, area)
    bounds = elevation.bounds(s.parts) or (0.0, 0.0, 1.0, 1.0)
    key = (rect, tuple(round(b, 4) for b in bounds))
    if s.view is None or getattr(s, 'view_key', None) != key:
        s.view = View2D(rect)
        s.view.fit(((bounds[0], bounds[1]), (bounds[2], bounds[3])), margin=0.18)
        s.view_key = key
    return s.view


def draw_editor(context):
    s = session()
    region = context.region
    if s is None or region is None:
        return
    view = ensure_view(region, context.area)
    flagged = {m.component for m in s.messages if m.component}
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), BACKGROUND)
    for part in elevation.draw_order(s.parts):
        x0, z0, x1, z1 = part.rect
        if part.kind == elevation.OPENING:
            a, b = view.to_screen((x0, z0)), view.to_screen((x1, z1))
            pts = []
            for p, q in (((a[0], a[1]), (b[0], a[1])), ((b[0], a[1]), (b[0], b[1])),
                         ((b[0], b[1]), (a[0], b[1])), ((a[0], b[1]), (a[0], a[1]))):
                pts += draw.dashed(p, q)
            draw.lines(sh, pts, OPENING_EDGE)
            continue
        color = FLAGGED if part.name in flagged else EDGE
        draw.box(sh, view, (x0, z0), (x1, z1), color, fill=FILL.get(part.kind, FILL[elevation.PART]))
    if s.selected:
        part = next((p for p in s.parts if p.name == s.selected), None)
        if part is not None:
            x0, z0, x1, z1 = part.rect
            r = draw.box(sh, view, (x0, z0), (x1, z1), SELECTED)
            draw.outline(sh, (r[0] - 2, r[1] - 2, r[2] + 4, r[3] + 4), SELECTED)
    draw.end()
    _labels(view, s)


def _labels(view, s):
    bounds = elevation.bounds(s.parts)
    if bounds is None:
        return
    x0, z0, x1, z1 = bounds
    width, height, depth = s.draft.current.dimensions
    bottom = view.to_screen(((x0 + x1) / 2.0, z0))
    label = units.format_value(width)
    draw.text(bottom[0] - draw.text_width(label) / 2.0, bottom[1] - 20, label)
    side = view.to_screen((x1, (z0 + z1) / 2.0))
    draw.text(side[0] + 8, side[1], units.format_value(height))
    title = "{}  —  {} × {} × {}".format(s.root_name, units.format_value(width), units.format_value(height),
                                         units.format_value(depth))
    top = view.to_screen((x0, z1))
    draw.text(top[0], top[1] + 16, title)
    status = tr("Rascunho alterado") if s.draft.dirty() else tr("Sem alterações")
    if s.blocking():
        status = tr("{} — corrija os erros para confirmar").format(status)
    draw.text(top[0], top[1] + 34, status, color=FLAGGED if s.blocking() else draw.COLORS['muted'])


def _draw():
    if is_editor_area(bpy.context):
        draw_editor(bpy.context)


def register():
    if not _draw_handle:
        _draw_handle.append(bpy.types.SpaceImageEditor.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _draw_handle:
        bpy.types.SpaceImageEditor.draw_handler_remove(_draw_handle.pop(), 'WINDOW')
