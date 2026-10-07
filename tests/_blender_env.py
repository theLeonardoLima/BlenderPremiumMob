"""Ambiente comum dos testes de fumaça da feature 003 no Blender (sem a extensão instalada).

- `extension_path_user` cai numa pasta temporária quando o pacote não é uma extensão instalada;
- preferências do add-on (cores) com valores neutros, como nos testes da 002;
- interface em pt_BR (as mensagens conferidas pelos smokes estão em português).
"""

import os
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
USER_DIR = tempfile.mkdtemp(prefix="caffmob_user_")
_original = bpy.utils.extension_path_user


def _extension_path_user(package, path="", create=False):
    try:
        return _original(package, path=path, create=create)
    except ValueError:
        folder = os.path.join(USER_DIR, path)
        if create:
            os.makedirs(folder, exist_ok=True)
        return folder


bpy.utils.extension_path_user = _extension_path_user

# Os smokes conferem comportamento com as mensagens em português; o Blender de fábrica abre em inglês e, com a
# tradução da interface (BUG-20261007-FLZO), as mensagens seguiriam o inglês. O idioma é testado à parte
# (`blender_bug_FLZO_i18n.py`, que troca a língua por conta própria).
bpy.context.preferences.view.language = 'pt_BR'
bpy.context.preferences.view.use_translate_new_dataname = False   # "Cube" continua "Cube"

import caffmob_draw as addon  # noqa: E402

addon.register()
addon.load_file_post(None)


class _Prefs:
    def __getattr__(self, _name):
        return (0.5, 0.5, 0.5, 1.0)


type(bpy.context.window_manager.home_builder).get_user_preferences = lambda self, c: _Prefs()


def clean_scene():
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def settle(times=3):
    for _ in range(times):
        bpy.context.view_layer.update()
