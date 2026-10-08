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


if __name__ == "__main__":
    unittest.main()
