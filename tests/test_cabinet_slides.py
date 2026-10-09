"""Testes dos deslizantes (feature 008, T008): `caffmob_draw/cabinet_editor/slides.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import divisions as dv
from caffmob_draw.cabinet_editor import slides as sl

INNER = dv.Box((0.015, 0.0, 0.015), (1.585, 0.535, 2.235))          # armário de 1600


class SlidesTest(unittest.TestCase):
    def test_largura_das_folhas_com_sobreposicao(self):
        lay = sl.layout(INNER, 2, 'SLIDE_LISA')
        w = (1.570 + sl.OVERLAP) / 2
        self.assertEqual(len(lay.leaves), 2)
        for leaf in lay.leaves:
            self.assertAlmostEqual(leaf.box[1][0] - leaf.box[0][0], w)
        self.assertAlmostEqual(lay.leaves[1].box[0][0] - lay.leaves[0].box[1][0], -sl.OVERLAP)

    def test_trilhos_escalonados(self):
        lay = sl.layout(INNER, 3, 'SLIDE_LISA')
        fronts = sorted(round(leaf.box[0][1], 6) for leaf in lay.leaves)
        self.assertEqual(fronts, [round(i * sl.PITCH, 6) for i in range(3)])
        self.assertEqual(len(lay.tracks), 2)
        self.assertAlmostEqual(lay.tracks[0].box[1][1], 3 * sl.PITCH)

    def test_profundidade_minima(self):
        self.assertIsNone(sl.missing_depth(INNER, 2))
        shallow = dv.Box((0.0, 0.0, 0.0), (1.0, 0.06, 2.0))
        self.assertAlmostEqual(sl.missing_depth(shallow, 3), 3 * sl.PITCH + sl.DEPTH_MARGIN)

    def test_invertido_troca_a_folha_da_frente(self):
        normal = sl.layout(INNER, 2, 'SLIDE_LISA')
        inverted = sl.layout(INNER, 2, 'SLIDE_LISA', invert=True)
        self.assertEqual(normal.leaves[0].track, 0)
        self.assertEqual(inverted.leaves[0].track, 1)

    def test_rasgo_por_estilo(self):
        self.assertIsNotNone(sl.layout(INNER, 2, 'SLIDE_GOLA_VERTICAL').leaves[0].groove)
        self.assertIsNone(sl.layout(INNER, 2, 'SLIDE_LISA').leaves[0].groove)


if __name__ == '__main__':
    unittest.main()
