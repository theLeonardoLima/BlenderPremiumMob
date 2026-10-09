"""Testes do alinhamento da mira (feature 009, T006; RN-02): `caffmob_draw/walls2d/inference.py`."""

import random
import time
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import inference

TOL = 8 / 1000.0                  # 8 px numa vista de 1 px = 1 mm


class InferenceTest(unittest.TestCase):
    def test_trava_y_no_canto_do_outro_lado(self):
        idx = inference.Index([(0.0, 0.0), (3.0, 2.0)])
        x, ref_x, y, ref_y = idx.query((5.0, 2.003), TOL)
        self.assertIsNone(x)
        self.assertEqual((y, ref_y), (2.0, (3.0, 2.0)))

    def test_trava_x(self):
        idx = inference.Index([(1.2, 0.0)])
        x, ref_x, y, _ref_y = idx.query((1.205, 4.0), TOL)
        self.assertEqual((x, ref_x, y), (1.2, (1.2, 0.0), None))

    def test_duas_travas_e_a_mais_proxima(self):
        idx = inference.Index([(1.0, 0.0), (1.006, 9.0), (7.0, 3.0)])
        x, ref_x, y, ref_y = idx.query((1.005, 3.002), TOL)
        self.assertEqual(x, 1.006)
        self.assertEqual(ref_x, (1.006, 9.0))
        self.assertEqual(y, 3.0)

    def test_fora_da_tolerancia(self):
        idx = inference.Index([(0.0, 0.0)])
        self.assertEqual(idx.query((0.009, 0.0091), TOL), (None, None, None, None))

    def test_ignora_o_proprio_ponto_e_vazio(self):
        self.assertEqual(inference.Index([]).query((1.0, 1.0), TOL), (None, None, None, None))
        idx = inference.Index([(1.0, 1.0)])
        self.assertEqual(idx.query((1.0, 1.0), TOL, exclude=[(1.0, 1.0)]), (None, None, None, None))

    def test_desempenho_2000_vertices(self):
        rnd = random.Random(9)
        idx = inference.Index([(rnd.uniform(0, 50), rnd.uniform(0, 50)) for _ in range(2000)])
        start = time.perf_counter()
        for _ in range(200):
            idx.query((rnd.uniform(0, 50), rnd.uniform(0, 50)), TOL)
        self.assertLess((time.perf_counter() - start) / 200, 0.002)


if __name__ == '__main__':
    unittest.main()
