"""Retexturizar uma parte ou um item inteiro (feature 009, T020; RN-12, D-12).

- **Acabamento do plugin:** os materiais das bibliotecas de chapas (frameless, face frame, closets) e os que já estão no
  arquivo. Um material que ainda não está no arquivo é anexado do `.blend` de origem. Peças `GeoNodeCutpart` recebem o
  material nas duas faces (`common.set_cutpart_material`); as outras malhas, em todos os slots.
- **Imagem própria:** material "Textura: <arquivo> <tamanho> mm", com Image Texture em projeção de caixa (Box) sobre
  coordenadas de objeto e escala real (`1 / tamanho em metros`), o que serve para malha importada sem UV boa. Um
  material com o mesmo arquivo e o mesmo tamanho é reaproveitado.

A troca vale para a cópia na cena: salvar de novo na biblioteca é opcional.
"""

import os

import bpy  # type: ignore

from ..customize.adapters import common

PACKAGE = os.path.dirname(os.path.dirname(__file__))
LIBRARIES = ("product_libraries/frameless/frameless_assets/materials/cabinet_material.blend",
             "product_libraries/face_frame/face_frame_assets/materials/cabinet_material.blend",
             "product_libraries/closets/assets/materials/library.blend")
PATH_PROP = 'btm_texture_path'
SIZE_PROP = 'btm_texture_size_mm'
_names_cache = {}


def library_materials():
    """{nome: caminho do .blend} dos acabamentos do plugin (lido uma vez por sessão)."""
    if not _names_cache:
        for rel in LIBRARIES:
            path = os.path.join(PACKAGE, rel)
            if not os.path.isfile(path):
                continue
            with bpy.data.libraries.load(path, link=False) as (data_from, _data_to):
                for name in data_from.materials:
                    _names_cache.setdefault(name, path)
    return _names_cache


def finish_names():
    """Acabamentos para escolher: os do plugin e os do arquivo (sem os de miniatura e os internos)."""
    names = set(library_materials()) | {m.name for m in bpy.data.materials if not m.name.startswith(".")}
    return sorted(names, key=str.lower)


def _finish(name):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    path = library_materials().get(name)
    if path is None:
        return None
    with bpy.data.libraries.load(path, link=False) as (_data_from, data_to):
        data_to.materials = [name]
    return data_to.materials[0] if data_to.materials else None


def targets(objs):
    return [o for o in objs if o.type == 'MESH']


def apply_finish(objs, name):
    """Aplica o acabamento `name`; devolve quantas malhas mudaram (0 se o material não existe)."""
    mat = _finish(name)
    if mat is None:
        return 0
    return sum(1 for obj in targets(objs) if common.set_cutpart_material(obj, mat))


def image_material(path, size_mm):
    """Material de textura com escala real; reaproveita um igual (mesmo arquivo e tamanho)."""
    path = os.path.abspath(path)
    for mat in bpy.data.materials:
        if mat.get(PATH_PROP) == path and abs(float(mat.get(SIZE_PROP, 0.0)) - size_mm) < 1e-6:
            return mat
    image = bpy.data.images.load(path, check_existing=True)
    mat = bpy.data.materials.new("Textura: {} {:g} mm".format(os.path.basename(path), size_mm))
    mat[PATH_PROP], mat[SIZE_PROP] = path, float(size_mm)
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')
    coords = tree.nodes.new('ShaderNodeTexCoord')
    mapping = tree.nodes.new('ShaderNodeMapping')
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.projection = 'BOX'
    tex.projection_blend = 0.2
    scale = 1.0 / max(size_mm / 1000.0, 1e-4)
    mapping.inputs['Scale'].default_value = (scale, scale, scale)
    coords.location, mapping.location, tex.location = (-900, 0), (-700, 0), (-450, 0)
    tree.links.new(coords.outputs['Object'], mapping.inputs['Vector'])
    tree.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def apply_image(objs, path, size_mm):
    mat = image_material(path, size_mm)
    return sum(1 for obj in targets(objs) if common.set_cutpart_material(obj, mat))
