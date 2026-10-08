"""Painéis do Editor de Armário (feature 004, T048; RF-02, RF-03, RF-04, RF-06, RF-07, RF-09, RF-10).

Na região lateral do Image Editor, aba "Editor de Armário". Feature 006 (T026; D-01, D-02, brief
`_reversa_forward/006-editor-armario-abas/design/editor-abas.md`): um cabeçalho com o módulo, o estado do rascunho e as
abas **Estrutura · Divisão · Acabamento**; os painéis aparecem conforme a aba:
- Estrutura: Medidas (com a faixa permitida) e Componentes externos (`panels_structure.py`);
- Divisão: Nova divisão e Divisões (`panels_divisions.py`);
- Acabamento: Componentes (lista da 004) e Personalizar (seções da 003 para o vão selecionado; as que a biblioteca
  não tem aparecem desabilitadas com o motivo).
O rodapé é igual em todas as abas: Mensagens, Ajustes automáticos, Desfazer/Refazer, Confirmar / Cancelar / Fechar e
Salvar como módulo.
"""

import bpy  # type: ignore

from ..customize import spec
from ..data import units
from ..data.i18n import tr
from ..selection import classify
from . import bridge, props, window
from .ops_actions import selected_path

_SEVERITY_ICON = {'ERROR': 'ERROR', 'WARNING': 'INFO', 'INFO': 'INFO'}
_CHANGE_LABEL = {'MOVED': "moveu", 'RESIZED': "mudou de medida", 'ADDED': "entrou", 'REMOVED': "saiu"}


class _EditorPanel:
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = props.EDITOR_CATEGORY

    @classmethod
    def poll(cls, context):
        return window.is_editor_area(context)


class _TabPanel(_EditorPanel):
    """Painel que só aparece numa aba (`TAB`)."""
    TAB = 'STRUCTURE'

    @classmethod
    def poll(cls, context):
        return window.is_editor_area(context) and context.window_manager.btm_cabinet_editor.tab == cls.TAB


class BTM_PT_CabinetEditorTabs(_EditorPanel, bpy.types.Panel):
    bl_label = "Editor de Armário"
    bl_idname = "BTM_PT_cabinet_editor_tabs"
    bl_order = 0
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        col = layout.column(align=True)
        library = tr(classify.LIBRARY_LABELS.get(s.library, s.library or ""))
        col.label(text="{}  ·  {}".format(s.root_name, library) if library else s.root_name, icon='MOD_BUILD')
        status = col.row()
        status.active = False
        status.label(text=tr("Rascunho alterado") if s.draft.dirty() else tr("Sem alterações"))
        layout.row().prop_tabs_enum(ui, "tab")
        if s.error:
            box = layout.box()
            box.alert = True
            box.label(text=tr(s.error), icon='ERROR')


class BTM_PT_CabinetEditorDimensions(_TabPanel, bpy.types.Panel):
    bl_label = "Medidas"
    bl_idname = "BTM_PT_cabinet_editor_dimensions"
    bl_order = 1
    TAB = 'STRUCTURE'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        unit = units.get_scene_length_unit(context.scene)
        col = layout.column(align=True)
        for field in ('width', 'height', 'depth'):
            row = col.row(align=True)
            row.alert = bool(s.dim_messages.get(field))
            row.prop(ui, field)
            lo, hi = s.limits[field]
            hint = col.row()
            hint.active = False
            hint.label(text=tr("faixa: {} – {}").format(units.format_length(lo, unit), units.format_length(hi, unit)))


class BTM_UL_CabinetEditorComponents(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        icon = 'ERROR' if item.flagged else ('MESH_PLANE' if item.kind == 'OPENING' else 'MESH_CUBE')
        layout.label(text=item.label, icon=icon)


class BTM_PT_CabinetEditorComponents(_TabPanel, bpy.types.Panel):
    bl_label = "Componentes"
    bl_idname = "BTM_PT_cabinet_editor_components"
    bl_order = 2
    TAB = 'FINISH'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        self.layout.template_list("BTM_UL_CabinetEditorComponents", "", ui, "components", ui, "component_index",
                                  rows=6)


def _edit(layout, action, text, icon, **values):
    op = layout.operator("caffmob.cabinet_editor_edit", text=text, icon=icon)
    op.action = action
    for name, value in values.items():
        setattr(op, name, value)
    return op


class BTM_PT_CabinetEditorCustomize(_TabPanel, bpy.types.Panel):
    bl_label = "Personalizar"
    bl_idname = "BTM_PT_cabinet_editor_customize"
    bl_order = 3
    TAB = 'FINISH'

    def draw(self, context):
        s = props.session()
        root = s.root()
        adapter = bridge.adapter_of(root) if root is not None else None
        layout = self.layout
        if adapter is None:
            layout.label(text=tr("Esta biblioteca não tem personalização"), icon='INFO')
            return
        caps = adapter.capabilities(root)
        path = selected_path()
        layout.label(text=tr("Vão: {}").format(path) if path else tr("Selecione um vão ou uma frente na vista"),
                     icon='RESTRICT_SELECT_OFF')
        for section in spec.SECTIONS:
            box = layout.box()
            box.label(text=tr(spec.SECTION_LABELS[section]))
            reason = caps.get(section)
            if reason:
                row = box.row()
                row.enabled = False
                row.label(text=reason, icon='CANCEL')
                continue
            col = box.column(align=True)
            col.enabled = bool(path) or section == 'MATERIALS'
            if section == 'FRONTS':
                grid = col.grid_flow(columns=2, align=True)
                for front in spec.FRONT_TYPES:
                    if front in adapter.front_types(root):
                        _edit(grid, 'FRONT', tr(spec.FRONT_LABELS[front]), 'NONE', front=front)
                _edit(col, 'STYLE', tr("Estilo da frente…"), 'MATERIAL')
            elif section == 'PULLS':
                _edit(col, 'PULL', tr("Puxador…"), 'MOD_ARRAY')
            elif section == 'MATERIALS':
                sub = col.row(align=True)
                sub.enabled = bool(path)
                _edit(sub, 'MATERIAL', tr("Material das frentes do vão…"), 'MATERIAL', target='FRONTS')
                _edit(col, 'MATERIAL', tr("Material de um grupo…"), 'MATERIAL', target='GROUP')
            elif section == 'INTERIOR':
                _edit(col, 'INTERIOR', tr("Divisões internas…"), 'MOD_LATTICE')


class BTM_PT_CabinetEditorMessages(_EditorPanel, bpy.types.Panel):
    bl_label = "Mensagens"
    bl_idname = "BTM_PT_cabinet_editor_messages"
    bl_order = 90

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.messages:
            layout.label(text=tr("Sem erros nem avisos"), icon='CHECKMARK')
            return
        for m in ui.messages:
            box = layout.box()
            box.alert = m.blocks
            head = m.code
            if m.component:
                head += " — " + m.component
            if m.parameter:
                head += " — " + tr(m.parameter)
            box.label(text=head, icon=_SEVERITY_ICON.get(m.severity, 'INFO'))
            if m.value or m.range:
                box.label(text=tr("valor: {}  faixa: {}").format(m.value or "-", m.range or "-"))
            if m.action:
                box.label(text=m.action)


class BTM_PT_CabinetEditorAdjustments(_EditorPanel, bpy.types.Panel):
    bl_label = "Ajustes automáticos"
    bl_idname = "BTM_PT_cabinet_editor_adjustments"
    bl_order = 91
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.adjustments:
            layout.label(text=tr("Nenhum ajuste automático"))
            return
        col = layout.column(align=True)
        for row in ui.adjustments[:30]:
            col.label(text="{}: {}".format(row.component, tr(_CHANGE_LABEL.get(row.change, row.change))))
        if len(ui.adjustments) > 30:
            col.label(text=tr("… e mais {}").format(len(ui.adjustments) - 30))


class BTM_PT_CabinetEditorConfirm(_EditorPanel, bpy.types.Panel):
    bl_label = "Confirmar"
    bl_idname = "BTM_PT_cabinet_editor_confirm"
    bl_order = 99
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        s = props.session()
        layout = self.layout
        row = layout.row(align=True)
        row.operator("caffmob.cabinet_editor_history", text=tr("Desfazer"), icon='LOOP_BACK').redo = False
        row.operator("caffmob.cabinet_editor_history", text=tr("Refazer"), icon='LOOP_FORWARDS').redo = True
        if s.blocking():
            box = layout.box()
            box.alert = True
            box.label(text=tr("Corrija os erros para confirmar"), icon='ERROR')
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("caffmob.cabinet_editor_confirm", text=tr("Confirmar"), icon='CHECKMARK')
        row.operator("caffmob.cabinet_editor_cancel", text=tr("Cancelar"), icon='X')
        row = layout.row(align=True)
        row.operator("caffmob.cabinet_editor_close", text=tr("Fechar"), icon='PANEL_CLOSE')
        row.operator("caffmob.cabinet_editor_save_module", text=tr("Salvar como módulo"), icon='FILE_TICK')


classes = (BTM_PT_CabinetEditorTabs, BTM_PT_CabinetEditorDimensions, BTM_UL_CabinetEditorComponents, BTM_PT_CabinetEditorComponents,
           BTM_PT_CabinetEditorCustomize, BTM_PT_CabinetEditorMessages, BTM_PT_CabinetEditorAdjustments,
           BTM_PT_CabinetEditorConfirm)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
