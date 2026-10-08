"""Janela do Editor de Paredes (T028; D-02).

Abre a planta numa **janela própria**: duplica a área 3D atual numa janela nova (`screen.area_dupli`) e troca o tipo
dessa área para Image Editor sem imagem — a tela 2D. A região lateral (N) do Image Editor recebe os painéis do editor.
Se a janela nova não puder ser criada, o editor ocupa a própria área atual e devolve o tipo original ao fechar.
A mecânica da janela é comum ao Editor de Armário e fica em `canvas2d/window.py` (feature 004, D-20).

O desenho da planta é um handler `SpaceImageEditor.draw_handler_add(... 'POST_PIXEL')`, registrado uma vez no
`register()` e removido no `unregister()`; ele só desenha na área marcada pela sessão (`props.Session.area_ptr`).
"""

import bpy  # type: ignore

from ..canvas2d import window as _window
from ..data.i18n import tr
from . import props

_draw_handle = []

EDITOR_CATEGORY = "Editor de Paredes"
side_panel = _window.side_panel
over_side_panel = _window.over_side_panel
visible_width = _window.visible_width
close_later = _window.close_later


def editor_area(context):
    """(janela, área, região principal) do editor aberto, ou (None, None, None)."""
    return _window.editor_area(context, props.session())


def is_editor_area(context):
    return _window.is_editor_area(context, props.session())


def focus_editor_tab(area):
    """Põe a região lateral na aba do editor; devolve True quando ficou ativa."""
    return _window.focus_tab(area, EDITOR_CATEGORY)


def open_editor(context):
    """Abre a janela do editor. Devolve (janela, área, região) ou levanta RuntimeError."""
    return _window.open_window(context, props.session(),
                               tr("O Editor de Paredes precisa de uma janela do Blender aberta."))


def _draw():
    if is_editor_area(bpy.context):
        from . import ops_editor
        ops_editor.draw_plan(bpy.context)


def register():
    if not _draw_handle:
        _draw_handle.append(bpy.types.SpaceImageEditor.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _draw_handle:
        bpy.types.SpaceImageEditor.draw_handler_remove(_draw_handle.pop(), 'WINDOW')
