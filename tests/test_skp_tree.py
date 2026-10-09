"""Testes da árvore do SketchUp (feature 010, T005; RN-07 a RN-09): `caffmob_draw/aggregates/skp_core.py`.

Objetos no formato do OpenSKP 1.3.0, montados à mão. As posições das primitivas estão em metros, no referencial do
glTF (Y para cima); `position_mm` dos nós, em mm no referencial do SketchUp (Z para cima).
"""

import unittest
from types import SimpleNamespace as NS

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import skp_core as sk


def quad(x0, y0, z0, x1, y1):
    """Quadrado no plano z do glTF, de (x0, y0) a (x1, y1)."""
    return [x0, y0, z0, x1, y0, z0, x1, y1, z0, x0, y1, z0]


def node(name, definition, path, pos=(0, 0, 0), children=()):
    return NS(name=name, definition_name=definition, path=path, position_mm=pos, children=list(children))


def prim(geom, positions, mat=0):
    return NS(positions=positions, normals=None, uvs=None, indices=[0, 1, 2, 0, 2, 3], material_index=mat,
              geom_name=geom)


def scene():
    hinges = [node("Dobradica", "Dobradica", "ROOT / Folha 1 / Dobradica", (0, 0, z)) for z in (200, 1000, 1800)]
    leaf = node("Folha 1", "Folha", "ROOT / Folha 1", children=hinges)
    person = node("Pessoa", "2D_Woman_Standing_Teste", "ROOT / Pessoa", (1000, 0, 0),
                  children=[node("Cabeca", "Cabeca", "ROOT / Pessoa / Cabeca")])
    box = node("Caixa", "Caixa", "ROOT / Caixa", children=[node("Gaveta", "Gaveta", "ROOT / Caixa / Gaveta")])
    root = node("ROOT", "ROOT_MODEL", "ROOT", children=[leaf, person, box])
    meta = {}
    prims = []

    def add(geom, path, name, positions):
        meta[geom] = NS(name=name, path=path, definition_name=name)
        prims.append(prim(geom, positions))
    add("g_leaf", "ROOT / Folha 1", "Folha 1", quad(0, 0, 0, 0.7, 2.0))
    for i, z in enumerate((0.2, 1.0, 1.8)):       # glTF y = altura (m) ≈ position_mm z / 1000
        add(f"g_h{i}", "ROOT / Folha 1 / Dobradica", "Dobradica", quad(0, z, 0.01, 0.01, z + 0.09))
    add("g_person", "ROOT / Pessoa", "Pessoa", quad(1, 0, 0, 1.2, 1.7))
    add("g_head", "ROOT / Pessoa / Cabeca", "Cabeca", quad(1, 1.6, 0.01, 1.1, 1.7))
    add("g_drawer", "ROOT / Caixa / Gaveta", "Gaveta", quad(2, 0, 0, 2.4, 0.2))
    return NS(scene_hierarchy=root, glb_primitives=prims, mesh_index=meta,
              gltf_materials=[{"pbrMetallicRoughness": {"baseColorFactor": [200 / 255, 200 / 255, 200 / 255, 1.0]}}], textures=[])


MODEL = NS(materials=[NS(name="Layer_Layer0", color=(200, 200, 200, 255), texture=None)])


class SkpTreeTest(unittest.TestCase):
    def test_arvore_com_ferragens_dentro_da_folha(self):
        roots, skipped = sk.tree(scene(), MODEL)
        names = [g.name for g in roots]
        self.assertIn("Folha 1", names)
        leaf = next(g for g in roots if g.name == "Folha 1")
        self.assertEqual(len(leaf.meshes), 1)
        self.assertEqual([c.name for c in leaf.children], ["Dobradica", "Dobradica", "Dobradica"])
        heights = sorted(round(c.meshes[0].verts[0][2], 2) for c in leaf.children)
        self.assertEqual(heights, [0.2, 1.0, 1.8])           # cada dobradiça com a sua malha

    def test_figura_de_escala_sai_com_os_filhos(self):
        roots, skipped = sk.tree(scene(), MODEL)
        self.assertEqual(skipped, 1)
        all_names = [g.name for g in sk.walk(roots)]
        self.assertNotIn("Pessoa", all_names)
        self.assertNotIn("Cabeca", all_names)

    def test_conteiner_com_um_filho_colapsa(self):
        roots, _skipped = sk.tree(scene(), MODEL)
        self.assertIn("Gaveta", [g.name for g in roots])
        self.assertNotIn("Caixa", [g.name for g in roots])

    def test_figuras_reconhecidas(self):
        for name in ("2D_Woman_Standing_Sandra", "2D Man", "Chris", "Susan Sitting", "Laura"):
            self.assertTrue(sk.is_scale_figure(name), name)
        for name in ("Porta", "Component_810", "Christmas tree"):
            self.assertFalse(sk.is_scale_figure(name), name)

    def test_material_de_camada(self):
        self.assertEqual(sk.material_names(scene(), MODEL), ["Layer0"])
        self.assertEqual(sk.clean_material_name("Layer_Layer0"), "Layer0")
        self.assertEqual(sk.clean_material_name("Madeira"), "Madeira")


if __name__ == '__main__':
    unittest.main()
