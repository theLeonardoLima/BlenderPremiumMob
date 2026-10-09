"""Modo de vista Sólido · Textura com o interruptor Linhas (feature 010, T011; RN-06, D-05). Python puro.

`settings` traduz o estado da cena nos valores de `View3DShading` e `View3DOverlay` que a vista recebe. Linhas valem
para todos os objetos: `show_wireframes` com limiar 0,5 (arestas de forma, sem a triangulação) e opacidade 0,6.
Voltar a Sólido devolve o `color_type` que a vista tinha antes de Textura.
"""

from ..data.i18n import N_, tr

THRESHOLD = 0.5
OPACITY = 0.6
MODES = (('SOLID', N_("Sólido")), ('TEXTURE', N_("Textura")))


def settings(mode, lines, previous_color):
    color = 'TEXTURE' if mode == 'TEXTURE' else (previous_color if previous_color and previous_color != 'TEXTURE'
                                                 else 'MATERIAL')
    return {'shading_type': 'SOLID', 'color_type': color, 'show_wireframes': bool(lines),
            'wireframe_threshold': THRESHOLD, 'wireframe_opacity': OPACITY}


def label(mode, lines):
    if mode == 'TEXTURE':
        return tr("Textura com linha") if lines else tr("Textura")
    return tr("Sólido com linha") if lines else tr("Sólido")
