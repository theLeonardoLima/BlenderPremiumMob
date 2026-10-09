"""Porta e janela reais na parede (feature 010, incrementos I3 e I4).

- `door_core`, `window_core`: geradores paramétricos puros (peças pela largura, altura e espessura da parede)
- `materials`, `build`: materiais compartilhados e montagem em poucas malhas por papel
- `sync`: monta e refaz a porta ou a janela dentro da caixa da parede
- `props`, `ops`: `Object.btm_opening_real` e "Atualizar portas e janelas"
"""


def _modules():
    from ..ui import view_mode
    from . import ops, props
    return (props, ops, view_mode)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
