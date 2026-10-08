"""Dados gravados no módulo pelas abas Estrutura e Divisão (feature 006, T001; data-delta §1.1, §1.2).

- `Object.btm_structure` (na raiz do módulo): só os componentes externos que o usuário mexeu. Ausente = como a
  biblioteca faz.
- `Object.btm_division` (em cada chapa de divisão): subvão, orientação, posição e recuos. A chapa é um `CabinetPart`
  filho da raiz (D-03); o objeto é desenhado e lido como qualquer peça.

Medidas em metros. Espessura 0 e material vazio = segue o Configurador de Dimensões.
"""

import bpy  # type: ignore

ROLE_ITEMS = [
    ('TOP', "Tampo", "Chapa de cima"),
    ('BOTTOM', "Base", "Chapa de baixo"),
    ('BACK', "Fundo", "Chapa de trás"),
    ('LEFT', "Lateral esquerda", ""),
    ('RIGHT', "Lateral direita", ""),
]
MODE_ITEMS = [
    ('KEEP', "Manter tudo", "Medidas e demais chapas ficam onde estão; só a chapa sai"),
    ('EXTEND', "Estender as vizinhas", "As chapas vizinhas avançam até a borda; o vão interno cresce"),
    ('SHRINK', "Reduzir o armário", "As medidas externas diminuem pela espessura da chapa; o vão interno fica igual"),
]
ORIENTATION_ITEMS = [
    ('VERTICAL', "Vertical", "Chapa em pé: separa esquerda e direita"),
    ('HORIZONTAL', "Horizontal", "Chapa deitada: separa cima e baixo"),
]
MATERIAL_ITEMS = [('', "Do Configurador", "Segue o Configurador de Dimensões")] + [
    (m, m, "") for m in ('MDF', 'MDP', 'COMPENSADO', 'OSB', 'VIDRO', 'OUTRO')]


class BTM_PG_StructureItem(bpy.types.PropertyGroup):
    role: bpy.props.EnumProperty(name="Componente", items=ROLE_ITEMS)  # type: ignore
    removed: bpy.props.BoolProperty(name="Removido", default=False)  # type: ignore
    mode: bpy.props.EnumProperty(name="Ao remover", items=MODE_ITEMS, default='KEEP')  # type: ignore
    thickness: bpy.props.FloatProperty(name="Espessura", subtype='DISTANCE', unit='LENGTH', min=0.0,
                                       description="0 = segue o Configurador")  # type: ignore
    material: bpy.props.StringProperty(name="Material da chapa",
                                       description="Vazio = segue o Configurador")  # type: ignore


class BTM_PG_Structure(bpy.types.PropertyGroup):
    components: bpy.props.CollectionProperty(type=BTM_PG_StructureItem)  # type: ignore

    def item(self, role, create=False):
        for entry in self.components:
            if entry.role == role:
                return entry
        if not create:
            return None
        entry = self.components.add()
        entry.role = role
        return entry

    def to_dict(self):
        return {e.role: {"removed": bool(e.removed), "mode": e.mode, "thickness": float(e.thickness),
                         "material": e.material} for e in self.components}

    def from_dict(self, data):
        self.components.clear()
        for role, values in sorted((data or {}).items()):
            entry = self.components.add()
            entry.role = role
            entry.removed = bool(values.get("removed", False))
            entry.mode = values.get("mode", 'KEEP') or 'KEEP'
            entry.thickness = float(values.get("thickness", 0.0) or 0.0)
            entry.material = str(values.get("material", "") or "")


class BTM_PG_Division(bpy.types.PropertyGroup):
    is_division: bpy.props.BoolProperty(default=False)  # type: ignore
    uid: bpy.props.StringProperty()  # type: ignore
    space: bpy.props.StringProperty(name="Subvão", default="s0")  # type: ignore
    orientation: bpy.props.EnumProperty(name="Orientação", items=ORIENTATION_ITEMS)  # type: ignore
    offset: bpy.props.FloatProperty(name="Posição", subtype='DISTANCE', unit='LENGTH')  # type: ignore
    use_front: bpy.props.BoolProperty(name="Recuo na frente", default=False)  # type: ignore
    front: bpy.props.FloatProperty(name="Recuo da frente", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                   min=0.0)  # type: ignore
    use_back: bpy.props.BoolProperty(name="Recuo atrás", default=False)  # type: ignore
    back: bpy.props.FloatProperty(name="Recuo de trás", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                  min=0.0)  # type: ignore
    thickness: bpy.props.FloatProperty(name="Espessura", subtype='DISTANCE', unit='LENGTH', min=0.0,
                                       description="0 = segue o Configurador")  # type: ignore
    material: bpy.props.StringProperty(name="Material da chapa",
                                       description="Vazio = segue o Configurador")  # type: ignore

    FIELDS = ('uid', 'space', 'orientation', 'offset', 'use_front', 'front', 'use_back', 'back', 'thickness',
              'material')

    def to_dict(self):
        return {name: getattr(self, name) for name in self.FIELDS}

    def from_dict(self, data):
        for name in self.FIELDS:
            if name in data:
                setattr(self, name, data[name])
        self.is_division = True


classes = (BTM_PG_StructureItem, BTM_PG_Structure, BTM_PG_Division)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_structure = bpy.props.PointerProperty(type=BTM_PG_Structure)
    bpy.types.Object.btm_division = bpy.props.PointerProperty(type=BTM_PG_Division)


def unregister():
    for name in ('btm_division', 'btm_structure'):
        if hasattr(bpy.types.Object, name):
            delattr(bpy.types.Object, name)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
