"""Selecionado abre sozinho quando o objeto ativo muda (feature 005, T011; RN-01, D-03).

`draw` não pode gravar dados, então a troca do ativo é ouvida pelo `msgbus`
(`bpy.msgbus.subscribe_rna` com a chave `(LayerObjects, "active")`). A assinatura
some quando outro arquivo é aberto, por isso é refeita no `load_post`; é removida no `unregister`.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

_OWNER = object()


def on_active_changed(*_args):
    context = bpy.context
    st = getattr(context.window_manager, 'btm_sidebar', None)
    if st is None:
        return
    obj = context.view_layer.objects.active if context.view_layer is not None else None
    name = obj.name if obj is not None else ""
    if name == st.last_active:
        return
    st.last_active = name
    if obj is not None:
        from ..selection import classify
        info = classify.classify(obj)
        if info is not None and info.kind != classify.ANNOTATION:
            st.open_selected = True
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def subscribe():
    bpy.msgbus.clear_by_owner(_OWNER)
    bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects, "active"), owner=_OWNER, args=(),
                             notify=on_active_changed)


@persistent
def on_load_post(*_args):
    subscribe()


def register():
    subscribe()
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)


def unregister():
    if on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post)
    bpy.msgbus.clear_by_owner(_OWNER)
