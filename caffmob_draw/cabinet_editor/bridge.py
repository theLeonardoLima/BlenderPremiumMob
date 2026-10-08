"""Ponte do Editor de Armário com a cena (feature 004, T044; D-21, D-22, D-23).

- `read_state(root)`: medidas (`selection/editing`) + personalização da 003 (`adapter.read`) + os valores crus de
  `btm_custom` (vãos, raiz e peças), para que reaplicar um instantâneo devolva exatamente o que havia.
- `apply_state(context, root, target)`: leva o módulo ao instantâneo. Muda só o que difere (medida, frente do vão,
  divisões internas), grava os campos crus de `btm_custom` e reaplica pela biblioteca. Chamado de dentro do modal do
  editor: os operadores das bibliotecas usados pelos adaptadores não criam passos de desfazer próprios (D-22).
- `edit(context, root, action, data)`: as edições do editor (frente, estilo, puxador, material, interior), as mesmas
  dos operadores de `customize/ops_customize.py`, sem passar por operador.
- `parts(root)`: caixas das peças no referencial da raiz, para a vista frontal (`elevation.Part`).
"""

from mathutils import Vector  # type: ignore

from ..customize import adapters, reapply, spec
from ..cutting import part_roles
from ..selection import classify, editing
from . import elevation, state as _state

CUSTOM_FIELDS = ('door_style', 'drawer_style', 'pull_model', 'pull_position', 'front_material', 'interior')
_LIBRARY_HOLDER = {'FACE_FRAME': 'face_frame_cabinet', 'CLOSETS': 'hb_closet_starter', 'BTM': 'btm_cabinet'}
_SKIP_TAGS = ('IS_CUTTING_OBJ', 'IS_2D_ANNOTATION', 'IS_DIMENSION', 'obj_x')


def info_of(root):
    return classify.classify(root)


def adapter_of(root):
    return adapters.for_root(root)


# Leitura ---------------------------------------------------------------------------------------------------
def _raw(root, adapter):
    openings = {}
    for path, opening in adapter.openings(root):
        custom = opening.btm_custom
        openings[path] = {name: getattr(custom, name) for name in CUSTOM_FIELDS}
    custom = root.btm_custom
    groups = {item.group: item.material for item in custom.group_materials}
    parts = {obj.name: obj.btm_custom.material for obj in root.children_recursive
             if getattr(obj, 'btm_custom', None) is not None and obj.btm_custom.material}
    return {"openings": openings, "pull_model": custom.pull_model, "pull_all_fronts": bool(custom.pull_all_fronts),
            "groups": groups, "parts": parts}


def read_state(root):
    info = info_of(root)
    adapter = adapter_of(root)
    dims = tuple(float(editing.get_dimension(info, f) or 0.0) for f in ('width', 'height', 'depth'))
    data = spec.to_dict(adapter.read(root)) if adapter is not None else {}
    if adapter is not None:
        data["_raw"] = _raw(root, adapter)
    return _state.EditorState(dims, data)


def library_limits(root, library):
    holder = getattr(root, _LIBRARY_HOLDER.get(library, ''), None)
    out = {}
    if holder is None:
        return out
    for field in ('width', 'height', 'depth'):
        prop = holder.bl_rna.properties.get(field)
        if prop is not None:
            out[field] = (max(prop.hard_min, 0.0), prop.hard_max)
    return out


# Escrita ---------------------------------------------------------------------------------------------------
def set_dimension(context, root, field, value):
    editing.set_dimension(context, info_of(root), field, value)


def _openings(root, adapter):
    return dict(adapter.openings(root))


def apply_state(context, root, target):
    """Leva o módulo ao instantâneo `target`; devolve os avisos da biblioteca."""
    adapter = adapter_of(root)
    messages = []
    current = read_state(root)
    for index, field in enumerate(('width', 'height', 'depth')):
        if abs(current.dimensions[index] - target.dimensions[index]) > 1e-7:
            set_dimension(context, root, field, target.dimensions[index])
    if adapter is None:
        return messages
    wanted = spec.from_dict(target.spec)
    now = spec.from_dict(current.spec)
    openings = _openings(root, adapter)
    for item in wanted.openings:
        opening = openings.get(item.path)
        cur = now.opening(item.path)
        if opening is None or cur is None:
            continue
        if item.front and (item.front, item.drawer_count) != (cur.front, cur.drawer_count):
            messages += adapter.set_front(context, root, opening, item.front, item.drawer_count or 1)
            openings = _openings(root, adapter)
            opening = openings.get(item.path, opening)
        if item.interior is not None and item.interior != cur.interior:
            messages += adapter.set_interior(context, root, opening, item.interior)
    raw = target.spec.get("_raw", {})
    openings = _openings(root, adapter)
    for path, fields in raw.get("openings", {}).items():
        opening = openings.get(path)
        if opening is None:
            continue
        for name, value in fields.items():
            if getattr(opening.btm_custom, name) != value:
                setattr(opening.btm_custom, name, value)
    custom = root.btm_custom
    custom.pull_model = raw.get("pull_model", custom.pull_model)
    custom.pull_all_fronts = raw.get("pull_all_fronts", custom.pull_all_fronts)
    groups = raw.get("groups", {})
    for group in spec.GROUPS:
        if custom.group_material(group) != groups.get(group, ""):
            custom.set_group_material(group, groups.get(group, ""))
    parts = raw.get("parts", {})
    for obj in root.children_recursive:
        if getattr(obj, 'btm_custom', None) is not None and obj.btm_custom.material != parts.get(obj.name, ""):
            obj.btm_custom.material = parts.get(obj.name, "")
    messages += reapply.reapply(context, root)
    return messages


def edit(context, root, action, data):
    """Uma edição do editor sobre o vão `data['path']`; devolve os avisos da biblioteca."""
    adapter = adapter_of(root)
    if adapter is None:
        return []
    opening = _openings(root, adapter).get(data.get('path', ''))
    if action == 'FRONT':
        if opening is None:
            return []
        current = adapter.read(root).opening(data.get('path', ''))
        if current is not None and (current.front, current.drawer_count or 0) == (
                data['front'], data.get('drawer_count', 1) if data['front'] == 'DRAWERS' else 0):
            return []                      # mesma frente: nada a refazer (o face frame reconstruiria o vão)
        return adapter.set_front(context, root, opening, data['front'], data.get('drawer_count', 1)) + \
            reapply.reapply(context, root)
    if action == 'STYLE':
        if opening is None:
            return []
        setattr(opening.btm_custom, 'door_style' if data.get('kind', 'DOOR') == 'DOOR' else 'drawer_style',
                data.get('style', ""))
    elif action == 'PULL':
        root.btm_custom.pull_all_fronts = bool(data.get('all_fronts'))
        if data.get('all_fronts'):
            root.btm_custom.pull_model = data.get('model', "")
            for _path, other in adapter.openings(root):
                other.btm_custom.pull_position = data.get('position', 'DEFAULT')
        elif opening is not None:
            opening.btm_custom.pull_model = data.get('model', "")
            opening.btm_custom.pull_position = data.get('position', 'DEFAULT')
    elif action == 'MATERIAL':
        target = data.get('target', 'GROUP')
        if target == 'GROUP':
            root.btm_custom.set_group_material(data['group'], data.get('material', ""))
        elif target == 'FRONTS' and opening is not None:
            opening.btm_custom.front_material = data.get('material', "")
    elif action == 'INTERIOR':
        if opening is None:
            return []
        inner = spec.Interior(int(data.get('shelves', 0)), int(data.get('dividers', 0)), int(data.get('drawers', 0)),
                              list(data.get('heights', [])))
        messages = adapter.set_interior(context, root, opening, inner)
        return messages or reapply.reapply(context, root)
    return reapply.reapply(context, root)


# Vista frontal ---------------------------------------------------------------------------------------------
def _own_corners(obj, to_root, depsgraph):
    if obj.type != 'MESH':
        return []
    evaluated = obj.evaluated_get(depsgraph)
    corners = [Vector(c) for c in evaluated.bound_box]
    if all(c.length < 1e-9 for c in corners):
        return []
    return [to_root @ c for c in corners]


def _kind(obj, opening_names):
    if obj.name in opening_names:
        return elevation.OPENING
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate:
        return elevation.AGGREGATE
    if classify.classify(obj).kind == classify.FRONT or obj.get('IS_CABINET_FRONT'):
        return elevation.FRONT
    code = part_roles.classify(obj.name, obj.get('hb_part_role'))
    return elevation.kind_from_role(code)


def root_box(root, depsgraph):
    from ..stick import apply as stick_apply
    return stick_apply.local_box(root, depsgraph)


def parts(context, root):
    """Peças visíveis do módulo como `elevation.Part`, com a origem no canto mínimo da caixa da raiz."""
    depsgraph = context.evaluated_depsgraph_get()
    adapter = adapter_of(root)
    opening_names = {o.name for _p, o in adapter.openings(root)} if adapter is not None else set()
    lo_root, _hi = root_box(root, depsgraph)
    shift = Vector(lo_root)
    to_root_world = root.matrix_world.inverted_safe()
    out = []
    for obj in root.children_recursive:
        if obj.name not in opening_names and (any(obj.get(tag) for tag in _SKIP_TAGS) or obj.hide_viewport
                                              or not obj.visible_get() or obj.display_type in {'WIRE', 'BOUNDS'}):
            continue                       # gaiolas em arame e auxiliares não são peças; os vãos entram tracejados
        corners = _own_corners(obj, to_root_world @ obj.matrix_world, depsgraph)
        if not corners:
            continue
        lo = tuple(min(c[i] for c in corners) - shift[i] for i in range(3))
        hi = tuple(max(c[i] for c in corners) - shift[i] for i in range(3))
        out.append(elevation.Part(obj.name, _kind(obj, opening_names), lo, hi))
    return out


def root_size(context, root):
    lo, hi = root_box(root, context.evaluated_depsgraph_get())
    return tuple(hi[i] - lo[i] for i in range(3))


def opening_of(root, name):
    """Caminho do vão que contém o componente `name` (o próprio vão, uma frente ou peça dentro dele)."""
    adapter = adapter_of(root)
    if adapter is None or not name:
        return None
    import bpy  # type: ignore
    obj = bpy.data.objects.get(name)
    best = None
    for path, opening in adapter.openings(root):
        node = obj
        while node is not None:
            if node == opening:
                if best is None or len(opening.children_recursive) < len(best[1].children_recursive):
                    best = (path, opening)
                break
            node = node.parent
    return best[0] if best else None
