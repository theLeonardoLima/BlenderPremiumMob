"""Testes da validação do editor de armário (feature 004, T020): `caffmob_draw/cabinet_editor/validate.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import elevation as el
from caffmob_draw.cabinet_editor import validate as va

LIMITS = va.limits_for({'width': (0.15, 1.2)})


class ValidateTest(unittest.TestCase):
    def test_faixa_estreitada_pela_biblioteca(self):
        self.assertEqual(LIMITS['width'], (0.15, 1.2))
        self.assertEqual(LIMITS['depth'], va.DEFAULT_LIMITS['depth'])

    def test_dim_001_002_003(self):
        value, msgs = va.parse_dimension('width', '', LIMITS)
        self.assertIsNone(value)
        self.assertEqual(msgs[0].code, 'DIM-001')
        value, msgs = va.parse_dimension('width', 'abc', LIMITS)
        self.assertEqual(msgs[0].code, 'DIM-002')
        value, msgs = va.parse_dimension('width', '50', LIMITS)
        self.assertAlmostEqual(value, 0.05)
        self.assertEqual(msgs[0].code, 'DIM-003')
        self.assertEqual(msgs[0].range, "150 mm – 1200 mm")
        self.assertTrue(msgs[0].blocks)
        value, msgs = va.parse_dimension('width', '600', LIMITS)
        self.assertAlmostEqual(value, 0.6)
        self.assertEqual(msgs, [])

    def test_geo_001_prateleira_acima_do_topo(self):
        shelf = el.Part('Shelf', el.SHELF, (0.018, -0.5, 0.71), (0.78, 0.0, 0.728))
        door = el.Part('Door', el.FRONT, (0.0, -0.57, 0.0), (0.8, -0.55, 0.7225))
        pull = el.Part('Pull', el.PART, (0.3, -0.62, 0.3), (0.5, -0.57, 0.32))
        msgs = va.outside_volume((0.8, 0.55, 0.72), [shelf, door, pull])
        self.assertEqual([(m.code, m.component, m.severity) for m in msgs],
                         [('GEO-001', 'Shelf', va.ERROR), ('GEO-001', 'Door', va.WARNING)])

    def test_geo_002_divisoes_sobrepostas(self):
        a = el.Part('Shelf', el.SHELF, (0.0, -0.5, 0.30), (0.8, 0.0, 0.318))
        b = el.Part('Shelf.001', el.SHELF, (0.0, -0.5, 0.31), (0.8, 0.0, 0.328))
        c = el.Part('Divider', el.DIVIDER, (0.4, -0.5, 0.318), (0.418, 0.0, 0.7))    # só encosta em Shelf
        msgs = va.internal_overlaps([a, b, c])
        self.assertEqual([(m.code, m.component, m.value) for m in msgs], [('GEO-002', 'Divider', 'Shelf.001'),
                                                                          ('GEO-002', 'Shelf', 'Shelf.001')])

    def test_so_erro_bloqueia(self):
        warning = va.unsupported('INTERIOR', 'sem gavetas internas')
        self.assertFalse(va.blocking([warning]))
        self.assertTrue(va.blocking([warning, va.check_dimension('width', 0.05, LIMITS)[0]]))
        ordered = va.sort_messages([warning, va.check_dimension('width', 0.05, LIMITS)[0]])
        self.assertEqual(ordered[0].code, 'DIM-003')


if __name__ == "__main__":
    unittest.main()
