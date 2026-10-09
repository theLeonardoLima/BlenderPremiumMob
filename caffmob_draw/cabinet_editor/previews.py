"""Miniaturas do catálogo do Construtor (feature 008, T035; D-19).

Coleção `bpy.utils.previews` carregada sob demanda de `cabinet_editor/thumbnails/<chave>.png` (o padrão de
`standards/previews.py`). Sem a imagem, quem desenha usa um ícone nativo. `unregister` remove a coleção.
"""

import os

import bpy  # type: ignore
import bpy.utils.previews  # type: ignore

FOLDER = os.path.join(os.path.dirname(__file__), "thumbnails")
_collection = [None]


def icon_id(key):
    """`icon_value` da miniatura `key`, ou 0 se a imagem não existe."""
    path = os.path.join(FOLDER, key + ".png")
    if not os.path.isfile(path):
        return 0
    if _collection[0] is None:
        _collection[0] = bpy.utils.previews.new()
    collection = _collection[0]
    if key not in collection:
        collection.load(key, path, 'IMAGE')
    return collection[key].icon_id


def register():
    pass


def unregister():
    if _collection[0] is not None:
        bpy.utils.previews.remove(_collection[0])
        _collection[0] = None
