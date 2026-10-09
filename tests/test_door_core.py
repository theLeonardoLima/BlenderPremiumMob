"""Testes da porta paramétrica (feature 010, T006; RN-01, RN-02, D-07): `caffmob_draw/openings/door_core.py`.

Referencial da caixa: x ao longo do vão (0 = borda esquerda do furo), y na espessura da parede (0 a `wall`),
z para cima (0 = piso). Medidas em metros.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.openings import door_core as dc


def by(parts, prefix):
    return [p for p in parts if p.name.startswith(prefix)]


def span(parts, axis):
    lo = min(p.lo[axis] for p in parts)
    hi = max(p.hi[axis] for p in parts)
    return lo, hi


class DoorCoreTest(unittest.TestCase):
    def setUp(self):
        self.parts = dc.door_parts(0.80, 2.10, 0.15)

    def test_furo_pela_folha(self):
        self.assertEqual(dc.hole_size(0.80, 2.10), (0.898, 2.159))
        self.assertEqual(dc.leaf_size(0.898, 2.159), (0.80, 2.10))
        self.assertEqual(dc.hole_size(0.80, 2.10, double=True), (1.701, 2.159))     # 2 folhas + folga do meio

    def test_folha_de_40_mm_a_8_mm_do_piso(self):
        leaf = [p for p in self.parts if p.role == dc.LEAF and p.material == dc.WOOD]
        x0, x1 = span(leaf, 0)
        y0, y1 = span([p for p in leaf if p.name.startswith("Folha_montante")], 1)
        z0, z1 = span(leaf, 2)
        self.assertAlmostEqual(x1 - x0, 0.80, places=6)
        self.assertAlmostEqual(y1 - y0, 0.04, places=6)
        self.assertAlmostEqual(z0, 0.008, places=6)
        self.assertAlmostEqual(z1, 2.108, places=6)
        self.assertAlmostEqual((y0 + y1) / 2, 0.075, places=6)              # no meio da parede de 150

    def test_marco_com_a_espessura_da_parede(self):
        marco = by(self.parts, "Marco_esquerdo")[0]
        self.assertAlmostEqual(marco.hi[1] - marco.lo[1], 0.15, places=6)
        self.assertAlmostEqual(marco.lo[0], 0.0, places=6)                   # encosta na borda do furo
        top = by(self.parts, "Marco_superior")[0]
        self.assertAlmostEqual(top.hi[2], 2.159, places=6)

    def test_guarnicoes_dos_dois_lados(self):
        g = by(self.parts, "Guarnicao_vertical")
        self.assertEqual(len(g), 4)
        self.assertTrue(any(p.hi[1] <= 0.0 + 1e-9 for p in g) and any(p.lo[1] >= 0.15 - 1e-9 for p in g))

    def test_ferragens(self):
        self.assertEqual(len(by(self.parts, "Dobradica_folha")), 3)
        handles = by(self.parts, "Alavanca_macaneta")
        self.assertEqual(len(handles), 2)
        self.assertTrue(all(abs(p.center[2] - 1.02) < 1e-9 for p in handles))

    def test_largura_maior_nao_distorce_ferragens(self):
        wide = dc.door_parts(0.90, 2.10, 0.15)
        for name in ("Alavanca_macaneta", "Dobradica_folha", "Roseta_macaneta"):
            self.assertEqual(by(wide, name)[0].size, by(self.parts, name)[0].size, name)
        leaf = [p for p in wide if p.role == dc.LEAF and p.material == dc.WOOD]
        self.assertAlmostEqual(span(leaf, 0)[1] - span(leaf, 0)[0], 0.90, places=6)

    def test_lado_da_dobradica_e_sentido(self):
        left = by(dc.door_parts(0.8, 2.1, 0.15, hinge='LEFT'), "Dobradica_folha")[0]
        right = by(dc.door_parts(0.8, 2.1, 0.15, hinge='RIGHT'), "Dobradica_folha")[0]
        self.assertLess(left.center[0], 0.2)
        self.assertGreater(right.center[0], 0.7)
        neg = by(dc.door_parts(0.8, 2.1, 0.15, side='NEG_Y'), "Dobradica_folha")[0]
        pos = by(dc.door_parts(0.8, 2.1, 0.15, side='POS_Y'), "Dobradica_folha")[0]
        self.assertLess(neg.center[1], 0.075)
        self.assertGreater(pos.center[1], 0.075)

    def test_dupla_e_vao_aberto(self):
        double = dc.door_parts(0.80, 2.10, 0.15, double=True)
        self.assertEqual(sorted({p.leaf for p in double if p.leaf is not None}), [0, 1])
        self.assertEqual(len(by(double, "Alavanca_macaneta")), 4)
        opening = dc.door_parts(0.80, 2.10, 0.15, open_door=True)
        self.assertFalse([p for p in opening if p.role in (dc.LEAF, dc.LEAF_HW)])
        self.assertTrue(by(opening, "Guarnicao_vertical"))

    def test_papeis(self):
        self.assertEqual({p.role for p in self.parts}, {dc.FRAME, dc.FRAME_HW, dc.LEAF, dc.LEAF_HW})


if __name__ == '__main__':
    unittest.main()
