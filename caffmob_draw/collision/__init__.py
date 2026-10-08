"""Colisão de corpo entre itens e com paredes, piso e teto (feature 004, incremento I2).

- `obb`, `rules`: núcleos puros (caixa orientada, pares, classificação, ordem)
- `props`: `WindowManager.btm_collision` (não salvo)
- `scan`: itens da cena, confirmação pela malha e gravação do resultado
- `stale`: marca o resultado como desatualizado; `overlay`: destaque na viewport
- `ops_collision`, `panels`: verificar, ir para, limpar, afastar até encostar e os painéis
"""


def _modules():
    # Import tardio: `obb` e `rules` são usados nos testes fora do Blender sem carregar `bpy`.
    from . import ops_collision, overlay, panels, props, stale
    return (props, stale, ops_collision, overlay, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
