"""Janela importada instalada numa parede (feature 007, T002; data-delta §1.2, D-12, D-13).

Fica na jaula `IS_WINDOW_BP` que "Instalar na parede" cria: aponta para o grupo da esquadria e guarda a matriz do
mundo dele antes de instalar, para "Desinstalar" devolver a janela solta no mesmo lugar.
"""

import bpy  # type: ignore


class BTM_PG_WindowInstall(bpy.types.PropertyGroup):
    frame: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    frame_matrix: bpy.props.FloatVectorProperty(size=16)  # type: ignore


classes = (BTM_PG_WindowInstall,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_window = bpy.props.PointerProperty(type=BTM_PG_WindowInstall)


def unregister():
    if hasattr(bpy.types.Object, 'btm_window'):
        del bpy.types.Object.btm_window
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
