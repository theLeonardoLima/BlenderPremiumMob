"""Montagem do SketchUp no Blender (feature 009, T045; RN-14, D-16).

Recebe o `SkpModel` e a `Scene` do OpenSKP (`aggregates/skp.py`), passa pelo núcleo puro (`skp_core.plan`) e cria:
- uma malha por primitiva, com UV e o material do SketchUp (nome, cor base e, quando houver, a textura);
- um grupo de peças (007, `group.create_group`) por instância do SketchUp, com o nome dela.

As imagens das texturas são gravadas numa pasta temporária e empacotadas no `.blend` (`Image.pack`), para o arquivo e
os itens da biblioteca não dependerem da pasta.

Feature 010 (T010; RN-07 a RN-09, D-03): a montagem segue a árvore do `skp_core.tree`. Os grupos filhos são criados
primeiro e parentados ao grupo do pai mantendo a posição; um contêiner sem malha vira um Empty com `btm_group`. Um
material já importado com o mesmo nome, a mesma cor e a mesma imagem é reaproveitado (sem `.001`). A montagem
devolve também quantas figuras de escala foram puladas.
"""

import os
import tempfile

import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from . import group, skp_core

SKP_TAG = 'btm_skp_material'
KEY_PROP = 'btm_skp_key'


def _image(scene, index, folder, cache):
    if index in cache:
        return cache[index]
    texture = scene.textures[index]
    path = os.path.join(folder, skp_core.texture_filename(texture, index))
    with open(path, "wb") as handle:
        handle.write(texture.data)
    image = bpy.data.images.load(path, check_existing=False)
    image.pack()
    cache[index] = image
    return image


def _material(name, scene, plan_mesh, folder, images, cache):
    key = (name, plan_mesh.material_index)
    if key in cache:
        return cache[key]
    color = (scene.gltf_materials[plan_mesh.material_index].get("pbrMetallicRoughness") or {}).get(
        "baseColorFactor") if plan_mesh.material_index >= 0 else None
    color = list(color or [0.8, 0.8, 0.8, 1.0])
    image_name = (scene.textures[plan_mesh.texture].filename
                  if plan_mesh.texture is not None and plan_mesh.texture < len(scene.textures) else "")
    signature = "{}|{}|{}".format(name, ",".join(str(round(c, 3)) for c in color), image_name)
    reuse = next((m for m in bpy.data.materials if m.get(SKP_TAG) and m.get(KEY_PROP) == signature), None)
    if reuse is not None:                    # reimportar não duplica o material (RN-09)
        cache[key] = reuse
        return reuse
    mat = bpy.data.materials.new(name)
    mat[SKP_TAG] = True
    mat[KEY_PROP] = signature
    mat.diffuse_color = color
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = color
        if plan_mesh.texture is not None and plan_mesh.texture < len(scene.textures):
            node = tree.nodes.new('ShaderNodeTexImage')
            node.image = _image(scene, plan_mesh.texture, folder, images)
            node.location = (bsdf.location.x - 320, bsdf.location.y)
            tree.links.new(node.outputs['Color'], bsdf.inputs['Base Color'])
    cache[key] = mat
    return mat


def _mesh_object(collection, plan_mesh, mat):
    mesh = bpy.data.meshes.new(plan_mesh.name)
    mesh.from_pydata(plan_mesh.verts, [], plan_mesh.tris)
    if plan_mesh.uvs and len(plan_mesh.uvs) == len(plan_mesh.verts):
        layer = mesh.uv_layers.new(name="UVMap")
        for loop in mesh.loops:
            layer.data[loop.index].uv = plan_mesh.uvs[loop.vertex_index]
    mesh.materials.append(mat)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(plan_mesh.name, mesh)
    collection.objects.link(obj)
    return obj


def _empty_group(collection, name, children):
    """Grupo de peças sem malha própria (contêiner): Empty com `btm_group`, no centro dos filhos."""
    lo, hi = group.world_box([o for c in children for o in [c] + list(c.children_recursive) if o.type == 'MESH'])
    root = bpy.data.objects.new(name, None)
    root.empty_display_type, root.empty_display_size = 'CUBE', 0.05
    collection.objects.link(root)
    root.location = ((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, lo.z)
    root.btm_group.is_group, root.btm_group.kind = True, 'PLAIN'
    return root


def _build_node(context, collection, scene, plan, folder, images, materials):
    children = [_build_node(context, collection, scene, child, folder, images, materials) for child in plan.children]
    children = [c for c in children if c is not None]
    objs = [_mesh_object(collection, m, _material(m.material, scene, m, folder, images, materials))
            for m in plan.meshes]
    context.view_layer.update()
    root = group.create_group(objs, 'PLAIN', plan.name) if objs else _empty_group(collection, plan.name, children)
    context.view_layer.update()
    for child in children:                    # filho dentro do pai, no mesmo lugar (RN-07)
        world = child.matrix_world.copy()
        child.parent = root
        child.matrix_parent_inverse = Matrix.Identity(4)
        child.matrix_world = world
    return root


def build(context, model, scene):
    """Cria as malhas e os grupos da árvore; devolve (grupos de topo, figuras de escala puladas)."""
    plans, skipped = skp_core.tree(scene, model)
    collection = context.collection or context.scene.collection
    folder = tempfile.mkdtemp(prefix="caffmob_skp_")
    images, materials = {}, {}
    groups = [_build_node(context, collection, scene, plan, folder, images, materials) for plan in plans]
    return [g for g in groups if g is not None], skipped
