"""Miniaturas dos itens da biblioteca de objetos (feature 009, T030): `bpy.utils.previews` por caminho do `.png`,
carregadas sob demanda e recarregadas quando o arquivo muda (substituir um item gera outra miniatura)."""

import os

import bpy  # type: ignore
import bpy.utils.previews  # type: ignore

_collection = [None]


def icon_id(path):
    """`icon_value` da miniatura, ou 0 se não houver imagem."""
    if not path or not os.path.isfile(path):
        return 0
    if _collection[0] is None:
        _collection[0] = bpy.utils.previews.new()
    collection = _collection[0]
    key = "{}:{}".format(path, int(os.path.getmtime(path)))
    if key not in collection:
        collection.load(key, path, 'IMAGE')
    return collection[key].icon_id


def register():
    pass


def unregister():
    if _collection[0] is not None:
        bpy.utils.previews.remove(_collection[0])
        _collection[0] = None
