"""Testes do histórico do rascunho do editor de paredes (BUG-20261007-ZZUK): `caffmob_draw/walls2d/history.py`.

Regressão: Ctrl+Z desfaz passo a passo dentro do editor e Ctrl+Shift+Z refaz.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import history, model


def plan():
    return model.WallPlan([model.rectangle(4.0, 3.0)])


class HistoryTest(unittest.TestCase):
    def test_desfaz_e_refaz_passo_a_passo(self):
        p = plan()
        h = history.History(p)
        lengths = []
        for extra in (0.5, 1.0, 1.5):
            p.chains[0].set_length(0, 4.0 + extra)
            self.assertTrue(h.checkpoint(p))
            lengths.append(round(p.chains[0].length(0), 6))
        self.assertEqual(lengths, [4.5, 5.0, 5.5])
        back = []
        while h.can_undo():
            p = h.undo()
            back.append(round(p.chains[0].length(0), 6))
        self.assertEqual(back, [5.0, 4.5, 4.0])
        self.assertIsNone(h.undo())
        p = h.redo()
        self.assertAlmostEqual(p.chains[0].length(0), 4.5)

    def test_sem_mudanca_nao_grava(self):
        p = plan()
        h = history.History(p)
        self.assertFalse(h.checkpoint(p))
        self.assertFalse(h.can_undo())

    def test_nova_acao_apaga_o_refazer(self):
        p = plan()
        h = history.History(p)
        p.chains[0].set_length(0, 5.0)
        h.checkpoint(p)
        p = h.undo()
        self.assertTrue(h.can_redo())
        p.chains[0].set_length(0, 6.0)
        h.checkpoint(p)
        self.assertFalse(h.can_redo())

    def test_estado_desfeito_e_copia(self):
        p = plan()
        h = history.History(p)
        p.chains[0].set_length(0, 5.0)
        h.checkpoint(p)
        old = h.undo()
        old.chains[0].set_length(0, 9.0)          # mexer no estado devolvido não muda o histórico
        again = h.redo()
        self.assertAlmostEqual(again.chains[0].length(0), 5.0)

    def test_limite(self):
        p = plan()
        h = history.History(p, limit=3)
        for k in range(6):
            p.chains[0].set_length(0, 4.0 + k + 1)
            h.checkpoint(p)
        steps = 0
        while h.can_undo():
            h.undo()
            steps += 1
        self.assertEqual(steps, 3)


if __name__ == "__main__":
    unittest.main()
