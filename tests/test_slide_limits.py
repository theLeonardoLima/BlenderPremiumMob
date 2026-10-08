"""Testes dos limites da folha de correr (feature 007, T007): `caffmob_draw/aggregates/slide_limits.py`.

Caixas reais do arquivo de teste, em mm, no eixo do trilho (X): folha esquerda −676 a 16; direita −16 a 676; face
interna do marco em ±678.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import slide_limits as sl

LEFT, RIGHT, FRAME = (-676.0, 16.0), (-16.0, 676.0), (-678.0, 678.0)


class SlideLimitsTest(unittest.TestCase):
    def test_sentido_padrao_para_o_proprio_lado(self):
        self.assertEqual(sl.default_direction(LEFT, FRAME), 'NEG_X')
        self.assertEqual(sl.default_direction(RIGHT, FRAME), 'POS_X')

    def test_pouco_curso(self):
        self.assertTrue(sl.low_travel(2.0, 692.0))
        self.assertFalse(sl.low_travel(660.0, 692.0))

    def test_sobreposicao_dos_montantes(self):
        self.assertEqual(sl.rest_overlap(LEFT, RIGHT), 32.0)
        self.assertEqual(sl.rest_overlap((0.0, 1.0), (2.0, 3.0)), 0.0)

    def test_fechar_com_a_outra_em_repouso_volta_ao_arquivo(self):
        self.assertEqual(sl.close_stop(-1.0, 0.0), 0.0)
        self.assertEqual(sl.close_stop(1.0, 0.0), 0.0)

    def test_fechar_encosta_na_outra_que_veio_para_o_caminho(self):
        # folha esquerda abre para −X; a direita (invertida) andou 270 para −X: a esquerda para 270 antes do arquivo
        self.assertEqual(sl.close_stop(-1.0, -270.0), 270.0)
        # a direita andou para o próprio lado (+X): não atrapalha
        self.assertEqual(sl.close_stop(-1.0, 300.0), 0.0)
        # folha esquerda invertida (+X) e a direita para +X: a esquerda para no deslocamento dela
        self.assertEqual(sl.close_stop(1.0, 120.0), 120.0)


if __name__ == '__main__':
    unittest.main()
