"""Botões internos do Editor de Armário (feature 004, T046; RF-03, RF-04, RF-06, RF-07, D-22).

Não têm `UNDO`: só registram um pedido na sessão (`props.Session.push`); quem edita o módulo é o modal do editor, para
que o Blender crie um passo de desfazer só no Confirmar. As edições são as da 003 sobre o vão do componente
selecionado (frente, estilo, puxador, material, divisões internas) e o desfazer/refazer do rascunho.
"""

import bpy  # type: ignore

from ..customize import spec
from ..customize.props import PULL_POSITION_ITEMS
from ..data import units
from ..data.i18n import N_, tr
from . import bridge, props

_ENUM_CACHE = {}


def _session_root():
    s = props.session()
    return (s, s.root()) if s is not None else (None, None)


def _adapter():
    _s, root = _session_root()
    return (root, bridge.adapter_of(root)) if root is not None else (None, None)


def selected_path():
    s, root = _session_root()
    if root is None:
        return None
    return bridge.opening_of(root, s.selected)


def _front_items(self, context):
    root, adapter = _adapter()
    allowed = adapter.front_types(root) if adapter else []
    items = [(f, spec.FRONT_LABELS[f], "") for f in spec.FRONT_TYPES if f in allowed] or [('OPEN', "Vazio", "")]
    _ENUM_CACHE['front'] = items
    return items


def _style_items(self, context):
    _root, adapter = _adapter()
    names = adapter.style_names() if adapter else []
    items = [("", "Estilo do módulo", "Volta ao estilo da biblioteca")] + [(n, n, "") for n in names]
    _ENUM_CACHE['style'] = items
    return items


def _pull_items(self, context):
    _root, adapter = _adapter()
    pulls = adapter.pull_items() if adapter else []
    items = ([("", "Puxador do projeto", "Usa a escolha geral do projeto"), (spec.NO_PULL, N_("Sem puxador"), "")]
             + [(key, label, "") for key, label in pulls])
    _ENUM_CACHE['pull'] = items
    return items


class BTM_OT_CabinetEditorEdit(bpy.types.Operator):
    """Edita o vão do componente selecionado no Editor de Armário"""
    bl_idname = "caffmob.cabinet_editor_edit"
    bl_label = "Editar componente"
    bl_options = {'REGISTER', 'INTERNAL'}

    action: bpy.props.EnumProperty(items=[('FRONT', "Frente", ""), ('STYLE', "Estilo", ""), ('PULL', "Puxador", ""),
                                          ('MATERIAL', "Material", ""), ('INTERIOR', "Divisões internas", "")])  # type: ignore
    front: bpy.props.EnumProperty(name="Frente", items=_front_items)  # type: ignore
    drawer_count: bpy.props.IntProperty(name="Gavetas", default=1, min=1, max=spec.MAX_DRAWERS)  # type: ignore
    kind: bpy.props.EnumProperty(name="Frente", items=[('DOOR', "Porta", ""), ('DRAWER', "Gaveta", "")])  # type: ignore
    style: bpy.props.EnumProperty(name="Estilo", items=_style_items)  # type: ignore
    model: bpy.props.EnumProperty(name="Modelo", items=_pull_items)  # type: ignore
    position: bpy.props.EnumProperty(name="Posição", items=PULL_POSITION_ITEMS)  # type: ignore
    all_fronts: bpy.props.BoolProperty(name="Aplicar a todas as frentes", default=False)  # type: ignore
    target: bpy.props.EnumProperty(name="Aplicar em", items=[('FRONTS', "Frentes do vão", ""),
                                                            ('GROUP', "Grupo de peças", "")])  # type: ignore
    group: bpy.props.EnumProperty(name="Grupo", items=[(g, spec.GROUP_LABELS[g], "") for g in spec.GROUPS])  # type: ignore
    material: bpy.props.StringProperty(name="Material", description="Vazio = volta ao material da biblioteca")  # type: ignore
    shelves: bpy.props.IntProperty(name="Prateleiras", min=0, max=spec.MAX_SHELVES)  # type: ignore
    dividers: bpy.props.IntProperty(name="Divisórias", min=0, max=spec.MAX_DIVIDERS)  # type: ignore
    drawers: bpy.props.IntProperty(name="Gavetas internas", min=0, max=spec.MAX_DRAWERS)  # type: ignore
    heights: bpy.props.StringProperty(
        name="Alturas", description="Alturas das prateleiras a partir da base do vão, separadas por ';'. "
        "Vazio = espaçamento igual")  # type: ignore

    @classmethod
    def poll(cls, context):
        return props.session() is not None

    def invoke(self, context, event):
        needs_opening = self.action != 'MATERIAL' or self.target == 'FRONTS'
        if needs_opening and selected_path() is None:
            self.report({'WARNING'}, tr("Selecione um vão ou uma frente na vista"))
            return {'CANCELLED'}
        if self.action == 'INTERIOR':
            root, adapter = _adapter()
            current = adapter.read(root).opening(selected_path()) if adapter else None
            inner = current.interior if current is not None and current.interior else spec.Interior()
            self.shelves, self.dividers, self.drawers = inner.shelves, inner.dividers, inner.drawers
            unit = units.get_scene_length_unit(context.scene)
            self.heights = "; ".join(units.format_length(h, unit=unit) for h in inner.heights)
        if self.action == 'FRONT' and self.front != 'DRAWERS':
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if self.action == 'FRONT':
            layout.prop(self, "drawer_count")
        elif self.action == 'STYLE':
            layout.prop(self, "kind", expand=True)
            layout.prop(self, "style")
        elif self.action == 'PULL':
            layout.prop(self, "model")
            layout.prop(self, "position")
            layout.prop(self, "all_fronts")
        elif self.action == 'MATERIAL':
            layout.prop(self, "target", expand=True)
            if self.target == 'GROUP':
                layout.prop(self, "group")
            layout.prop_search(self, "material", bpy.data, "materials")
        else:
            layout.prop(self, "shelves")
            layout.prop(self, "dividers")
            layout.prop(self, "drawers")
            layout.prop(self, "heights")

    def execute(self, context):
        s = props.session()
        path = selected_path() or ""
        data = {'path': path, 'targets': [s.selected] if s.selected else []}
        if self.action == 'FRONT':
            data.update(front=self.front, drawer_count=self.drawer_count)
        elif self.action == 'STYLE':
            data.update(kind=self.kind, style=self.style)
        elif self.action == 'PULL':
            data.update(model=self.model, position=self.position, all_fronts=self.all_fronts)
        elif self.action == 'MATERIAL':
            data.update(target=self.target, group=self.group, material=self.material)
        else:
            unit = units.get_scene_length_unit(context.scene)
            try:
                heights = [units.parse_length(raw.strip(), default_unit=unit)
                           for raw in self.heights.split(";") if raw.strip()]
            except ValueError:
                self.report({'WARNING'}, tr("Alturas inválidas"))
                return {'CANCELLED'}
            data.update(shelves=self.shelves, dividers=self.dividers, drawers=self.drawers, heights=heights)
        s.push('edit', (self.action, data))
        return {'FINISHED'}


class BTM_OT_CabinetEditorHistory(bpy.types.Operator):
    """Desfaz ou refaz no rascunho do editor (Ctrl+Z / Ctrl+Shift+Z)"""
    bl_idname = "caffmob.cabinet_editor_history"
    bl_label = "Desfazer no editor"
    bl_options = {'REGISTER', 'INTERNAL'}

    redo: bpy.props.BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return props.session() is not None

    def execute(self, context):
        props.session().push('redo' if self.redo else 'undo')
        return {'FINISHED'}


class BTM_OT_CabinetEditorSaveModule(bpy.types.Operator):
    """Salva o armário como está no editor na biblioteca do usuário (Salvar como módulo da 003)"""
    bl_idname = "caffmob.cabinet_editor_save_module"
    bl_label = "Salvar como módulo"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return props.session() is not None and props.session().root() is not None

    def invoke(self, context, event):
        root = props.session().root()
        for obj in context.selected_objects:
            obj.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        return bpy.ops.caffmob.module_save('INVOKE_DEFAULT')


classes = (BTM_OT_CabinetEditorEdit, BTM_OT_CabinetEditorHistory, BTM_OT_CabinetEditorSaveModule)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
