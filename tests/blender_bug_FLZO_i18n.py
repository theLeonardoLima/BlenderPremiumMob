"""Reprodução do BUG-20261007-FLZO no Blender: a interface segue o idioma do Blender, sem reinstalar o plugin.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_FLZO_i18n.py
"""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.data.i18n import N_, tr  # noqa: E402

T = bpy.app.translations
view = bpy.context.preferences.view
view.use_translate_interface = view.use_translate_tooltips = view.use_translate_reports = True
HINT = ("Clique numa face (interna tracejada / externa) ou num vértice e digite a medida + Enter; arraste os vértices. "
        "Delete remove o trecho.")


def language(code):
    view.language = code
    assert T.locale == code, T.locale


# 1. Blender em inglês: a barra do editor, o rótulo do operador e os itens do painel saem em inglês.
language('en_US')
assert tr(HINT).startswith("Click a face"), tr(HINT)
assert N_(HINT) == HINT
assert T.pgettext_iface("Editar Paredes…", "Operator") == "Edit Walls…"
assert T.pgettext_iface("Paredes de outra camada") != "Paredes de outra camada"
assert tr("Comprimento: {}").format("1.200") == "Length: 1.200"
assert tr("Empilhar") == "Stack"                                   # etapa B: texto desenhado do Mover Sobre

# 2. Blender em português: os rótulos herdados em inglês saem em português (contexto padrão e de operador).
language('pt_BR')
assert tr(HINT) == HINT
assert T.pgettext_iface("Place Door", "Operator") == "Inserir Porta"     # etapa C: rótulo de operador herdado
assert T.pgettext_iface("Reset Closet Dimension Label", "Operator") != "Reset Closet Dimension Label"   # etapa D
assert T.pgettext_iface("Add Countertops", "Operator") != "Add Countertops"                           # etapa E
assert T.pgettext_iface("Join Cabinets", "Operator") != "Join Cabinets"                               # etapa F
for msgid in ("Wall Thickness", "Wall Height"):
    assert T.pgettext_iface(msgid) != msgid, msgid
    assert T.pgettext_iface(msgid, "Operator") != msgid, msgid

# 3. Trocar de volta muda na hora, sem registrar de novo.
language('en_US')
assert tr(HINT).startswith("Click a face")

print("blender_bug_FLZO_i18n: OK")
