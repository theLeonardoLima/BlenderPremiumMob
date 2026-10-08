"""Testes da unidade de importação (feature 007, T005): `caffmob_draw/aggregates/import_units.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import import_units as iu


class ImportUnitsTest(unittest.TestCase):
    def test_escala_por_unidade(self):
        self.assertEqual(iu.scale_for('MM', 1.0), 0.001)
        self.assertEqual(iu.scale_for('CM', 1.0), 0.01)
        self.assertEqual(iu.scale_for('M', 1400.0), 1.0)
        self.assertAlmostEqual(iu.scale_for('IN', 1.0), 0.0254)

    def test_sugestao_automatica(self):
        self.assertEqual(iu.suggest(1400.0), 'MM')        # a janela do arquivo de teste
        self.assertEqual(iu.suggest(50.0), 'M')           # no limite ainda é metro
        self.assertEqual(iu.suggest(0.8), 'M')
        self.assertEqual(iu.scale_for('AUTO', 1400.0), 0.001)
        self.assertEqual(iu.scale_for('AUTO', 2.1), 1.0)


if __name__ == '__main__':
    unittest.main()
