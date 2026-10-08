"""Testes do núcleo da estrutura (feature 006, T006): `caffmob_draw/cabinet_editor/structure.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import structure as st

T = 0.015
THICK = {role: T for role in st.ROLES}
W, H, D = 0.8, 0.72, 0.56


def inner(states):
    return st.layout(W, H, D, THICK, states)[1]


class StructureTest(unittest.TestCase):
    def test_caixa_completa_igual_ao_legado(self):
        boxes, box = st.layout(W, H, D, THICK, {})
        self.assertEqual(sorted(boxes), sorted(st.ROLES))
        self.assertAlmostEqual(box[0][0], -W / 2 + T)
        self.assertAlmostEqual(box[1][0], W / 2 - T)
        self.assertAlmostEqual(box[1][1], -T)
        self.assertAlmostEqual(box[0][2], T)
        self.assertAlmostEqual(box[1][2], H - T)

    def test_keep_tira_a_chapa_e_mantem_o_vao(self):
        states = {'RIGHT': st.RoleState(removed=True)}
        boxes, box = st.layout(W, H, D, THICK, states)
        self.assertNotIn('RIGHT', boxes)
        self.assertEqual(box, inner({}))
        self.assertAlmostEqual(boxes['TOP'][1][0], W / 2 - T)       # o tampo não avança

    def test_extend_avanca_as_vizinhas(self):
        states = {'RIGHT': st.RoleState(removed=True, mode=st.EXTEND)}
        boxes, box = st.layout(W, H, D, THICK, states)
        self.assertAlmostEqual(boxes['TOP'][1][0], W / 2)
        self.assertAlmostEqual(boxes['BOTTOM'][1][0], W / 2)
        self.assertAlmostEqual(box[1][0] - box[0][0], W - T)       # vão 15 mm mais largo

    def test_extend_da_base_desce_o_fundo(self):
        boxes, box = st.layout(W, H, D, THICK, {'BOTTOM': st.RoleState(removed=True, mode=st.EXTEND)})
        self.assertAlmostEqual(boxes['BACK'][0][2], 0.0)
        self.assertAlmostEqual(box[0][2], 0.0)

    def test_shrink_reduz_a_medida_e_mantem_o_vao(self):
        delta, shift = st.shrink_change('RIGHT', T)
        self.assertEqual(delta, {'width': -T})
        states = {'RIGHT': st.RoleState(removed=True, mode=st.SHRINK)}
        _b, box = st.layout(W - T, H, D, THICK, states)
        self.assertAlmostEqual(box[1][0] - box[0][0], W - 2 * T)   # vão igual ao original
        # deslocada pela raiz, a lateral esquerda continua no mesmo lugar
        self.assertAlmostEqual(-(W - T) / 2 + shift[0], -W / 2)

    def test_shrink_do_fundo_mantem_a_frente(self):
        delta, shift = st.shrink_change('BACK', T)
        self.assertEqual(delta, {'depth': -T})
        self.assertAlmostEqual(-(D - T) + shift[1], -D)

    def test_espessura_por_componente(self):
        thick = dict(THICK, TOP=0.018)
        boxes, box = st.layout(W, H, D, thick, {})
        self.assertAlmostEqual(boxes['TOP'][0][2], H - 0.018)
        self.assertAlmostEqual(box[1][2], H - 0.018)

    def test_modo_nao_suportado_cai_em_keep(self):
        caps = {st.KEEP: None, st.EXTEND: "não dá", st.SHRINK: "não dá"}
        self.assertEqual(st.allowed_mode(st.EXTEND, caps), (st.KEEP, "não dá"))
        self.assertEqual(st.allowed_mode(st.KEEP, caps), (st.KEEP, None))

    def test_str_002(self):
        self.assertEqual(st.check_thickness('TOP', 0.0), [])
        self.assertEqual(st.check_thickness('TOP', 0.018), [])
        msgs = st.check_thickness('TOP', 0.1)
        self.assertEqual(msgs[0].code, 'STR-002')
        self.assertTrue(msgs[0].blocks)

    def test_dicionario_ida_e_volta_sem_padroes(self):
        states = {'TOP': st.RoleState(thickness=0.018), 'LEFT': st.RoleState()}
        data = st.state_to_dict(states)
        self.assertEqual(list(data), ['TOP'])
        self.assertEqual(st.state_from_dict(data), {'TOP': st.RoleState(thickness=0.018)})


if __name__ == '__main__':
    unittest.main()
