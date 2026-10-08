"""Histórico do rascunho do Editor de Paredes (BUG-20261007-ZZUK). Python puro.

Ctrl+Z desfaz, uma por vez, as ações feitas na planta antes do OK; Ctrl+Shift+Z (ou Ctrl+Y) refaz. Cada passo é uma
cópia do `WallPlan`, gravada quando a assinatura do rascunho (`model.plan_signature`) muda. O desfazer do Blender não
alcança o rascunho, que vive só em memória até o OK (RN-16 da 002).

A assinatura é uma função: o editor de armário (feature 004, D-21) usa o mesmo histórico com a assinatura do estado dele.
"""

import copy

from . import model

LIMIT = 100


class History:
    def __init__(self, plan, limit=LIMIT, signature=model.plan_signature):
        self.limit = int(limit)
        self._sign = signature
        self._undo = []
        self._redo = []
        self._current = copy.deepcopy(plan)
        self._signature = self._sign(plan)

    def checkpoint(self, plan):
        """Grava um passo se o rascunho mudou desde o último; devolve True quando gravou."""
        signature = self._sign(plan)
        if signature == self._signature:
            return False
        self._undo.append(self._current)
        del self._undo[:-self.limit]
        self._redo.clear()
        self._current = copy.deepcopy(plan)
        self._signature = signature
        return True

    def can_undo(self):
        return bool(self._undo)

    def can_redo(self):
        return bool(self._redo)

    def _move(self, source, target):
        if not source:
            return None
        target.append(self._current)
        self._current = source.pop()
        self._signature = self._sign(self._current)
        return copy.deepcopy(self._current)

    def undo(self):
        """Rascunho anterior (cópia), ou None se não houver."""
        return self._move(self._undo, self._redo)

    def redo(self):
        """Rascunho desfeito por último (cópia), ou None se não houver."""
        return self._move(self._redo, self._undo)
