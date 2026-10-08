"""Testes do referencial do grudar (feature 004, T017): `caffmob_draw/stick/frame.py`."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.stick import frame as fr

# Parede de 4 m, 150 mm de espessura (Y de 0 a +0,15), 2,6 m de altura.
WALL = ((0.0, 0.0, 0.0), (4.0, 0.15, 2.6))


def box_corners(lo, hi):
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def moved(corners, delta):
    return [(c[0] + delta[0], c[1] + delta[1], c[2] + delta[2]) for c in corners]


class FrameTest(unittest.TestCase):
    def test_ida_e_volta_nas_seis_faces(self):
        host = ((0.0, 0.0, 0.0), (0.6, 0.018, 2.0))
        item = box_corners((0.1, 0.1, 0.1), (0.3, 0.2, 0.4))
        for face in fr.FACES:
            frame = fr.box_frame(host, face)
            u, v, d = fr.params(frame, item)
            back = fr.shift(frame, item, u + 0.05, v - 0.02, 0.0)
            new = moved(item, back)
            nu, nv, nd = fr.params(frame, new)
            self.assertAlmostEqual(nu, u + 0.05, places=9, msg=face)
            self.assertAlmostEqual(nv, v - 0.02, places=9, msg=face)
            self.assertAlmostEqual(nd, 0.0, places=9, msg=face)

    def test_aereo_atras_continua_encostado_quando_a_parede_engrossa(self):
        # Aéreo grudado na face de trás (POS_Y): fundo em Y = 0,15, corpo para +Y.
        aereo = box_corners((1.0, 0.15, 1.5), (1.8, 0.50, 2.2))
        frame = fr.box_frame(WALL, 'POS_Y')
        u, v, d = fr.params(frame, aereo)
        self.assertAlmostEqual(d, 0.0)
        thicker = ((0.0, 0.0, 0.0), (4.0, 0.20, 2.6))
        new_frame = fr.box_frame(thicker, 'POS_Y')
        delta = fr.shift(new_frame, aereo, u, v, d)
        self.assertAlmostEqual(delta[1], 0.05, places=9)
        _u, _v, nd = fr.params(new_frame, moved(aereo, delta))
        self.assertLessEqual(abs(nd), 0.0001)

    def test_dez_mudancas_de_espessura_sem_erro_acumulado(self):
        aereo = box_corners((1.0, 0.15, 1.5), (1.8, 0.50, 2.2))
        u, v, d = fr.params(fr.box_frame(WALL, 'POS_Y'), aereo)
        for i in range(10):
            t = 0.10 + 0.013 * i
            frame = fr.box_frame(((0.0, 0.0, 0.0), (4.0, t, 2.6)), 'POS_Y')
            aereo = moved(aereo, fr.shift(frame, aereo, u, v, d))
        final = fr.box_frame(((0.0, 0.0, 0.0), (4.0, 0.15, 2.6)), 'POS_Y')
        aereo = moved(aereo, fr.shift(final, aereo, u, v, d))
        self.assertAlmostEqual(min(c[1] for c in aereo), 0.15, places=9)

    def test_frente_da_parede_e_neg_y(self):
        balcao = box_corners((0.5, -0.55, 0.0), (1.3, 0.0, 0.72))
        u, v, d = fr.params(fr.box_frame(WALL, 'NEG_Y'), balcao)
        self.assertAlmostEqual(d, 0.0)
        self.assertAlmostEqual(u, 0.5)

    def test_plano_inclinado(self):
        normal = (0.0, -math.sin(math.radians(30)), math.cos(math.radians(30)))
        frame = fr.plane_frame((0.0, 0.0, 0.0), normal)
        self.assertAlmostEqual(sum(a * b for a, b in zip(frame[3], normal)), 1.0)
        values = fr.frame_to_matrix(frame)
        again = fr.matrix_to_frame(values)
        for a, b in zip(frame, again):
            for x, y in zip(a, b):
                self.assertAlmostEqual(x, y)
        item = box_corners((-0.1, -0.1, 0.2), (0.1, 0.1, 0.4))
        new = moved(item, fr.shift(frame, item, distance=0.0))
        self.assertAlmostEqual(fr.params(frame, new)[2], 0.0, places=9)

    def test_fora_da_face(self):
        panel = ((0.0, 0.0, 0.0), (0.018, 0.6, 2.0))
        frame = fr.box_frame(panel, 'POS_X')
        extent = fr.face_extent(panel, 'POS_X')
        nicho = box_corners((0.018, 0.1, 1.0), (0.3, 0.4, 1.3))
        self.assertFalse(fr.out_of_face(frame, nicho, extent))
        shorter = ((0.0, 0.0, 0.0), (0.018, 0.6, 0.9))
        self.assertTrue(fr.out_of_face(fr.box_frame(shorter, 'POS_X'), nicho, fr.face_extent(shorter, 'POS_X')))
        self.assertFalse(fr.out_of_face(frame, nicho, None))

    def test_face_plana(self):
        flat = [(0, 0, 0), (1, 0, 0.0004), (1, 1, 0), (0, 1, -0.0003)]
        curved = [(0, 0, 0), (1, 0, 0.002), (1, 1, 0), (0, 1, 0)]
        self.assertTrue(fr.is_planar(flat, (0, 0, 1)))
        self.assertFalse(fr.is_planar(curved, (0, 0, 1)))
        self.assertFalse(fr.is_planar([], (0, 0, 1)))

    def test_escolha_do_tipo_de_face(self):
        self.assertEqual(fr.choose_face(WALL, (2.0, 0.0, 1.0), (0.0, -1.0, 0.0)), (fr.BOX_SIDE, 'NEG_Y'))
        self.assertEqual(fr.choose_face(WALL, (2.0, 0.15, 1.0), (0.0, 1.0, 0.0)), (fr.BOX_SIDE, 'POS_Y'))
        tilted = (0.0, -math.sin(math.radians(5)), math.cos(math.radians(5)))
        self.assertEqual(fr.choose_face(WALL, (2.0, 0.07, 2.6), tilted), (fr.PLANE, None))
        self.assertEqual(fr.choose_face(WALL, (2.0, 0.07, 1.0), (0.0, -1.0, 0.0)), (fr.PLANE, None))


if __name__ == "__main__":
    unittest.main()
