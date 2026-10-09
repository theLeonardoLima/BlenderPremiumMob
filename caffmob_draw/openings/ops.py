"""Atualizar portas e janelas (feature 010, T022; RN-04, D-16).

Caixas de porta e janela de arquivos antigos (sem a porta real) ou de uma versão anterior do gerador são montadas de
novo, nas mesmas posições e medidas. Nunca roda sozinho: a barra lateral só avisa.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import sync


class BTM_OT_OpeningsUpdate(bpy.types.Operator):
    """Troca as portas e janelas em caixa deste arquivo pelas portas e janelas reais"""
    bl_idname = "caffmob.openings_update"
    bl_label = "Atualizar portas e janelas"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        cages = sync.outdated(context.scene)
        done = sum(1 for cage in cages if sync.sync(context, cage, force=True))
        if not cages:
            self.report({'INFO'}, tr("Todas as portas e janelas já estão atualizadas"))
        else:
            self.report({'INFO'}, tr("{} porta(s) e janela(s) atualizada(s)").format(done))
        return {'FINISHED'}


classes = (BTM_OT_OpeningsUpdate,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
