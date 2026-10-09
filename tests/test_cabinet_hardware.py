"""Testes da lista de ferragens e da furação (feature 008, T054): `cutting/hardware.py`, `cutting/drilling.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cutting import drilling, hardware


class HardwareTest(unittest.TestCase):
    def test_soma_por_codigo_e_modulo(self):
        items = [('PE_PLASTICO', 'a'), ('PE_PLASTICO', 'a'), ('PE_PLASTICO', 'b'), ('PISTAO', 'a')]
        rows = hardware.summarize(items)
        self.assertEqual([(r['module_uid'], r['code'], r['quantity']) for r in rows],
                         [('a', 'PE_PLASTICO', 2), ('a', 'PISTAO', 1), ('b', 'PE_PLASTICO', 1)])
        self.assertEqual(rows[0]['name'], "Pé plástico")

    def test_corredicas_por_gaveta(self):
        self.assertEqual(hardware.drawer_items(4, 'm', blum=False), [('CORREDICA', 'm')] * 4)
        self.assertEqual(hardware.drawer_items(2, 'm', blum=True), [('CORREDICA_BLUM', 'm')] * 2)


class DrillingTest(unittest.TestCase):
    def test_linhas_da_prateleira_movel(self):
        # prateleira móvel (horizontal) num subvão de Z 0,1 a 0,7 e Y 0 a 0,54: furos nas faces esquerda e direita
        lines = drilling.pin_lines(((0.0, 0.0, 0.1), (0.77, 0.54, 0.7)), 'HORIZONTAL')
        self.assertEqual(sorted({ln['side'] for ln in lines}), ['LEFT', 'RIGHT'])
        self.assertEqual(len(lines), 4)                    # frente e trás em cada lado
        self.assertEqual(sorted({round(ln['depth_pos'], 3) for ln in lines}), [0.037, 0.503])
        self.assertTrue(all(ln['axis'] == 'Z' and ln['start'] == 0.1 and ln['end'] == 0.7 for ln in lines))

    def test_divisoria_movel_vertical(self):
        lines = drilling.pin_lines(((0.0, 0.0, 0.0), (0.77, 0.54, 0.7)), 'VERTICAL')
        self.assertEqual(sorted({ln['side'] for ln in lines}), ['BOTTOM', 'TOP'])
        self.assertTrue(all(ln['axis'] == 'X' for ln in lines))

    def test_entrada_do_json(self):
        entry = drilling.to_json(side_face='TOP', front_mm=37.0, start_mm=120.0, end_mm=560.0, source="Divisória 2")
        self.assertEqual(entry, {"kind": "SHELF_PIN_LINE", "face": "TOP", "diameter_mm": 5.0, "depth_mm": 10.0,
                                 "x_mm": 37.0, "y_start_mm": 120.0, "y_end_mm": 560.0, "pitch_mm": 32.0,
                                 "source_name": "Divisória 2"})


if __name__ == '__main__':
    unittest.main()
