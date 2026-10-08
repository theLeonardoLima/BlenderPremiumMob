"""Antiga inserção do submenu `MENU_ID` no menu do botão direito.

Desde a feature 005 o menu de contexto é desenhado por `ui/context_menu.py` (uma inserção só, com o submenu do objeto e
as ações frequentes). Este módulo continua registrável para não quebrar o registro legado, mas não insere nada.
"""


def register():
    pass


def unregister():
    pass
