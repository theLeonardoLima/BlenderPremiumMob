"""Grupo de peças (feature 007, T001; data-delta §1.1, D-03).

Um Empty com `Object.btm_group` é o "objeto de grupo": as peças viram filhas dele e se movem juntas, sem fundir as
malhas (nome, material e vidro continuam separados). Cada membro guarda o pai e a matriz do mundo de antes, para
desfazer o grupo sem perda (RN-04).
"""

import bpy  # type: ignore

KIND_ITEMS = [
    ('PLAIN', "Grupo", "Peças que se movem juntas"),
    ('FRAME', "Esquadria", "Parte fixa da janela ou porta: marco, bordas, trilhos e guias"),
    ('LEAF', "Folha", "Parte móvel: abre e fecha"),
]


class BTM_PG_GroupMember(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    orig_parent: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    orig_matrix: bpy.props.FloatVectorProperty(size=16)  # type: ignore


class BTM_PG_Group(bpy.types.PropertyGroup):
    is_group: bpy.props.BoolProperty(default=False)  # type: ignore
    kind: bpy.props.EnumProperty(name="Papel", items=KIND_ITEMS, default='PLAIN')  # type: ignore
    members: bpy.props.CollectionProperty(type=BTM_PG_GroupMember)  # type: ignore


classes = (BTM_PG_GroupMember, BTM_PG_Group)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_group = bpy.props.PointerProperty(type=BTM_PG_Group)


def unregister():
    if hasattr(bpy.types.Object, 'btm_group'):
        del bpy.types.Object.btm_group
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
