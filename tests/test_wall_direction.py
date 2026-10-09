"""Testes da direção travada do lápis (feature 009, T007; RN-05, RN-06): `caffmob_draw/walls2d/direction.py`."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.data import expr
from caffmob_draw.walls2d import direction as dr


def close(a, b):
    return all(abs(p - q) < 1e-9 for p, q in zip(a, b))


class DirectionTest(unittest.TestCase):
    def test_sequencia_na_direcao_atual(self):
        point, angle = (0.0, 0.0), dr.initial_direction((0.0, 0.0), (0.9, 0.02))
        self.assertEqual(angle, 0.0)
        for text in ("100", "285", "2*8", "200/2", "2000"):
            point = dr.next_point(point, angle, expr.evaluate(text, 'MM'))
        self.assertTrue(close(point, (2.501, 0.0)), point)

    def test_setas(self):
        self.assertEqual(dr.arrow_direction('RIGHT_ARROW'), 0.0)
        self.assertAlmostEqual(dr.arrow_direction('UP_ARROW'), math.pi / 2)
        self.assertAlmostEqual(dr.arrow_direction('LEFT_ARROW'), math.pi)
        self.assertAlmostEqual(dr.arrow_direction('DOWN_ARROW'), 3 * math.pi / 2)
        self.assertIsNone(dr.arrow_direction('A'))
        self.assertTrue(close(dr.next_point((2.501, 0.0), dr.arrow_direction('UP_ARROW'), 1.2), (2.501, 1.2)))

    def test_clique_passa_a_direcao_do_trecho(self):
        self.assertAlmostEqual(dr.segment_direction((2.801, 1.2), (1.0, 1.2)), math.pi)
        self.assertTrue(close(dr.next_point((1.0, 1.2), math.pi, 0.5), (0.5, 1.2)))

    def test_inicial_com_trava_ortogonal_e_livre(self):
        self.assertAlmostEqual(dr.initial_direction((0, 0), (0.01, 1.0)), math.pi / 2)
        free = dr.initial_direction((0, 0), (1.0, 1.0))
        self.assertAlmostEqual(free, math.pi / 4)
        self.assertIsNone(dr.initial_direction((0, 0), (0, 0)))

    def test_texto(self):
        self.assertEqual(dr.label(0.0), "→ 0°")
        self.assertEqual(dr.label(math.pi / 2), "↑ 90°")
        self.assertEqual(dr.label(math.pi / 4), "45°")


if __name__ == '__main__':
    unittest.main()
