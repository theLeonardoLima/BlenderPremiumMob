"""Gravar e inserir módulos da biblioteca do usuário (feature 003, T027-T028; D-10).

Mecânica comum às quatro bibliotecas, no mesmo formato dos grupos de gabinete do frameless
(`product_libraries/frameless/operators/ops_library.py`, que continua como está): `bpy.data.libraries.write` com
`path_remap='RELATIVE_ALL'` e `fake_user=True`, miniatura 256 px, e um manifesto JSON ao lado
(`interfaces/user-module-file.md`) com estilos, materiais e puxadores **por nome**.
"""

import datetime
import os
import tempfile

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..data.i18n import tr
from ..selection import classify
from . import adapters, manifest, reapply
from .adapters import common

MODULES_DIR = "modules"
GENERAL = "Geral"


def _package():
    return __package__.rsplit('.customize', 1)[0]


def modules_root():
    return bpy.utils.extension_path_user(_package(), path=MODULES_DIR, create=True)


def paths_for(name, category):
    folder = os.path.join(modules_root(), manifest.file_stem(category or GENERAL))
    stem = manifest.file_stem(name)
    return {ext: os.path.join(folder, stem + "." + ext) for ext in ("blend", "png", "json")}


def exists(name, category):
    return os.path.exists(paths_for(name, category)["blend"])


def list_modules():
    """[{name, category, blend, png, json, has_manifest}] de todas as categorias."""
    root = modules_root()
    found = []
    for category in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        folder = os.path.join(root, category)
        if not os.path.isdir(folder):
            continue
        for filename in sorted(os.listdir(folder)):
            if not filename.endswith(".blend"):
                continue
            stem = filename[:-6]
            base = os.path.join(folder, stem)
            entry = {"name": stem, "category": category, "blend": base + ".blend", "png": base + ".png",
                     "json": base + ".json", "has_manifest": os.path.exists(base + ".json")}
            if entry["has_manifest"]:
                with open(entry["json"], encoding="utf-8") as handle:
                    data, _spec, errors = manifest.loads(handle.read())
                if not errors:
                    entry["name"] = data["name"]
            found.append(entry)
    return found


# Gravação -------------------------------------------------------------------------------------------------------

def _tree(root):
    return [root] + list(root.children_recursive)


def _data_blocks(objects):
    blocks = set()
    for obj in objects:
        blocks.add(obj)
        if obj.data is not None:
            blocks.add(obj.data)
            for mat in getattr(obj.data, 'materials', []) or []:
                if mat is None:
                    continue
                blocks.add(mat)
                if mat.node_tree:
                    blocks.update(n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image)
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                blocks.add(mod.node_group)
    return blocks


def world_box(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = []
    for obj in objects:
        if obj.type != 'MESH' or obj.hide_get():
            continue
        evaluated = obj.evaluated_get(depsgraph)
        corners += [obj.matrix_world @ Vector(c) for c in evaluated.bound_box]
    if not corners:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    return (Vector([min(c[i] for c in corners) for i in range(3)]),
            Vector([max(c[i] for c in corners) for i in range(3)]))


def _thumbnail(context, objects, filepath):
    scene = context.scene
    saved = (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage,
             scene.render.engine, scene.render.filepath, scene.render.film_transparent)
    cam_data = bpy.data.cameras.new("Miniatura")
    cam_obj = bpy.data.objects.new("Miniatura", cam_data)
    scene.collection.objects.link(cam_obj)
    try:
        lo, hi = world_box(objects)
        center, size = (lo + hi) / 2.0, max((hi - lo).length, 0.1)
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = size * 1.1
        cam_obj.location = center + Vector((size, -size, size * 0.8))
        cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()
        scene.camera = cam_obj
        scene.render.resolution_x = scene.render.resolution_y = 256
        scene.render.resolution_percentage = 100
        scene.render.engine = 'BLENDER_WORKBENCH'
        scene.render.film_transparent = True
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return True
    except (RuntimeError, OSError) as exc:
        print(f"CAFFMob Draw: miniatura não gerada ({exc})")
        return False
    finally:
        (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage,
         scene.render.engine, scene.render.filepath, scene.render.film_transparent) = saved
        bpy.data.objects.remove(cam_obj)
        bpy.data.cameras.remove(cam_data)


def _addon_version():
    try:
        import addon_utils  # type: ignore
        for mod in addon_utils.modules():
            if mod.__name__ == _package():
                return ".".join(str(v) for v in mod.bl_info.get("version", ()))
    except (ImportError, AttributeError):
        pass
    return ""


def build_manifest(root, name, category):
    adapter = adapters.for_root(root)
    current = adapter.read(root)
    lo, hi = world_box(_tree(root))
    size = hi - lo
    door_styles = sorted({o.door_style for o in current.openings if o.door_style} |
                         {o.drawer_style for o in current.openings if o.drawer_style})
    materials = ([o.front_material for o in current.openings] + list(current.group_materials.values())
                 + list(current.part_materials.values()))
    pulls = [o.pull_model for o in current.openings] + [current.pull_all_fronts]
    current.aggregates = [{"name": obj.name, "parent_path": obj.parent.name if obj.parent else "",
                           "kind": obj.btm_aggregate.kind}
                          for obj in root.children_recursive if obj.btm_aggregate.is_aggregate]
    return manifest.build(
        name, category or GENERAL, classify.module_library(root), root.name, current,
        created=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), addon_version=_addon_version(),
        dimensions_mm={"width": round(size.x * 1000), "height": round(size.z * 1000), "depth": round(size.y * 1000)},
        styles={"door_styles": door_styles}, materials=materials, pulls=pulls,
        structure=root.btm_structure.to_dict() if getattr(root, 'btm_structure', None) is not None else None,
        divisions=_divisions(root))


def _divisions(root):
    """Divisões do módulo para o manifesto 1.1.0 (feature 006, T034); a geometria viaja no `.blend`."""
    from ..cabinet_editor import scene_divisions
    return scene_divisions.read(root)


def _renew_divisions(context, root):
    """Módulo inserido: uids novos nas divisões (cada inserção é independente) e chapas no vão atual."""
    from ..cabinet_editor import divisions, scene_divisions
    for obj in scene_divisions.objects(root):
        obj.btm_division.uid = divisions.new_uid()
    scene_divisions.reflow(context, root, force=True)


def save(context, root, name, category, thumbnail=True):
    """Grava `.blend` + `.json` (+ `.png`). Devolve (caminhos, mensagens de erro). Erro → nada parcial fica."""
    if adapters.for_root(root) is None:
        return None, [tr("O objeto selecionado não é um módulo")]
    paths = paths_for(name, category)
    folder = os.path.dirname(paths["blend"])
    written = []
    try:
        os.makedirs(folder, exist_ok=True)
        data = build_manifest(root, name, category)
        fd, tmp_blend = tempfile.mkstemp(suffix=".blend", dir=folder)
        os.close(fd)
        written.append(tmp_blend)
        bpy.data.libraries.write(tmp_blend, _data_blocks(_tree(root)), path_remap='RELATIVE_ALL', fake_user=True)
        fd, tmp_json = tempfile.mkstemp(suffix=".json", dir=folder)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(manifest.dumps(data))
        written.append(tmp_json)
        os.replace(tmp_blend, paths["blend"])
        os.replace(tmp_json, paths["json"])
        written = []
    except (OSError, RuntimeError) as exc:
        for path in written:
            if os.path.exists(path):
                os.remove(path)
        return None, [tr("Não foi possível gravar o módulo em {}: {}").format(folder, exc)]
    if thumbnail:
        _thumbnail(context, _tree(root), paths["png"])
    return paths, []


# Inserção -------------------------------------------------------------------------------------------------------

def _geo_node_refs(objects):
    from .. import compat
    refs = set()
    for obj in objects:
        for mod in obj.modifiers:
            if mod.type != 'NODES' or not mod.node_group:
                continue
            for item in mod.node_group.interface.items_tree:
                if (item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                        and item.socket_type == 'NodeSocketObject'):
                    ref = compat.try_get_gn_input_by_id(mod, item.identifier)
                    if ref is not None:
                        refs.add(ref)
    return refs


def _missing_styles(data):
    from .. import hb_project
    library = data.get("library")
    wanted = set((data.get("styles") or {}).get("door_styles", []))
    if not wanted:
        return []
    main = hb_project.get_main_scene()
    if library == 'FRAMELESS':
        existing = {s.name for s in main.hb_frameless.door_styles}
    elif library == 'FACE_FRAME':
        props = main.hb_face_frame
        existing = {s.name for s in props.door_styles} | {s.name for s in getattr(props, 'drawer_front_styles', [])}
    else:
        existing = set()
    return sorted(wanted - existing)


def load(context, entry):
    """Anexa o módulo; devolve (raiz, objetos carregados, avisos). Sem raiz → (None, objetos, avisos)."""
    warnings, data = [], None
    if entry.get("has_manifest"):
        with open(entry["json"], encoding="utf-8") as handle:
            data, _spec, errors = manifest.loads(handle.read())
        if errors:
            return None, [], [tr("Manifesto inválido: {}").format("; ".join(errors))]
    with bpy.data.libraries.load(entry["blend"], link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    loaded = [obj for obj in data_to.objects if obj is not None]
    for obj in loaded:
        context.scene.collection.objects.link(obj)
    roots = [obj for obj in loaded if obj.parent is None and classify.module_library(obj)]
    root = roots[0] if roots else None
    for ref in _geo_node_refs(loaded):
        ref.hide_set(True)
        ref.hide_viewport = True
        ref.hide_render = True
    if data is not None:
        missing = _missing_styles(data)
        if missing:
            warnings.append(tr("Estilos ausentes neste arquivo (mantida a geometria salva): {}").format(", ".join(missing)))
    if root is not None and data is not None:
        warnings += reapply.reapply(context, root)
    if root is not None:
        _renew_divisions(context, root)
    elif root is None:
        warnings.append(tr("Nenhum módulo encontrado no arquivo"))
    if missing:
        # O aviso geral de estilos ausentes substitui o aviso por estilo dos adaptadores (prefixo na língua atual).
        prefix = tr("Estilo '{}' não existe neste arquivo").split("{}")[0]
        warnings = [w for w in warnings if not w.startswith(prefix)]
    return root, loaded, common.unique(warnings)


def delete(entry):
    for key in ("blend", "png", "json"):
        if os.path.exists(entry[key]):
            os.remove(entry[key])


def rename(entry, new_name):
    """Renomeia os arquivos e o nome no manifesto; devolve mensagens de erro."""
    target = paths_for(new_name, entry["category"])
    if os.path.exists(target["blend"]):
        return [tr("Já existe um módulo '{}' nessa categoria").format(new_name)]
    for key in ("blend", "png", "json"):
        if os.path.exists(entry[key]):
            os.replace(entry[key], target[key])
    if os.path.exists(target["json"]):
        with open(target["json"], encoding="utf-8") as handle:
            data, _spec, errors = manifest.loads(handle.read())
        if not errors:
            data["name"] = new_name
            with open(target["json"], "w", encoding="utf-8") as handle:
                handle.write(manifest.dumps(data))
    return []
