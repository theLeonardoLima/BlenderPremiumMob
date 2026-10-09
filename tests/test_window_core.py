"""Testes da janela paramétrica (feature 010, T007; RN-10, D-14): `caffmob_draw/openings/window_core.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.openings import window_core as wc


def span(parts, axis):
    return min(p.lo[axis] for p in parts), max(p.hi[axis] for p in parts)


class WindowCoreTest(unittest.TestCase):
    def setUp(self):
        self.parts = wc.window_parts(1.20, 1.00, 0.15)

    def test_marco_no_furo(self):
        frame = [p for p in self.parts if p.role == wc.FRAME and p.name.startswith("Marco")]
        self.assertEqual(span(frame, 0), (0.0, 1.2))
        self.assertEqual(span(frame, 2), (0.0, 1.0))
        self.assertTrue(all(abs(p.size[0] - wc.PROFILE) < 1e-9 or abs(p.size[2] - wc.PROFILE) < 1e-9
                            for p in frame))

    def test_duas_folhas_com_sobreposicao_e_vidro(self):
        leaves = sorted({p.leaf for p in self.parts if p.leaf is not None})
        self.assertEqual(leaves, [0, 1])
        a = span([p for p in self.parts if p.leaf == 0], 0)
        b = span([p for p in self.parts if p.leaf == 1], 0)
        self.assertGreater(a[1], b[0])                               # sobrepõem no meio
        glass = [p for p in self.parts if p.material == wc.GLASS]
        self.assertEqual(len(glass), 2)
        self.assertTrue(all(abs(p.size[1] - 0.004) < 1e-9 for p in glass))

    def test_folhas_em_trilhos_diferentes(self):
        y0 = span([p for p in self.parts if p.leaf == 0], 1)
        y1 = span([p for p in self.parts if p.leaf == 1], 1)
        self.assertTrue(y0[1] <= y1[0] + 1e-9 or y1[1] <= y0[0] + 1e-9)

    def test_peitoril_trilhos_puxadores(self):
        names = {p.name.split("_")[0] for p in self.parts}
        self.assertTrue({"Peitoril", "Trilho", "Puxador"} <= names, names)
        sill = [p for p in self.parts if p.name.startswith("Peitoril")]
        self.assertLessEqual(span(sill, 2)[1], 0.0 + 1e-9)        # embaixo do furo

    def test_tamanho_maior(self):
        wide = wc.window_parts(1.60, 1.20, 0.20)
        frame = [p for p in wide if p.name.startswith("Marco")]
        self.assertEqual(span(frame, 0), (0.0, 1.6))
        self.assertAlmostEqual(span(frame, 1)[1] - span(frame, 1)[0], 0.20)


if __name__ == '__main__':
    unittest.main()
