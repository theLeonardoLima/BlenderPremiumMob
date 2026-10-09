"""Aviso com as medidas do elemento tocado, na parte de baixo da viewport.

Ao selecionar um objeto (porta, parede, módulo, grupo de peças ou qualquer outro), mostra por alguns segundos
"<tipo> <nome>  L … × A … × P …" com a largura, a altura e a profundidade de `selection.element_size`. O handler
`POST_PIXEL` percebe a troca do objeto ativo no próprio desenho e um timer apaga o aviso no fim do tempo.
"""

import time

import bpy  # type: ignore

DURATION = 3.0
MARGIN = 48
PAD_X, PAD_Y = 14, 9

_handle = None
_state = {'name': None, 'shown_at': 0.0}


def _redraw():
    wm = bpy.context.window_manager
    for window in (wm.windows if wm else []):
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    return None


def show(obj):
    """Mostra (de novo) o aviso do objeto, como se ele tivesse acabado de ser tocado."""
    _state['name'] = obj.name if obj is not None else None
    _state['shown_at'] = time.monotonic()
    if bpy.app.timers.is_registered(_redraw):
        bpy.app.timers.unregister(_redraw)
    bpy.app.timers.register(_redraw, first_interval=DURATION + 0.05)
    _redraw()


def message(obj):
    """Texto do aviso, ou None se o objeto não tem medidas para mostrar."""
    from ..data import units
    from ..data.i18n import tr
    from ..selection import element_size
    el = element_size.element(obj)
    if el is None:
        return None
    width, height, depth = element_size.size(el)
    return tr("{} {}   L {} × A {} × P {}").format(
        tr(el.label), el.obj.name, units.format_value(width), units.format_value(height), units.format_value(depth))


def _draw():
    context = bpy.context
    obj = context.active_object
    if obj is None or not obj.select_get():
        _state['name'] = None
        return
    if obj.name != _state['name']:
        show(obj)
    if time.monotonic() - _state['shown_at'] > DURATION:
        return
    try:
        text = message(obj)
    except Exception:              # medida que não dá para ler (objeto sendo refeito): sem aviso neste desenho
        return
    if not text:
        return
    from ..canvas2d import draw
    region = context.region
    w = draw.text_width(text)
    h = draw.FONT_SIZE + 2 * PAD_Y
    x = (region.width - w) / 2.0 - PAD_X
    rect = (x, MARGIN, w + 2 * PAD_X, h)
    sh = draw.begin()
    draw.rect(sh, rect, draw.COLORS['panel'])
    draw.outline(sh, rect, draw.COLORS['border'])
    draw.text(x + PAD_X, MARGIN + PAD_Y + 2, text)
    draw.end()


def register():
    global _handle
    _handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    global _handle
    if _handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        _handle = None
    if bpy.app.timers.is_registered(_redraw):
        bpy.app.timers.unregister(_redraw)
    _state['name'] = None
