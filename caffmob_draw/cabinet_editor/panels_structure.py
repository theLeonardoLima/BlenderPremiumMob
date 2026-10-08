"""Aba Estrutura do Editor de Armário: componentes externos (feature 006, T027; RN-03 a RN-07, RF-05 a RF-08).

Uma linha por chapa que o módulo tem (tampo, base, fundo, laterais): medidas, material e espessura em uso, Editar e
Remover; removida mostra "removido · <modo>" e Restaurar. O que a biblioteca não faz fica desabilitado, com o motivo
no tooltip (RN-07). Brief: `_reversa_forward/006-editor-armario-abas/design/editor-abas.md`.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import props
from .panels import _TabPanel
from .structure import MODE_LABELS

FACE_FRAME_NOTE = "Face frame ainda não entra no plano de corte"


def face_frame_note(layout):
    s = props.session()
    if s is not None and s.library == 'FACE_FRAME':
        row = layout.row()
        row.active = False
        row.label(text=tr(FACE_FRAME_NOTE), icon='INFO')


class BTM_PT_CabinetEditorStructure(_TabPanel, bpy.types.Panel):
    bl_label = "Componentes externos"
    bl_idname = "BTM_PT_cabinet_editor_structure"
    bl_order = 2
    TAB = 'STRUCTURE'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.structure:
            row = layout.row()
            row.active = False
            row.label(text=tr("Esta biblioteca não tem estrutura editável"), icon='INFO')
            return
        col = layout.column(align=True)
        for item in ui.structure:
            box = col.box()
            head = box.row(align=True)
            head.label(text=item.label, icon='MESH_PLANE' if not item.removed else 'GHOST_DISABLED')
            if item.removed:
                op = head.operator("caffmob.cabinet_editor_part_restore", text=tr("Restaurar"), icon='LOOP_BACK')
                op.role = item.role
                detail = box.row()
                detail.active = False
                detail.label(text="{} · {}".format(tr("removido"), tr(MODE_LABELS.get(item.mode, item.mode))))
                continue
            edit = head.row(align=True)
            edit.enabled = not item.reason_edit
            edit.operator("caffmob.cabinet_editor_part_edit", text="", icon='GREASEPENCIL').role = item.role
            remove = head.row(align=True)
            remove.enabled = not item.reason_remove
            remove.operator("caffmob.cabinet_editor_part_remove", text="", icon='X').role = item.role
            detail = box.row()
            detail.active = False
            text = "{}  ·  {} {}".format(item.size, item.material, item.thickness)
            if item.changed:
                text += "  ·  " + tr("alterado")
            detail.label(text=text)
        face_frame_note(layout)


classes = (BTM_PT_CabinetEditorStructure,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
