"""Estado da verificação de colisão (feature 004, T013; data-delta §1.4, D-14).

Fica em `WindowManager.btm_collision` e não é salvo no arquivo, como a interferência de frentes (`inspection/props.py`).
`stale` liga quando um item verificado muda (RN-14); a interface nunca diz "sem colisões" com `stale` ou `error`.
"""

import bpy  # type: ignore

KIND_ITEMS = [('WALL', "Penetração em parede", "Item entra numa parede ou obstáculo"),
              ('ITEM', "Colisão entre itens", "Dois itens ocupam o mesmo espaço"),
              ('FLOOR_CEILING', "Piso ou teto", "Item entra no piso ou no teto")]


class BTM_PG_Collision(bpy.types.PropertyGroup):
    kind: bpy.props.EnumProperty(name="Tipo", items=KIND_ITEMS, default='ITEM')  # type: ignore
    name_a: bpy.props.StringProperty(name="Item")  # type: ignore
    name_b: bpy.props.StringProperty(name="Outro")  # type: ignore
    depth: bpy.props.FloatProperty(name="Profundidade", subtype='DISTANCE', unit='LENGTH')  # type: ignore
    push: bpy.props.FloatVectorProperty(name="Afastar", size=3, subtype='TRANSLATION')  # type: ignore
    location: bpy.props.FloatVectorProperty(name="Ponto", size=3, subtype='TRANSLATION')  # type: ignore


class BTM_PG_CollisionState(bpy.types.PropertyGroup):
    items: bpy.props.CollectionProperty(type=BTM_PG_Collision)  # type: ignore
    index: bpy.props.IntProperty(default=0)  # type: ignore
    checked: bpy.props.IntProperty(
        name="Itens verificados", description="Itens verificados na última checagem (-1 = nunca)",
        default=-1)  # type: ignore
    scope: bpy.props.EnumProperty(
        name="Escopo", items=[('ALL', "Cena", "Todos os itens da cena"),
                              ('SELECTED', "Selecionado", "Só o item selecionado e o que ele toca")],
        default='ALL')  # type: ignore
    stale: bpy.props.BoolProperty(name="Desatualizado", default=False)  # type: ignore
    error: bpy.props.StringProperty(name="Erro")  # type: ignore
    checked_names: bpy.props.StringProperty()  # type: ignore   # nomes verificados, separados por "\n"


classes = (BTM_PG_Collision, BTM_PG_CollisionState)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_collision = bpy.props.PointerProperty(type=BTM_PG_CollisionState)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_collision'):
        del bpy.types.WindowManager.btm_collision
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
