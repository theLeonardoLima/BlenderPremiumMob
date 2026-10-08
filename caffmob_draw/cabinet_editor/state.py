"""Estado do editor de armário e o histórico do rascunho (feature 004, T009; D-21). Python puro, sem `bpy`.

O módulo é editado ao vivo; o rascunho é a pilha de instantâneos `EditorState` (medidas + personalização da 003 como
dicionário). Desfazer e refazer no editor devolvem um instantâneo, que a ponte com a cena reaplica. O instantâneo
inicial é o que Cancelar reaplica. O histórico é o mesmo do editor de paredes, com a assinatura deste estado.
"""

import copy
import json
from dataclasses import dataclass, field

from ..walls2d import history as _history

PRECISION = 6       # casas (m) na assinatura: 1 µm


@dataclass
class EditorState:
    dimensions: tuple = (0.0, 0.0, 0.0)      # largura, altura, profundidade (m)
    spec: dict = field(default_factory=dict)

    def copy(self):
        return copy.deepcopy(self)


def signature(state):
    dims = [round(float(v), PRECISION) for v in state.dimensions]
    return json.dumps({"dims": dims, "spec": state.spec}, sort_keys=True, default=str)


class Draft:
    """Instantâneo inicial + histórico do rascunho."""

    def __init__(self, initial):
        self.initial = initial.copy()
        self.current = initial.copy()
        self.history = _history.History(self.current, signature=signature)

    def checkpoint(self, state):
        self.current = state.copy()
        return self.history.checkpoint(self.current)

    def undo(self):
        state = self.history.undo()
        if state is not None:
            self.current = state
        return state

    def redo(self):
        state = self.history.redo()
        if state is not None:
            self.current = state
        return state

    def dirty(self):
        return signature(self.current) != signature(self.initial)
