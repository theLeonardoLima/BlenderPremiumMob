"""Aba Fundos do Editor de Armário (feature 008, T044; RN-14, RN-15, D-11).

Inteiro / Inteiro Recuado, a medida do recuo, "Inserir automaticamente" e o item "Fundo Inteiro <espessura>"; Inserir
aplica o modo e devolve o fundo, se ele tiver sido removido.
"""

import bpy  # type: ignore

from ..data import units
from ..data.i18n import tr
from . import bridge, catalog, props
from .panels import _TabPanel, insert_button, properties_box
from .panels_tabs_common import registrar


class BTM_PT_CabinetEditorBacks(_TabPanel, bpy.types.Panel):
    bl_label = "Fundos"
    bl_idname = "BTM_PT_cabinet_editor_backs"
    bl_order = 1
    bl_options = {'HIDE_HEADER'}
    TAB = 'BACKS'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        root = s.root()
        layout.row().prop(ui, "back_tab", expand=True)
        if root is not None:
            holder = root.btm_structure
            layout.prop(holder, "auto_back")
            if ui.back_tab == 'RECESSED':
                layout.prop(holder, "back_setback")
            _material, thickness = bridge.configured_part(context, root, 'BACK')
            unit = units.get_scene_length_unit(context.scene)
            box = layout.box()
            box.label(text=tr("Fundo Inteiro {}").format(units.format_length(thickness, unit)) if thickness
                      else tr("Fundo Inteiro"), icon='MOD_SOLIDIFY')
            current = tr("Inteiro Recuado") if holder.back_mode == 'RECESSED' else tr("Inteiro")
            hint = box.row()
            hint.active = False
            hint.label(text=tr("Atual: {}").format(current))
        insert_button(layout, context, 'BACKS')
        properties_box(layout, catalog.get('BACK_RECESSED' if ui.back_tab == 'RECESSED' else 'BACK_FULL'))


classes = (BTM_PT_CabinetEditorBacks,)
register, unregister = registrar(classes)
