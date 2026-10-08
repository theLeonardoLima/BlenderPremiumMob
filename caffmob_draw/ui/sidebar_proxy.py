"""Desenhar o conteúdo de um painel dentro de uma seção (feature 005, T004; D-04).

Os painéis legados (Home Builder, face frame) e os subpainéis das features 003/004 deixam de ser registrados na aba; o
conteúdo deles é desenhado dentro das seções da barra lateral chamando o próprio `draw` da classe com o layout da seção.
O objeto passado como `self` tem `layout` e, para o resto, cai nos atributos da classe (métodos ligados a ele), então a
lógica de desenho das bibliotecas não muda.
"""

import types


class _PanelProxy:
    def __init__(self, cls, layout):
        object.__setattr__(self, '_cls', cls)
        object.__setattr__(self, 'layout', layout)

    def __getattr__(self, name):
        value = getattr(self._cls, name)
        if isinstance(value, types.FunctionType):
            return types.MethodType(value, self)
        return value

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


def visible(cls, context):
    poll = getattr(cls, 'poll', None)
    if poll is None:
        return True
    try:
        return bool(poll(context))
    except (AttributeError, KeyError, ReferenceError, RuntimeError):
        return False


def draw_panel(cls, layout, context, header=False):
    """Desenha o painel `cls` em `layout` se o `poll` dele permitir; devolve True quando desenhou."""
    if not visible(cls, context):
        return False
    proxy = _PanelProxy(cls, layout)
    if header and hasattr(cls, 'draw_header'):
        cls.draw_header(proxy, context)
    cls.draw(proxy, context)
    return True


def label_of(cls):
    return getattr(cls, 'bl_label', cls.__name__)
