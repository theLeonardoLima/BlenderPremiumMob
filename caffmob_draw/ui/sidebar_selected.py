"""Seção Selecionado (feature 005, T017; RF-04, RN-05, D-07).

Os grupos por tipo vêm de `object_properties.draw_selected` (no máximo 4 abertos). Para um módulo face frame, as
opções da biblioteca (dimensões, construção, padrões, vãos, seleção…) entram como o grupo recolhido "Opções do face
frame", com os subpainéis do face frame desenhados pelo proxy, no lugar do antigo painel "Face Frame Cabinet".
"""

from ..data.i18n import N_
from . import object_properties, sidebar_proxy
from .sidebar import group_scope

_FACE_FRAME_CHILDREN = ('HB_FACE_FRAME_PT_dimensions', 'HB_FACE_FRAME_PT_selection', 'HB_FACE_FRAME_PT_all_bays',
                        'HB_FACE_FRAME_PT_construction', 'HB_FACE_FRAME_PT_face_frame_defaults',
                        'HB_FACE_FRAME_PT_leg_product', 'HB_FACE_FRAME_PT_floating_shelf')


def _draw_face_frame(layout, context):
    from ..product_libraries.face_frame import ui_face_frame as uff
    parent = uff.HB_FACE_FRAME_PT_active_cabinet
    if not sidebar_proxy.visible(parent, context):
        return
    with group_scope(layout, context, 'sel_library', N_("Opções do face frame"), 'MESH_GRID') as body:
        if body is None:
            return
        sidebar_proxy.draw_panel(parent, body, context)
        for name in _FACE_FRAME_CHILDREN:
            child = getattr(uff, name, None)
            if child is None or not sidebar_proxy.visible(child, context):
                continue
            box = body.box()
            box.label(text=sidebar_proxy.label_of(child))
            sidebar_proxy.draw_panel(child, box, context, header=True)


def draw(layout, context):
    object_properties.draw_selected(layout, context)
    if context.active_object is not None:
        _draw_face_frame(layout, context)
