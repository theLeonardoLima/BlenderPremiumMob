"""Aba Portas do Editor de Armário (feature 008, T042; RN-11, RN-13, D-08, D-09, D-21).

Região (Inferior / Superior / Alta / Basculante), portas (Ambas / Inteira / Esquerda / Direita), estilo da biblioteca,
puxador e Inserir invertido (troca o lado da dobradiça); Inserir no vão da biblioteca do vão alvo.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import props
from .panels import _TabPanel, insert_button, properties_box, target_box
from .panels_tabs_common import registrar


class BTM_PT_CabinetEditorDoors(_TabPanel, bpy.types.Panel):
    bl_label = "Portas"
    bl_idname = "BTM_PT_cabinet_editor_doors"
    bl_order = 1
    bl_options = {'HIDE_HEADER'}
    TAB = 'DOORS'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        target_box(layout, context, 'DOORS')
        grid = layout.grid_flow(columns=2, align=True)
        for key in ('LOWER', 'UPPER', 'TALL', 'FLIP'):
            grid.prop_enum(ui, "door_region", key)
        row = layout.row()
        row.enabled = ui.door_region != 'FLIP'
        row.prop(ui, "door_scope", expand=True)
        box = layout.box()
        box.label(text=tr("Estilo"))
        box.prop(ui, "door_style", text="")
        box.prop(ui, "door_pull")
        row = layout.row()
        row.enabled = ui.door_scope in ('WHOLE', 'LEFT', 'RIGHT') or ui.door_region == 'FLIP'
        row.prop(ui, "invert")
        insert_button(layout, context, 'DOORS')
        properties_box(layout, None)
        s = props.session()
        if s.library_box is not None:
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("A frente ocupa o vão da biblioteca contornado na vista"), icon='INFO')


classes = (BTM_PT_CabinetEditorDoors,)
register, unregister = registrar(classes)
