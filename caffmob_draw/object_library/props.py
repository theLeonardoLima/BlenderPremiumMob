"""Dados de um item da biblioteca de objetos no objeto raiz (feature 009, T001; D-09, data-delta §2).

`Object.btm_object_item` marca a raiz de um item inserido ou salvo: id estável, categoria, origem e licença. As
conversões (grupo de peças, folha, agregado, peça de produção) ficam nos próprios objetos (`btm_group`,
`btm_aggregate`), não aqui.
"""

import bpy  # type: ignore

from .catalog import CATEGORY_ITEMS


class BTM_PG_ObjectItem(bpy.types.PropertyGroup):
    is_item: bpy.props.BoolProperty(default=False)  # type: ignore
    item_id: bpy.props.StringProperty(name="Id do item")  # type: ignore
    category: bpy.props.EnumProperty(name="Categoria", items=CATEGORY_ITEMS, default='OTHER')  # type: ignore
    source: bpy.props.StringProperty(name="Origem")  # type: ignore
    license: bpy.props.StringProperty(name="Licença")  # type: ignore


class BTM_PG_ObjectLibraryUI(bpy.types.PropertyGroup):
    """Estado da seção Inserir › Objetos (não vai para o arquivo)."""
    category: bpy.props.EnumProperty(name="Categoria", items=CATEGORY_ITEMS, default='DOORS')  # type: ignore
    search: bpy.props.StringProperty(name="Buscar", description="Parte do nome do objeto",
                                     options={'TEXTEDIT_UPDATE'})  # type: ignore


classes = (BTM_PG_ObjectItem, BTM_PG_ObjectLibraryUI)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_object_item = bpy.props.PointerProperty(type=BTM_PG_ObjectItem)
    bpy.types.WindowManager.btm_object_library = bpy.props.PointerProperty(type=BTM_PG_ObjectLibraryUI)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_object_library'):
        del bpy.types.WindowManager.btm_object_library
    if hasattr(bpy.types.Object, 'btm_object_item'):
        del bpy.types.Object.btm_object_item
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
