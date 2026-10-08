"""Barra lateral única do CAFFMob Draw (feature 005, T010; RN-01, RN-02, D-01, D-02).

Um painel hospedeiro, sem cabeçalho, desenha as 5 seções na ordem do trabalho (Construir, Inserir, Selecionado,
Verificar, Produção/Projeto) como painéis de layout recolhíveis (`UILayout.panel_prop`): ficam iguais aos painéis do
Blender, mas o estado aberto/fechado vive em `WindowManager.btm_sidebar`, o que deixa Selecionado abrir sozinho quando
algo é selecionado (`sidebar_selection.py`). Cada função aparece numa seção só.

`group()` é o mesmo recurso para os grupos internos. Quando o layout é a camada falsa dos testes
(`layout_probe.Probe`), cada seção e grupo vira um escopo do inventário.
"""

from contextlib import contextmanager, nullcontext

import bpy  # type: ignore

from ..data.i18n import tr
from . import sidebar_vocab

CATEGORY = "CAFFMob Draw"


def state(context):
    return context.window_manager.btm_sidebar


@contextmanager
def _scope(layout, name):
    recorder = getattr(layout, 'recorder', None)
    with (recorder.section(name) if recorder is not None else nullcontext()):
        yield


def group(layout, context, gid, label, icon='NONE'):
    """Grupo recolhível dentro de uma seção; devolve o corpo (ou None se recolhido)."""
    header, body = layout.panel_prop(state(context), f"open_group_{gid}")
    header.label(text=tr(label), icon=icon)
    return body


@contextmanager
def group_scope(layout, context, gid, label, icon='NONE'):
    body = group(layout, context, gid, label, icon)
    with _scope(layout, tr(label)):
        yield body


def empty_state(layout, text, icon='INFO'):
    layout.label(text=tr(text), icon=icon)


def _sections():
    from . import sidebar_build, sidebar_check, sidebar_insert, sidebar_project, sidebar_selected
    return {'build': sidebar_build.draw, 'insert': sidebar_insert.draw, 'selected': sidebar_selected.draw,
            'check': sidebar_check.draw, 'project': sidebar_project.draw}


def draw_header(layout, context):
    """Topo fixo: ambiente atual, navegador de cenas, modo de seleção e o aviso de configurações recomendadas."""
    from . import sidebar_proxy, view3d_sidebar
    with _scope(layout, tr("Topo")):
        sidebar_proxy.draw_panel(view3d_sidebar.HOME_BUILDER_PT_hidden_header, layout, context)


def draw_sidebar(layout, context):
    draw_header(layout, context)
    st = state(context)
    sections = _sections()
    for key, label, icon in sidebar_vocab.SECTIONS:
        header, body = layout.panel_prop(st, f"open_{key}")
        header.label(text=tr(label), icon=icon)
        if body is None:
            continue
        with _scope(layout, tr(label)):
            sections[key](body, context)


class BTM_PT_Sidebar(bpy.types.Panel):
    bl_label = "CAFFMob Draw"
    bl_idname = "BTM_PT_sidebar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return getattr(context.window_manager, 'btm_sidebar', None) is not None

    def draw(self, context):
        draw_sidebar(self.layout, context)


classes = (BTM_PT_Sidebar,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
