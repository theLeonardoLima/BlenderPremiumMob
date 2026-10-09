"""Testes das cotas e do passo (feature 008, T011): `caffmob_draw/cabinet_editor/position.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import divisions as dv
from caffmob_draw.cabinet_editor import position as po

SPACE = dv.Box((0.0, 0.0, 0.0), (0.768, 0.540, 0.690))
T = 0.015


class PositionTest(unittest.TestCase):
    def test_cotas_horizontal(self):
        d = dv.Division("a", 's0', dv.HORIZONTAL, 0.3, T, use_front=True, front=0.02)
        c = po.cotas(SPACE, d)
        self.assertAlmostEqual(c['front'], 0.02)
        self.assertAlmostEqual(c['back'], 0.0)
        self.assertAlmostEqual(c['low'], 0.3)
        self.assertAlmostEqual(c['high'], 0.690 - 0.3 - T)

    def test_editar_cota(self):
        d = dv.Division("a", 's0', dv.VERTICAL, 0.3, T)
        self.assertAlmostEqual(po.offset_from_cota(SPACE, d, 'low', 0.4), 0.4)
        self.assertAlmostEqual(po.offset_from_cota(SPACE, d, 'high', 0.4), 0.768 - 0.4 - T)

    def test_passo(self):
        d = dv.Division("a", 's0', dv.VERTICAL, 0.3, T)
        self.assertAlmostEqual(po.step_move(SPACE, d, +1, 0.01, 0.0, first=True), 0.31)
        self.assertAlmostEqual(po.step_move(SPACE, d, +1, 0.01, 0.05, first=True), 0.35)
        self.assertAlmostEqual(po.step_move(SPACE, d, -1, 0.01, 0.05, first=False), 0.29)
        far = dv.Division("a", 's0', dv.VERTICAL, 0.70, T)
        self.assertAlmostEqual(po.step_move(SPACE, far, +1, 0.1, 0.0, first=False), 0.768 - T - dv.MIN_SPACE)


if __name__ == '__main__':
    unittest.main()
