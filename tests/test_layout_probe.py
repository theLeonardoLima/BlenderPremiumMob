"""Testes da camada falsa de layout (feature 005, T009): `caffmob_draw/ui/layout_probe.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.ui import layout_probe as lp


class FakePanel:
    bl_label = "Painel"

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        box = layout.box()
        row = box.row(align=True)
        op = row.operator("caffmob.geometry_create", text="Placa", icon='MESH_PLANE')
        op.kind = 'PLACA'
        header, body = layout.panel_prop(context, "open_group")
        body.column().operator("caffmob.check_collisions").scope = 'ALL'
        layout.operator_menu_enum("caffmob.customize_set_style", "style").path = "o0"
        layout.menu("HOME_BUILDER_MT_wall_commands")
        layout.prop(context, "collision_global")
        layout.template_list("UL", "", context, "items", context, "index")
        layout.separator()


class Ctx:
    collision_global = True


class ProbeTest(unittest.TestCase):
    def test_registra_operadores_menus_e_props_com_a_secao(self):
        rec = lp.Recorder()
        panel = FakePanel()
        panel.layout = lp.Probe(rec)
        with rec.section("Construir"):
            panel.draw(Ctx())
        ops = rec.operators()
        self.assertEqual([o['name'] for o in ops],
                         ["caffmob.geometry_create", "caffmob.check_collisions", "caffmob.customize_set_style"])
        self.assertEqual(ops[0]['args'], {'kind': 'PLACA'})
        self.assertEqual(ops[2]['args'], {'path': 'o0'})
        self.assertTrue(all(o['section'] == "Construir" for o in ops))
        self.assertIn('HOME_BUILDER_MT_wall_commands', [r['name'] for r in rec.records if r['kind'] == 'menu'])
        self.assertIn('collision_global', [r['name'] for r in rec.records if r['kind'] == 'prop'])

    def test_secoes_aninhadas_e_mapa(self):
        rec = lp.Recorder()
        probe = lp.Probe(rec)
        with rec.section("Verificar"):
            with rec.section("Colisões"):
                probe.operator("caffmob.check_collisions")
        with rec.section("Selecionado"):
            probe.operator("caffmob.check_collisions")
        self.assertEqual(lp.operator_sections(rec),
                         {"caffmob.check_collisions": ["Selecionado", "Verificar › Colisões"]})

    def test_atributos_de_estado(self):
        probe = lp.Probe()
        probe.enabled = False
        self.assertFalse(probe.enabled)
        self.assertEqual(probe.operator_context, 'INVOKE_DEFAULT')


if __name__ == "__main__":
    unittest.main()
