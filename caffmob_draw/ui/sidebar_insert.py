"""Seção Inserir (feature 005, T015; RF-03, RN-04, D-06).

Uma galeria só: o seletor de biblioteca (frameless, face frame, closets) e o catálogo da biblioteca escolhida, sem a
parte do usuário, que fica no grupo Meus módulos logo abaixo. O Módulo Rápido (módulo paramétrico do CAFFMob Draw)
também entra por aqui.
"""

from ..data.i18n import N_
from . import my_modules
from .sidebar import group_scope


def draw(layout, context):
    scene = context.scene
    hb_scene = getattr(scene, 'home_builder', None)
    row = layout.row(align=True)
    row.scale_y = 1.2
    row.operator("caffmob.cabinet_builder", text=N_("Módulo Rápido"), icon='OUTLINER_OB_MESH')
    row.operator("caffmob.import_model", text=N_("Importar modelo 3D"), icon='IMPORT')
    if hb_scene is not None:
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop(hb_scene, "product_tab", text="")
        if hb_scene.product_tab == 'FRAMELESS' and hasattr(scene, 'hb_frameless'):
            scene.hb_frameless.draw_library_ui(layout, context, include_user=False)
        elif hb_scene.product_tab == 'FACE FRAME' and hasattr(scene, 'hb_face_frame'):
            scene.hb_face_frame.draw_library_ui(layout, context, include_user=False)
        elif hasattr(scene, 'hb_closets'):
            scene.hb_closets.draw_library_ui(layout, context, include_user=False)
    with group_scope(layout, context, 'my_modules', N_("Meus módulos"), 'USER') as body:
        if body is not None:
            my_modules.draw(body, context)
