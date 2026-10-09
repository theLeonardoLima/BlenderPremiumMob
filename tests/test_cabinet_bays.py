"""Testes do Número de vãos (feature 008, T007): `caffmob_draw/cabinet_editor/bays.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import bays, divisions as dv

T = 0.015
ROOT = {'s0': dv.Box((0.015, 0.0, 0.015), (0.785, 0.535, 2.235))}       # interno 770


class BaysTest(unittest.TestCase):
    def test_interno_770(self):
        self.assertAlmostEqual(ROOT['s0'].size(0), 0.770)

    def test_dois_vaos(self):
        plan = bays.plan(ROOT['s0'], 2, T)
        self.assertEqual([p[0] for p in plan], ['s0'])
        self.assertAlmostEqual(plan[0][1], (0.770 - T) / 2)

    def test_tres_vaos_iguais(self):
        divs = bays.apply(ROOT, [], 3, T)
        self.assertEqual([d.space for d in divs], ['s0', 's0.b'])
        leaves, _c, _o = dv.resolve(ROOT, divs)
        widths = sorted(round(b.size(0), 6) for b in leaves.values())
        self.assertEqual(len(set(widths)), 1)

    def test_reduzir_lista_removidas_e_preserva_comuns(self):
        divs = bays.apply(ROOT, [], 3, T)
        common = dv.Division("c1", 's0.a', dv.HORIZONTAL, 0.3, T)
        divs = divs + [common]
        rest = bays.apply(ROOT, divs, 2, T)
        self.assertEqual(bays.count(rest), 2)
        self.assertIn("c1", [d.uid for d in rest])
        self.assertEqual(bays.removed(divs, rest), [d.uid for d in divs if d.bay and d.space == 's0.b'])

    def test_um_vao(self):
        self.assertEqual(bays.apply(ROOT, bays.apply(ROOT, [], 3, T), 1, T), [])


if __name__ == '__main__':
    unittest.main()
