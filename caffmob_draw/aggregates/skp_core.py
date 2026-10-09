"""Núcleo do SketchUp (feature 009, T044; RN-13, RN-14, D-16). Python puro, sem `bpy` nem `openskp`.

Transforma a cena que o OpenSKP monta (`Scene.glb_primitives`, `mesh_index`, `gltf_materials`, `textures`;
`SkpModel.materials`) num plano de montagem para o Blender:
- uma entrada por instância do SketchUp (o grupo de peças leva o nome dela), com as malhas já no lugar;
- as posições chegam em metros no referencial do glTF (Y para cima) e viram Z para cima: (x, y, z) → (x, −z, y);
- o v da UV do glTF é invertido para o Blender;
- quando a frente e o verso de uma face têm cores diferentes, o OpenSKP emite o verso como outra primitiva com os
  mesmos vértices; num móvel isso só duplica a geometria, então fica a primeira primitiva de cada conjunto;
- os materiais recebem o nome do SketchUp: o texturizado pela imagem, o liso pela cor; o resto vira "SketchUp padrão".

Feature 010 (T009; RN-07 a RN-09, D-01, D-02): o plano é uma **árvore** pelo `scene_hierarchy`. Cada instância é um
nó com as próprias malhas e os filhos, e instâncias repetidas (mesmo caminho) recebem as primitivas mais perto da
sua origem. Figuras de escala do SketchUp saem com os descendentes e são contadas. Um contêiner sem malha e com um
filho só colapsa no filho. O material de camada `Layer_<x>` vira `<x>`.
"""

import re
from dataclasses import dataclass, field

from ..data.i18n import N_, tr

DEFAULT_MATERIAL = N_("SketchUp padrão")
_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/bmp": ".bmp", "image/tiff": ".tif"}


@dataclass
class MeshPlan:
    name: str
    verts: list
    tris: list
    uvs: list = None
    material: str = ""
    material_index: int = -1
    texture: int = None             # índice em `Scene.textures`, ou None


@dataclass
class GroupPlan:
    name: str
    path: str
    meshes: list = field(default_factory=list)
    children: list = field(default_factory=list)


# Figuras de escala que o SketchUp põe nos modelos (pessoas em 2D): pelo nome da instância ou da definição.
_FIGURE = re.compile(r"^2D[_ ]?(Woman|Man|Person|Figure|People)(_|\b)|^(Sandra|Chris|Susan|Lily|Derrick|Laura|Nancy|Bryce|"
                     r"Steve|Mark|Ivan|Emily|Kelly|Joe)(\b|_)", re.IGNORECASE)


def is_scale_figure(name):
    return bool(_FIGURE.match(str(name or "").strip()))


def clean_material_name(name):
    return name[len("Layer_"):] if name.startswith("Layer_") and len(name) > len("Layer_") else name


def to_blender(point):
    x, y, z = point
    return (float(x), -float(z), float(y))


def _triples(flat, size):
    flat = list(flat) if flat is not None else []
    return [tuple(float(v) for v in flat[i:i + size]) for i in range(0, len(flat) - size + 1, size)]


def _rgb(material):
    color = (material.get("pbrMetallicRoughness") or {}).get("baseColorFactor") or [1, 1, 1, 1]
    return tuple(round(float(c) * 255) for c in color[:3])


def _texture_index(material):
    tex = (material.get("pbrMetallicRoughness") or {}).get("baseColorTexture")
    return tex.get("index") if isinstance(tex, dict) else None


def material_names(scene, model):
    """Nome do SketchUp para cada material do glTF (`scene.gltf_materials`)."""
    named = list(getattr(model, "materials", None) or [])
    by_texture = {getattr(m.texture, "filename", None): m.name for m in named if getattr(m, "texture", None)}
    by_color = {}
    for m in named:
        if not getattr(m, "texture", None):
            by_color.setdefault(tuple(int(c) for c in m.color[:3]), m.name)
    names = []
    for material in scene.gltf_materials:
        tex = _texture_index(material)
        if tex is not None and tex < len(scene.textures):
            name = by_texture.get(scene.textures[tex].filename)
        else:
            name = by_color.get(_rgb(material))
        names.append(clean_material_name(name) if name else tr(DEFAULT_MATERIAL))
    return names


def _nodes(scene):
    """[(id, nó, id do pai)] da hierarquia, sem as figuras de escala; e quantas figuras saíram."""
    root = getattr(scene, "scene_hierarchy", None)
    if root is None:                    # cena sem hierarquia: um nó por caminho, todos no topo
        paths = sorted({getattr(scene.mesh_index.get(p.geom_name), "path", "") or "ROOT" for p in scene.glb_primitives})
        fake = [type("N", (), {"name": p.rsplit(" / ", 1)[-1], "definition_name": "", "path": p,
                               "position_mm": (0.0, 0.0, 0.0), "children": []})() for p in paths]
        return [(i + 1, n, 0) for i, n in enumerate(fake)], 0, []
    out, skipped, banned = [], 0, []
    stack = [(child, 0) for child in reversed(root.children)]
    counter = 0
    while stack:
        node, parent = stack.pop()
        if is_scale_figure(node.name) or is_scale_figure(getattr(node, "definition_name", "")):
            skipped += 1
            banned.append(node.path)
            continue
        counter += 1
        out.append((counter, node, parent))
        stack.extend((child, counter) for child in reversed(node.children))
    return out, skipped, banned


def _distance_to_box(point, lo, hi):
    return sum(max(lo[i] - point[i], 0.0, point[i] - hi[i]) ** 2 for i in range(3)) ** 0.5


def tree(scene, model):
    """(grupos de topo com os filhos, figuras de escala puladas). Malhas já no referencial do Blender."""
    names = material_names(scene, model)
    nodes, skipped, banned = _nodes(scene)
    by_path = {}
    for node_id, node, _parent in nodes:
        by_path.setdefault(node.path, []).append((node_id, node))
    plans = {node_id: GroupPlan(node.name, node.path) for node_id, node, _parent in nodes}
    root_plan = GroupPlan("SketchUp", "ROOT")
    seen = {}
    for prim in scene.glb_primitives:
        meta = scene.mesh_index.get(prim.geom_name)
        path = getattr(meta, "path", "") or "ROOT"
        if any(path == b or path.startswith(b + " / ") for b in banned):
            continue                                  # geometria de figura de escala
        verts = [to_blender(p) for p in _triples(prim.positions, 3)]
        candidates = by_path.get(path, [])
        if len(candidates) > 1 and verts:             # instâncias repetidas: a mais perto da sua origem
            lo = tuple(min(v[i] for v in verts) * 1000.0 for i in range(3))
            hi = tuple(max(v[i] for v in verts) * 1000.0 for i in range(3))
            node_id = min(candidates, key=lambda c: _distance_to_box(c[1].position_mm, lo, hi))[0]
        else:
            node_id = candidates[0][0] if candidates else None
        target = plans.get(node_id, root_plan)
        key = frozenset((round(v[0], 6), round(v[1], 6), round(v[2], 6)) for v in verts)
        if key in seen.setdefault(id(target), set()):
            continue                                  # verso emitido à parte: mesma geometria
        seen[id(target)].add(key)
        tris = [tuple(int(i) for i in t) for t in _triples(prim.indices, 3)]
        uvs = [(u, 1.0 - v) for u, v in _triples(prim.uvs, 2)] if prim.uvs is not None and len(prim.uvs) else None
        mat_index = prim.material_index if prim.material_index is not None else -1
        material = names[mat_index] if 0 <= mat_index < len(names) else tr(DEFAULT_MATERIAL)
        texture = _texture_index(scene.gltf_materials[mat_index]) if 0 <= mat_index < len(names) else None
        target.meshes.append(MeshPlan(f"{target.name} {len(target.meshes) + 1}", verts, tris, uvs, material,
                                      mat_index, texture))
    tops = []
    for node_id, _node, parent in nodes:
        (plans[parent].children if parent else tops).append(plans[node_id])
    tops = _prune(tops)
    if root_plan.meshes:
        tops.insert(0, root_plan)
    return tops, skipped


def _prune(groups):
    out = []
    for group in groups:
        group.children = _prune(group.children)
        if not group.meshes and not group.children:
            continue
        if not group.meshes and len(group.children) == 1:
            out.append(group.children[0])          # contêiner com um filho só colapsa (R-06)
            continue
        out.append(group)
    return out


def walk(groups):
    for group in groups:
        yield group
        yield from walk(group.children)


def plan(scene, model):
    """Lista plana dos grupos com malha (009), na ordem da árvore."""
    return [g for g in walk(tree(scene, model)[0]) if g.meshes]


def texture_filename(texture, index):
    """Nome seguro para gravar a imagem: só o nome do arquivo, sem pastas nem caracteres estranhos."""
    base = re.split(r"[\\/]", texture.filename or "")[-1]
    stem, dot, ext = base.rpartition(".")
    if not dot:
        stem, ext = base, ""
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")
    ext = "." + ext.lower() if ext else _EXT.get(texture.mime_type, ".png")
    return f"skp_{index}_{stem}{ext}" if stem else f"skp_{index}{ext}"


def failure_message(reason):
    return tr("Não foi possível ler o SketchUp: {}. Salve numa versão recente do SketchUp ou exporte em "
              "glTF, OBJ ou FBX.").format(reason)
