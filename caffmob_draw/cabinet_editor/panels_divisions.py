"""Aba Divisão do Editor de Armário (feature 006, T028; RN-08 a RN-14, RF-09 a RF-14).

Nova divisão: chapa do Configurador (material e espessura), vão escolhido (lista ou clique na vista), orientação,
recuos da frente e de trás com as medidas e Adicionar. Divisões: uma linha por chapa, com Editar e Remover.
Brief: `_reversa_forward/006-editor-armario-abas/design/editor-abas.md`.
"""

import bpy  # type: ignore

from ..data import units
from ..data.i18n import tr
from . import props, scene_divisions
from .panels import _TabPanel
from .panels_structure import face_frame_note


class BTM_PT_CabinetEditorDivisionNew(_TabPanel, bpy.types.Panel):
    bl_label = "Nova divisão"
    bl_idname = "BTM_PT_cabinet_editor_division_new"
    bl_order = 1
    TAB = 'DIVISIONS'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        root = s.root()
        if root is not None:
            material, thickness = scene_divisions.configured(context.scene, root)
            info = layout.row()
            info.active = False
            info.label(text=tr("Chapa: {} {} (Configurador › {})").format(
                material, units.format_length(thickness, units.get_scene_length_unit(context.scene)),
                scene_divisions.line_of(root)), icon='MOD_SOLIDIFY')
        face_frame_note(layout)
        col = layout.column()
        col.prop(ui, "space")
        hint = col.row()
        hint.active = False
        hint.label(text=tr("ou clique no vão na vista"))
        col.separator()
        col.row().prop(ui, "new_orientation", expand=True)
        for use, value in (("new_use_front", "new_front"), ("new_use_back", "new_back")):
            row = col.row(align=True)
            row.prop(ui, use)
            sub = row.row(align=True)
            sub.active = getattr(ui, use)
            sub.prop(ui, value, text="")
        col.separator()
        row = col.row()
        row.scale_y = 1.4
        row.enabled = bool(s.space and s.space in s.spaces)
        label = tr("Adicionar em {}").format(s.space_labels.get(s.space, "")) if row.enabled else tr("Adicionar")
        row.operator("caffmob.cabinet_editor_division_add", text=label, icon='ADD')


class BTM_PT_CabinetEditorDivisionList(_TabPanel, bpy.types.Panel):
    bl_label = "Divisões"
    bl_idname = "BTM_PT_cabinet_editor_division_list"
    bl_order = 2
    TAB = 'DIVISIONS'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.divisions:
            row = layout.row()
            row.active = False
            row.label(text=tr("Nenhuma divisão. Escolha um vão e clique em Adicionar."))
            return
        col = layout.column(align=True)
        for item in ui.divisions:
            box = col.box()
            box.alert = item.flagged
            head = box.row(align=True)
            head.label(text=item.label, icon='ERROR' if item.flagged else 'MOD_LATTICE')
            head.operator("caffmob.cabinet_editor_division_edit", text="", icon='GREASEPENCIL').uid = item.uid
            head.operator("caffmob.cabinet_editor_division_remove", text="", icon='X').uid = item.uid
            detail = box.row()
            detail.active = False
            detail.label(text=item.detail)


classes = (BTM_PT_CabinetEditorDivisionNew, BTM_PT_CabinetEditorDivisionList)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
