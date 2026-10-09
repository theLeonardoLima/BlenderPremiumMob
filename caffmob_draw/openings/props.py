"""Dados da porta e da janela reais na caixa da parede (feature 010, T001; data-delta §2).

`Object.btm_opening_real` fica na caixa (`GeoNodeCage` com `IS_ENTRY_DOOR_BP`/`IS_WINDOW_BP`): o que foi montado nela, a
assinatura das medidas da última montagem (igual = não refaz) e a versão do gerador. `kind = NONE` = caixa antiga,
ainda sem a porta real ("Atualizar portas e janelas").
"""

import bpy  # type: ignore

KIND_ITEMS = [('NONE', "Nenhum", "Caixa antiga, sem a porta real"), ('DOOR', "Porta", ""),
              ('DOUBLE_DOOR', "Porta dupla", ""), ('OPEN_DOOR', "Vão aberto", ""), ('WINDOW', "Janela", "")]
MODEL_VERSION = 1


class BTM_PG_Opening(bpy.types.PropertyGroup):
    kind: bpy.props.EnumProperty(items=KIND_ITEMS, default='NONE')  # type: ignore
    signature: bpy.props.StringProperty()  # type: ignore
    model_version: bpy.props.IntProperty(default=0)  # type: ignore
    assembly: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore


classes = (BTM_PG_Opening,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_opening_real = bpy.props.PointerProperty(type=BTM_PG_Opening)


def unregister():
    if hasattr(bpy.types.Object, 'btm_opening_real'):
        del bpy.types.Object.btm_opening_real
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
