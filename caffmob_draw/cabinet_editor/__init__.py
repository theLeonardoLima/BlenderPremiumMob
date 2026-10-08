"""Editor de Armário (feature 004, incremento I3).

- `elevation`, `validate`, `state`: núcleos puros (vista frontal, validação, rascunho)
- `props`: sessão em memória e `WindowManager.btm_cabinet_editor`
- `bridge`: ler, editar e reaplicar o módulo pela biblioteca (adaptadores da 003)
- `window`: janela própria e desenho da vista frontal
- `ops_editor`, `ops_actions`, `panels`: abrir, modal, confirmar/cancelar, botões internos e painéis
"""


def _modules():
    # Import tardio: os núcleos puros são usados nos testes fora do Blender sem carregar `bpy`.
    from . import ops_actions, ops_editor, panels, props, window
    return (props, window, ops_editor, ops_actions, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
