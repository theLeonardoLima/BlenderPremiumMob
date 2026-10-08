"""Testes da varredura de abertura com parada no contato (T015): `caffmob_draw/aggregates/sweep.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import sweep as sw


class SweepTest(unittest.TestCase):
    def test_para_no_contato_do_giro(self):
        calls = []

        def hit(value):
            calls.append(value)
            return "Parede" if value >= 63.4 else None

        reached, contact = sw.sweep(0.0, 180.0, hit, sw.SWING_STEP, sw.SWING_TOLERANCE)
        self.assertEqual(contact, "Parede")
        self.assertLessEqual(reached, 63.4)
        self.assertGreater(reached, 63.4 - sw.SWING_TOLERANCE)

    def test_correr(self):
        reached, contact = sw.sweep(0.0, 0.8, lambda d: d >= 0.5, sw.SLIDE_STEP, sw.SLIDE_TOLERANCE)
        self.assertTrue(contact)
        self.assertAlmostEqual(reached, 0.5, delta=sw.SLIDE_TOLERANCE)

    def test_fechar_e_livre(self):
        def hit(_value):
            raise AssertionError("fechar não testa contato")
        self.assertEqual(sw.sweep(60.0, 10.0, hit, 2.0, 0.25), (10.0, None))

    def test_sem_obstaculo_chega_ao_maximo(self):
        self.assertEqual(sw.sweep(0.0, 90.0, lambda _v: None, 2.0, 0.25), (90.0, None))

    def test_ja_encostada_nao_avanca(self):
        reached, contact = sw.sweep(30.0, 90.0, lambda v: v > 30.0, 2.0, 0.25)
        self.assertTrue(contact)
        self.assertAlmostEqual(reached, 30.0, delta=0.25)

    # Feature 007 (T008): fechar com contato e com limite mínimo -----------------------------------------------
    def test_fechar_com_contato_para(self):
        reached, contact = sw.sweep(0.6, 0.0, lambda d: "Marco" if d <= 0.2 else None, sw.SLIDE_STEP,
                                    sw.SLIDE_TOLERANCE, close=True)
        self.assertEqual(contact, "Marco")
        self.assertAlmostEqual(reached, 0.2, delta=sw.SLIDE_TOLERANCE)

    def test_fechar_com_limite_minimo(self):
        reached, contact = sw.sweep(0.6, 0.0, lambda _d: None, sw.SLIDE_STEP, sw.SLIDE_TOLERANCE, close=True,
                                    floor=0.27, floor_contact="Folha_Direita")
        self.assertEqual((round(reached, 6), contact), (0.27, "Folha_Direita"))

    def test_fechar_livre_ate_zero(self):
        self.assertEqual(sw.sweep(0.6, 0.0, lambda _d: None, sw.SLIDE_STEP, sw.SLIDE_TOLERANCE, close=True),
                         (0.0, None))


if __name__ == "__main__":
    unittest.main()
