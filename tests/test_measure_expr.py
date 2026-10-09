"""Testes da expressão de medida (feature 009, T005; RN-04): `caffmob_draw/data/expr.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.data import expr, units


class ExprTest(unittest.TestCase):
    def mm(self, text, unit='MM'):
        return round(expr.evaluate(text, unit) * 1000.0, 6)

    def test_numeros_e_contas(self):
        self.assertEqual(self.mm("100"), 100.0)
        self.assertEqual(self.mm("2*8"), 16.0)
        self.assertEqual(self.mm("200/2"), 100.0)
        self.assertEqual(self.mm("(3000-150)/2"), 1425.0)
        self.assertEqual(self.mm("1,5m+20"), 1520.0)
        self.assertEqual(self.mm("2.5 * 4"), 10.0)
        self.assertEqual(self.mm("-(-50)"), 50.0)
        self.assertEqual(self.mm("10cm*2"), 200.0)

    def test_unidade_da_cena(self):
        self.assertEqual(self.mm("2*8", 'CM'), 160.0)

    def test_invalidos(self):
        for text in ("10/0", "2*", "((1)", "abc", "", "5-5", "-3", "1+" * 40, "2000m"):
            with self.subTest(text=text), self.assertRaises(ValueError) as ctx:
                expr.evaluate(text, 'MM')
            self.assertTrue(str(ctx.exception).startswith(expr.tr("Valor Inválido")), str(ctx.exception))

    def test_tem_conta(self):
        self.assertTrue(expr.has_operator("2*8"))
        self.assertFalse(expr.has_operator("1,5m"))
        self.assertFalse(expr.has_operator("-5"))

    def test_parse_length_delega(self):
        self.assertAlmostEqual(units.parse_length("2*8", 'MM', allow_zero=False), 0.016)
        self.assertAlmostEqual(units.parse_length("1,5 m", 'MM'), 1.5)

    def test_previa(self):
        self.assertEqual(expr.preview("2*8", 'MM'), "= 16 mm")
        self.assertEqual(expr.preview("100", 'MM'), "")
        self.assertEqual(expr.preview("10/0", 'MM'), expr.tr("Valor Inválido"))


if __name__ == '__main__':
    unittest.main()
