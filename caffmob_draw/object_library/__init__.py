"""Biblioteca de objetos do ambiente (feature 009, incremento I2).

- `catalog`, `store`: núcleos sem `bpy` (categorias, manifesto, pastas)
- `props`: `Object.btm_object_item`
- `item_io`: salvar e inserir itens; `retexture`: acabamento e imagem própria
- `ops`, `panels`: operadores e a seção Inserir › Objetos
"""


def _modules():
    from . import ops, previews, props
    return (props, previews, ops)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
