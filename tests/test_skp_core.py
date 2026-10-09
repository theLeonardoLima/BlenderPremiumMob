"""Testes do núcleo do SketchUp (feature 009, T043; RN-13, RN-14): `caffmob_draw/aggregates/skp_core.py`.

Usa objetos no formato do OpenSKP 1.3.0 (`Scene.glb_primitives`, `mesh_index`, `gltf_materials`, `textures`;
`SkpModel.materials`), montados à mão: o teste não depende do pacote instalado.
"""

import unittest
from types import SimpleNamespace as NS

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import skp_core as sk

QUAD = [0, 0, 0, 1, 0, 0, 1, 2, 0, 0, 2, 0]           # x, y(cima), z do glTF, em metros
TRIS = [0, 1, 2, 0, 2, 3]
UVS = [0, 0, 1, 0, 1, 1, 0, 1]


def prim(name, mat, positions=QUAD, indices=TRIS):
    return NS(positions=positions, normals=None, uvs=UVS, indices=indices, material_index=mat, geom_name=name)


def scene():
    meta = {"g0": NS(name="Batente 1", path="ROOT / Batente 1", definition_name="Batente"),
            "g1": NS(name="Batente 1", path="ROOT / Batente 1", definition_name="Batente"),
            "g2": NS(name="Folha 1", path="ROOT / Folha 1", definition_name="Folha")}
    mats = [{"pbrMetallicRoughness": {"baseColorFactor": [240 / 255, 240 / 255, 240 / 255, 1.0]}},
            {"pbrMetallicRoughness": {"baseColorFactor": [1.0, 84 / 255, 84 / 255, 1.0]}},
            {"pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "baseColorTexture": {"index": 0}}}]
    textures = [NS(data=b"\x89PNG", mime_type="image/png", filename="wood.png")]
    prims = [prim("g0", 0), prim("g1", 1, indices=[0, 2, 1, 0, 3, 2]), prim("g2", 2)]
    return NS(glb_primitives=prims, mesh_index=meta, gltf_materials=mats, textures=textures)


MODEL = NS(materials=[NS(name="Branco", color=(240, 240, 240, 255), texture=None),
                      NS(name="Madeira", color=(255, 255, 255, 254), texture=NS(filename="wood.png"))])


class SkpCoreTest(unittest.TestCase):
    def test_eixo_e_unidade(self):
        self.assertEqual(sk.to_blender((1.0, 2.0, 3.0)), (1.0, -3.0, 2.0))

    def test_nomes_dos_materiais(self):
        names = sk.material_names(scene(), MODEL)
        self.assertEqual(names, ["Branco", "SketchUp padrão", "Madeira"])

    def test_plano_por_instancia_sem_o_verso(self):
        groups = sk.plan(scene(), MODEL)
        self.assertEqual([(g.name, len(g.meshes)) for g in groups], [("Batente 1", 1), ("Folha 1", 1)])
        mesh = groups[1].meshes[0]
        self.assertEqual(mesh.material, "Madeira")
        self.assertEqual(mesh.texture, 0)
        self.assertEqual(mesh.verts[2], (1.0, 0.0, 2.0))          # Y-up → Z-up
        self.assertEqual(mesh.tris, [(0, 1, 2), (0, 2, 3)])
        self.assertEqual(mesh.uvs[2], (1.0, 0.0))                  # v do glTF invertido

    def test_nome_de_arquivo_da_textura(self):
        self.assertEqual(sk.texture_filename(NS(filename="../Madeira clara.jpg", mime_type="image/jpeg"), 3),
                         "skp_3_Madeira_clara.jpg")
        self.assertEqual(sk.texture_filename(NS(filename="", mime_type="image/png"), 0), "skp_0.png")

    def test_motivo(self):
        msg = sk.failure_message("versão não suportada")
        self.assertIn("versão não suportada", msg)
        self.assertIn("glTF", msg)


if __name__ == '__main__':
    unittest.main()
