"""Grudar itens em paredes, painéis e outras superfícies planas (feature 004, incremento I1).

- `frame`: núcleo puro (referencial da face, posição do item, face plana)
- `props`: `Object.btm_stick`
- `apply`: posição, handler de depsgraph e temporizador de assentar; `settle`: o que fazer depois do movimento
- `link`, `magnet`, `migrate`: grudar/desgrudar, ímã e migração dos módulos que já estão na parede
- `ops_stick`, `panels`: operadores e painel "Elemento filho"
- `magnet_preview`: prévia do ímã durante o arraste (feature 005)
"""


def _modules():
    # Import tardio: `frame` é usado nos testes fora do Blender sem carregar `bpy`.
    from . import apply, magnet_preview, ops_stick, panels, props
    return (props, apply, ops_stick, panels, magnet_preview)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
