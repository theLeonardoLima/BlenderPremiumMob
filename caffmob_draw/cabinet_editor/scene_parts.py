"""Peças das abas novas na cena (feature 008, T024 a T026; D-12).

Funções comuns para criar, posicionar e apagar os objetos de Estrutura (extras), Internos e Deslizantes, todos filhos
diretos da raiz do módulo e marcados com `btm_extra` (como as divisões da 006, ficam fora do que as bibliotecas
reconstroem):
- chapa = `CabinetPart` posicionado por uma caixa no referencial da raiz; a espessura vai no eixo mais fino da caixa;
- ferragem e eletro de referência = malha simples (cilindro ou caixa), fora do plano de corte de chapas.

Orientação da peça medida no Blender 5.2: sem rotação cresce em +X/+Y/+Z (comprimento/largura/espessura);
−90° em Y com `Mirror Z` põe a espessura em +X; +90° em X com `Mirror Z` põe a espessura em +Y.
"""

import json
import math

import bmesh  # type: ignore
import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from .. import compat
from ..customize.adapters import common
from . import scene_divisions

COMPONENT_PROP = scene_divisions.COMPONENT_PROP
HARDWARE_PROP = 'btm_hardware'


def extras_of(root, kinds=None):
    """Objetos `btm_extra` filhos diretos da raiz (de alguns tipos, se `kinds`)."""
    return [o for o in root.children if getattr(o, 'btm_extra', None) is not None and o.btm_extra.is_extra
            and (kinds is None or o.btm_extra.kind in kinds)]


def delete(objs):
    for obj in list(objs):
        for child in list(obj.children_recursive):
            bpy.data.objects.remove(child, do_unlink=True)
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)


def _link(root, obj):
    for collection in root.users_collection or (bpy.context.scene.collection,):
        if obj.name not in collection.objects:
            collection.objects.link(obj)
    for collection in list(obj.users_collection):
        if collection not in root.users_collection:
            collection.objects.unlink(obj)
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)


def _tag(obj, kind, catalog_id="", space="", slot=0, params=None):
    data = obj.btm_extra
    data.is_extra, data.kind, data.catalog_id, data.space, data.slot = True, kind, catalog_id, space, slot
    data.params = json.dumps(params or {}, sort_keys=True)


def place(obj, box):
    """Leva a chapa à caixa `box` ((lo), (hi)) no referencial da raiz."""
    mod = common.gn_modifier(obj, 'GeoNodeCutpart')
    size = [box[1][i] - box[0][i] for i in range(3)]
    thin = min(range(3), key=lambda i: size[i])
    obj.location = box[0]
    if thin == 2:
        obj.rotation_euler = (0.0, 0.0, 0.0)
        values = {'Length': size[0], 'Width': size[1], 'Thickness': size[2], 'Mirror Y': False, 'Mirror Z': False}
    elif thin == 0:
        obj.rotation_euler = (0.0, math.radians(-90.0), 0.0)
        values = {'Length': size[2], 'Width': size[1], 'Thickness': size[0], 'Mirror Y': False, 'Mirror Z': True}
    else:
        obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        values = {'Length': size[0], 'Width': size[2], 'Thickness': size[1], 'Mirror Y': False, 'Mirror Z': True}
    if mod is not None:
        for name, value in values.items():
            compat.try_set_gn_input(mod, name, value)
    obj.update_tag()
    return thin


def make_part(root, name, box, kind, component, material="", **tag):
    """Chapa de produção (`CabinetPart`) com `btm_extra`, `btm_component` e material de chapa opcional."""
    from ..product_libraries.frameless.types_frameless import CabinetPart
    part = CabinetPart()
    part.create(name)
    obj = part.obj
    _link(root, obj)
    obj[COMPONENT_PROP] = component
    if material:
        obj[common.RAW_MATERIAL_PROP] = material
    _tag(obj, kind, **tag)
    scene_divisions._borrow_material(root, obj)
    place(obj, box)
    return obj


def _mesh_object(root, name, build):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    _link(root, obj)
    return obj


def make_box(root, name, box, kind, hardware="", **tag):
    """Caixa simples (eletro de referência, trilho): fora do plano de corte de chapas."""
    (x0, y0, z0), (x1, y1, z1) = box

    def build(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=bm.verts)
        bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts)
    obj = _mesh_object(root, name, build)
    if hardware:
        obj[HARDWARE_PROP] = hardware
    _tag(obj, kind, **tag)
    return obj


def make_cylinder(root, name, box, kind, hardware="", **tag):
    """Cilindro vertical inscrito na caixa (pé plástico)."""
    (x0, y0, z0), (x1, y1, z1) = box
    radius = min(x1 - x0, y1 - y0) / 2.0

    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=radius, radius2=radius, depth=z1 - z0)
        bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts)
    obj = _mesh_object(root, name, build)
    if hardware:
        obj[HARDWARE_PROP] = hardware
    _tag(obj, kind, **tag)
    return obj


def carcass_box(context, root):
    """Caixa da carcaça (só as chapas da estrutura, sem extras), no referencial da raiz."""
    from ..customize import adapters
    adapter = adapters.for_root(root)
    if adapter is not None and adapter.LIBRARY == 'BTM':
        info = common.call(adapter, 'elevation_parts', context, root)
        boxes = [(lo, hi) for _n, _r, lo, hi in info]
    else:
        depsgraph = context.evaluated_depsgraph_get()
        parts = common.call(adapter, 'structure_parts', root) if adapter is not None else {}
        boxes = [b for objs in parts.values() for b in (common.local_box(root, o, depsgraph) for o in objs) if b]
    if not boxes:
        corners = [tuple(c) for c in root.bound_box]
        return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))
    return (tuple(min(b[0][i] for b in boxes) for i in range(3)), tuple(max(b[1][i] for b in boxes) for i in range(3)))
