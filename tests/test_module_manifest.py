"""Testes do manifesto do módulo salvo (T013): `caffmob_draw/customize/manifest.py`."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.customize import manifest as mf
from caffmob_draw.customize import spec as sp


def sample_spec():
    s = sp.Spec(library='FRAMELESS')
    s.ensure_opening("bay0/opening0").door_style = "Vidro"
    return s


class ManifestTest(unittest.TestCase):
    def test_montar_e_ler(self):
        data = mf.build("Aéreo vidro 2P", "Aéreos", 'FRAMELESS', "Aéreo", sample_spec(),
                        materials=["Laca", "", "Laca"], pulls=["Perfil", sp.NO_PULL])
        self.assertEqual(data["materials"], ["Laca"])
        self.assertEqual(data["pulls"], ["Perfil"])
        loaded, spec, errors = mf.loads(mf.dumps(data))
        self.assertEqual(errors, [])
        self.assertEqual(loaded["name"], "Aéreo vidro 2P")
        self.assertEqual(spec.opening("bay0/opening0").door_style, "Vidro")

    def test_versao_maior_recusada(self):
        data = mf.build("A", "B", 'BTM', "A", sp.Spec())
        data["schema_version"] = "2.0.0"
        _d, spec, errors = mf.loads(json.dumps(data))
        self.assertIsNone(spec)
        self.assertTrue(any("não suportada" in e for e in errors))

    def test_formato_e_biblioteca(self):
        errors = mf.validate({"format": "x", "schema_version": "1.0.0", "library": "OUTRA", "name": "", "root_object": ""})
        self.assertEqual(len(errors), 4)

    def test_json_invalido(self):
        self.assertTrue(mf.loads("{")[2][0].startswith("JSON inválido"))

    # Feature 006 (T008): estrutura e divisões, campos opcionais da 1.1.0 --------------------------------------
    def test_1_0_0_continua_valido(self):
        data = mf.build("A", "B", 'BTM', "A", sp.Spec())
        data["schema_version"] = "1.0.0"
        _d, spec, errors = mf.loads(json.dumps(data))
        self.assertEqual(errors, [])
        self.assertEqual(mf.structure_of(data), {})
        self.assertEqual(mf.divisions_of(data), [])

    def test_estrutura_e_divisoes_ida_e_volta(self):
        structure = {"RIGHT": {"removed": True, "mode": "KEEP", "thickness": 0.0, "material": ""},
                     "TOP": {"removed": False, "mode": "KEEP", "thickness": 0.018, "material": "MDP"}}
        divisions = [{"uid": "a1", "space": "s0.a", "orientation": "HORIZONTAL", "offset": 0.36, "use_front": True,
                      "front": 0.02, "use_back": False, "back": 0.02, "thickness": 0.0, "material": ""}]
        data = mf.build("A", "B", 'FRAMELESS', "A", sp.Spec(), structure=structure, divisions=divisions)
        self.assertEqual(data["schema_version"], "1.1.0")
        self.assertEqual(data["structure"]["TOP"]["thickness_mm"], 18.0)
        self.assertEqual(data["divisions"][0]["offset_mm"], 360.0)
        loaded, _spec, errors = mf.loads(mf.dumps(data))
        self.assertEqual(errors, [])
        self.assertAlmostEqual(mf.structure_of(loaded)["TOP"]["thickness"], 0.018)
        self.assertAlmostEqual(mf.divisions_of(loaded)[0]["offset"], 0.36)
        self.assertEqual(mf.divisions_of(loaded)[0]["space"], "s0.a")

    def test_erros_de_estrutura_e_divisao(self):
        data = mf.build("A", "B", 'BTM', "A", sp.Spec())
        data["structure"] = {"MEIO": {"mode": "KEEP"}, "TOP": {"mode": "VOAR", "thickness_mm": -1}}
        data["divisions"] = [{"space": "x9", "orientation": "DIAGONAL", "offset_mm": -5}]
        errors = mf.validate(data)
        self.assertEqual(len(errors), 6)

    def test_nome_de_arquivo(self):
        self.assertEqual(mf.file_stem('Aéreo 80/60: "vidro"?'), "Aéreo 80_60_ _vidro__")
        self.assertEqual(mf.file_stem(" ... "), "modulo")


if __name__ == "__main__":
    unittest.main()
