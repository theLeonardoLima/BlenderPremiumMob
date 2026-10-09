"""Registro comum dos painéis das abas de inserção da feature 008 (um painel por aba, padrão do Construtor)."""

import bpy  # type: ignore


def registrar(classes):
    def register():
        for cls in classes:
            bpy.utils.register_class(cls)

    def unregister():
        for cls in reversed(classes):
            if cls.is_registered:
                bpy.utils.unregister_class(cls)
    return register, unregister
