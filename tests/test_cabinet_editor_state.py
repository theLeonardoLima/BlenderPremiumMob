"""Testes do estado do editor de armário (feature 004, T022): `caffmob_draw/cabinet_editor/state.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import state as st


def make(width, front=""):
    return st.EditorState((width, 0.72, 0.55), {"library": "frameless", "openings": [{"path": "o0", "front": front}]})


class StateTest(unittest.TestCase):
    def test_tres_edicoes_dois_desfazer_e_refazer(self):
        draft = st.Draft(make(0.8))
        self.assertFalse(draft.dirty())
        for state in (make(0.7), make(0.7, "DRAWERS"), make(0.6, "DRAWERS")):
            self.assertTrue(draft.checkpoint(state))
        self.assertTrue(draft.dirty())
        draft.undo()
        back = draft.undo()
        self.assertEqual(back.dimensions[0], 0.7)
        self.assertEqual(back.spec["openings"][0]["front"], "")
        again = draft.redo()
        self.assertEqual(again.spec["openings"][0]["front"], "DRAWERS")
        self.assertEqual(draft.current.spec["openings"][0]["front"], "DRAWERS")

    def test_sem_mudanca_nao_grava_e_inicial_fica_intacto(self):
        draft = st.Draft(make(0.8))
        self.assertFalse(draft.checkpoint(make(0.8 + 1e-8)))
        state = make(0.6)
        draft.checkpoint(state)
        state.spec["openings"][0]["front"] = "OPEN"     # mexer no objeto depois não altera o histórico
        self.assertEqual(draft.current.spec["openings"][0]["front"], "")
        self.assertEqual(draft.initial.dimensions[0], 0.8)
        draft.undo()
        self.assertFalse(draft.dirty())

    def test_estrutura_e_divisoes_entram_na_assinatura(self):
        base = make(0.8)
        with_structure = make(0.8)
        with_structure.structure = {"RIGHT": {"removed": True, "mode": "KEEP", "thickness": 0.0, "material": ""}}
        with_division = make(0.8)
        with_division.divisions = [{"uid": "a1", "space": "s0", "orientation": "VERTICAL", "offset": 0.4}]
        sigs = {st.signature(s) for s in (base, with_structure, with_division)}
        self.assertEqual(len(sigs), 3)
        nudged = make(0.8)
        nudged.divisions = [{"uid": "a1", "space": "s0", "orientation": "VERTICAL", "offset": 0.4 + 1e-8}]
        self.assertEqual(st.signature(nudged), st.signature(with_division))


if __name__ == "__main__":
    unittest.main()
