"""Editor de Armário (feature 004, incremento I3).

- `elevation`, `validate`, `state`: núcleos puros (vista frontal, validação, rascunho)
- `props`: sessão em memória e `WindowManager.btm_cabinet_editor`
- `bridge`: ler, editar e reaplicar o módulo pela biblioteca (adaptadores da 003)
- `window`: janela própria e desenho da vista frontal
- `ops_editor`, `ops_actions`, `panels`: abrir, modal, confirmar/cancelar, botões internos e painéis
- Feature 006: `data_props` (estrutura e divisões gravadas no módulo), `divisions` e `structure` (núcleos puros),
  `scene_divisions` (chapas na cena), `reflow_handler` (divisões acompanham o vão), `panels_structure` e
  `panels_divisions` (abas Estrutura e Divisão)
"""


def _modules():
    # Import tardio: os núcleos puros são usados nos testes fora do Blender sem carregar `bpy`.
    from . import (data_props, ops_actions, ops_editor, panels, panels_divisions, panels_structure, props,
                   reflow_handler, window)
    return (data_props, props, window, ops_editor, ops_actions, panels, panels_structure, panels_divisions,
            reflow_handler)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
