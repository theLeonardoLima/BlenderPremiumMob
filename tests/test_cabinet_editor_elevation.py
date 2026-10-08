"""Testes da vista frontal do editor de armário (feature 004, T019): `caffmob_draw/cabinet_editor/elevation.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import elevation as el


def part(name, kind, lo, hi):
    return el.Part(name, kind, lo, hi)


# Balcão de 800 mm com 2 vãos: laterais, divisória central, prateleira no vão 1 e duas portas.
PARTS = [
    part('Left Side', el.STRUCTURE, (0.0, -0.55, 0.0), (0.018, 0.0, 0.72)),
    part('Right Side', el.STRUCTURE, (0.782, -0.55, 0.0), (0.8, 0.0, 0.72)),
    part('Divider', el.DIVIDER, (0.391, -0.53, 0.018), (0.409, 0.0, 0.702)),
    part('Shelf', el.SHELF, (0.018, -0.53, 0.35), (0.391, 0.0, 0.368)),
    part('Door L', el.FRONT, (0.0, -0.57, 0.0), (0.4, -0.55, 0.72)),
    part('Door R', el.FRONT, (0.4, -0.57, 0.0), (0.8, -0.55, 0.72)),
]


class ElevationTest(unittest.TestCase):
    def test_retangulos_e_limites(self):
        self.assertEqual(PARTS[3].rect, (0.018, 0.35, 0.391, 0.368))
        self.assertEqual(el.bounds(PARTS), (0.0, 0.0, 0.8, 0.72))
        self.assertIsNone(el.bounds([]))
        order = [p.name for p in el.draw_order(PARTS)]
        self.assertEqual(order[-2:], ['Door L', 'Door R'])

    def test_clique_pega_o_mais_a_frente(self):
        self.assertEqual(el.hit(PARTS, 0.2, 0.36), 'Door L')
        inner = [p for p in PARTS if p.kind != el.FRONT]
        self.assertEqual(el.hit(inner, 0.2, 0.36), 'Shelf')
        self.assertIsNone(el.hit(PARTS, 2.0, 2.0))

    def test_diferenca_lista_o_que_mudou_sozinho(self):
        after = [
            PARTS[0],
            part('Right Side', el.STRUCTURE, (0.582, -0.55, 0.0), (0.6, 0.0, 0.72)),      # moveu
            part('Divider', el.DIVIDER, (0.291, -0.53, 0.018), (0.309, 0.0, 0.702)),     # moveu
            part('Shelf', el.SHELF, (0.018, -0.53, 0.35), (0.291, 0.0, 0.368)),          # mudou de tamanho
            part('Door L', el.FRONT, (0.0, -0.57, 0.0), (0.3, -0.55, 0.72)),
            part('Drawer', el.FRONT, (0.3, -0.57, 0.0), (0.6, -0.55, 0.36)),             # entrou
        ]
        changes = el.diff(PARTS, after, targets=['Door L'])
        self.assertEqual(changes, [('Divider', el.MOVED), ('Door R', el.REMOVED), ('Drawer', el.ADDED),
                                   ('Right Side', el.MOVED), ('Shelf', el.RESIZED)])
        self.assertEqual(el.diff(PARTS, PARTS), [])

    def test_tipo_pelo_codigo_da_peca(self):
        self.assertEqual(el.kind_from_role('POR'), el.FRONT)
        self.assertEqual(el.kind_from_role('PRAT'), el.SHELF)
        self.assertEqual(el.kind_from_role('LAT'), el.STRUCTURE)
        self.assertEqual(el.kind_from_role(None), el.PART)


if __name__ == "__main__":
    unittest.main()
