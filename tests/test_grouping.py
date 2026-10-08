"""Testes da sugestão de grupos (feature 007, T006): `caffmob_draw/aggregates/grouping.py`."""

import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import grouping as gr

OBJ = Path(__file__).resolve().parents[1] / "_reversa_forward/007-janela-obj-folhas-colisao/inputs/janela_preta_1400mm.obj"


def obj_names():
    return [line.split()[1] for line in OBJ.read_text().splitlines() if line.startswith("o ")]


class GroupingTest(unittest.TestCase):
    def test_janela_do_arquivo(self):
        groups = gr.suggest(obj_names())
        summary = [(name, role, len(members)) for name, role, members in groups]
        self.assertEqual(summary, [("Folha_Direita", 'LEAF', 15), ("Folha_Esquerda", 'LEAF', 15),
                                   ("Esquadria", 'FRAME', 16)])

    def test_sufixo_do_blender(self):
        groups = gr.suggest(["Folha_Esquerda_Vidro.001", "Folha_Esquerda_Superior", "Marco.002"])
        self.assertEqual([(n, len(m)) for n, _r, m in groups], [("Folha_Esquerda", 2), ("Esquadria", 1)])

    def test_sem_folha_vira_um_grupo(self):
        groups = gr.suggest(["Puxador_Base", "Puxador_Haste"])
        self.assertEqual([(n, r, len(m)) for n, r, m in groups], [("Esquadria", 'FRAME', 2)])

    def test_ingles_e_vazio(self):
        self.assertEqual([n for n, _r, _m in gr.suggest(["Sash_Left_Glass", "Leaf_A_Top", "Frame"])],
                         ["Leaf_A", "Sash_Left", "Esquadria"])
        self.assertEqual(gr.suggest([]), [])


if __name__ == '__main__':
    unittest.main()
