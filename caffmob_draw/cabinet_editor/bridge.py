"""Ponte do Editor de Armário com a cena (feature 004, T044; D-21, D-22, D-23).

- `read_state(root)`: medidas (`selection/editing`) + personalização da 003 (`adapter.read`) + os valores crus de
  `btm_custom` (vãos, raiz e peças), para que reaplicar um instantâneo devolva exatamente o que havia.
- `apply_state(context, root, target)`: leva o módulo ao instantâneo. Muda só o que difere (medida, frente do vão,
  divisões internas), grava os campos crus de `btm_custom` e reaplica pela biblioteca. Chamado de dentro do modal do
  editor: os operadores das bibliotecas usados pelos adaptadores não criam passos de desfazer próprios (D-22).
- `edit(context, root, action, data)`: as edições do editor (frente, estilo, puxador, material, interior), as mesmas
  dos operadores de `customize/ops_customize.py`, sem passar por operador.
- `parts(root)`: caixas das peças no referencial da raiz, para a vista frontal (`elevation.Part`).
- Feature 006 (T021; D-11): o instantâneo leva também a estrutura (`root.btm_structure`) e as divisões; `edit` ganha
  `ADD_DIVISION`, `EDIT_DIVISION`, `REMOVE_DIVISION`, `EDIT_PART`, `REMOVE_PART` e `RESTORE_PART`. A ordem importa:
  o registro em `btm_structure` muda **antes** do adaptador, porque o recálculo das bibliotecas reafirma o que estiver
  gravado.
"""

from mathutils import Vector  # type: ignore

from ..customize import adapters, reapply, spec
from ..customize.adapters import common
from ..cutting import part_roles
from ..selection import classify, editing
from . import divisions as dv
from . import elevation, scene_divisions, state as _state
from . import structure as st

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
    structure = root.btm_structure.to_dict() if getattr(root, 'btm_structure', None) is not None else {}
    return _state.EditorState(dims, data, structure, scene_divisions.read(root))


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
    messages += _apply_structure(context, root, current.structure, target.structure)
    if target.divisions != scene_divisions.read(root):
        scene_divisions.apply(context, root, target.divisions)
    else:
        scene_divisions.reflow(context, root, force=True)
    return messages


def edit(context, root, action, data):
    """Uma edição do editor sobre o vão `data['path']`; devolve os avisos da biblioteca."""
    if action in EDIT_006:
        return EDIT_006[action](context, root, data)
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
    code = part_roles.classify(obj.name, obj.get('hb_part_role'), component=obj.get(scene_divisions.COMPONENT_PROP))
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
    if adapter is not None:              # chapas que não são objetos (malha única do `btm`, feature 006)
        for name, _role, lo, hi in common.call(adapter, 'elevation_parts', context, root):
            out.append(elevation.Part(name, elevation.STRUCTURE, tuple(lo[i] - shift[i] for i in range(3)),
                                      tuple(hi[i] - shift[i] for i in range(3))))
    return out


def view_shift(context, root):
    """Origem da vista frontal no referencial da raiz (canto mínimo da caixa do módulo)."""
    lo, _hi = root_box(root, context.evaluated_depsgraph_get())
    return tuple(lo)


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


# Estrutura e divisões (feature 006, T021) -----------------------------------------------------------------------
def structure_rows(context, root):
    """[(papel, info, capacidades, estado)] na ordem de `structure.ROLES`, só dos papéis que o módulo tem."""
    adapter = adapter_of(root)
    if adapter is None:
        return []
    info = common.call(adapter, 'structure_info', context, root)
    caps = common.call(adapter, 'structure_caps', root)
    states = st.state_from_dict(root.btm_structure.to_dict())
    return [(role, info[role], caps.get(role, {}), states.get(role, st.RoleState()))
            for role in st.ROLES if role in info]


def configured_part(context, root, role):
    """(material, espessura em m) do componente do Configurador para o papel, na linha do módulo."""
    from ..data import dimension_schema as schema
    from ..standards import api
    line = scene_divisions.line_of(root)
    component = st.ROLE_COMPONENT[role]
    material = api.get_value(context.scene, schema.sheet_key(line, component, 'material')) or 'MDF'
    thickness = api.get_value_m(context.scene, schema.sheet_key(line, component, 'thickness')) or 0.0
    return str(material), float(thickness)


def _item(root, role):
    return root.btm_structure.item(role, create=True)


def _tidy(root, role):
    """Tira o registro do papel quando ele voltou ao padrão (nada removido nem sobrescrito)."""
    components = root.btm_structure.components
    for index, entry in enumerate(components):
        if entry.role == role and not entry.removed and not entry.thickness and not entry.material:
            components.remove(index)
            return


def remove_part(context, root, data):
    role, mode = data['role'], data.get('mode', st.KEEP)
    adapter = adapter_of(root)
    caps = common.call(adapter, 'structure_caps', root).get(role)
    if not caps or caps.get('remove'):
        return [caps.get('remove') if caps else common.tr(common.NO_LIBRARY_REASON)]
    mode, reason = st.allowed_mode(mode, caps.get('modes', {}))
    entry = _item(root, role)
    if entry.removed:
        return []
    entry.removed, entry.mode = True, mode
    messages = [reason] if reason else []
    messages += common.call(adapter, 'remove_part', context, root, role, mode)
    scene_divisions.reflow(context, root, force=True)
    return messages


def restore_part(context, root, data):
    role = data['role']
    entry = root.btm_structure.item(role)
    if entry is None or not entry.removed:
        return []
    mode = entry.mode
    entry.removed, entry.mode = False, st.KEEP
    messages = common.call(adapter_of(root), 'restore_part', context, root, role, mode)
    _tidy(root, role)
    scene_divisions.reflow(context, root, force=True)
    return messages


def edit_part(context, root, data):
    role = data['role']
    adapter = adapter_of(root)
    entry = _item(root, role)
    messages = []
    if 'thickness' in data:
        value = float(data['thickness'] or 0.0)
        caps = common.call(adapter, 'structure_caps', root).get(role, {})
        if caps.get('thickness'):
            return [caps['thickness']]
        if abs(entry.thickness - value) > 1e-9:
            entry.thickness = value
            messages += common.call(adapter, 'set_part_thickness', context, root, role, value)
    if 'material' in data:
        entry.material = data['material'] or ""
    messages += common.call(adapter, 'reaffirm', context, root)
    _tidy(root, role)
    scene_divisions.reflow(context, root, force=True)
    return messages


def _apply_structure(context, root, current, target):
    """Leva a estrutura do módulo de `current` a `target` (dicionários de `BTM_PG_Structure.to_dict`)."""
    messages = []
    now = st.state_from_dict(current)
    wanted = st.state_from_dict(target)
    for role in st.ROLES:
        a, b = now.get(role, st.RoleState()), wanted.get(role, st.RoleState())
        if a == b:
            continue
        if a.removed and (not b.removed or a.mode != b.mode):
            messages += restore_part(context, root, {'role': role})
        if (a.thickness, a.material) != (b.thickness, b.material):
            messages += edit_part(context, root, {'role': role, 'thickness': b.thickness, 'material': b.material})
        if b.removed and not (a.removed and a.mode == b.mode):
            messages += remove_part(context, root, {'role': role, 'mode': b.mode})
    return messages


def division_context(context, root):
    """(vãos-raiz, divisões como `divisions.Division`, dicionários crus, nomes {uid: objeto})."""
    raw = scene_divisions.read(root)
    return (scene_divisions.roots(context, root), scene_divisions.core(context.scene, root, raw), raw,
            scene_divisions.names(root))


def add_division(context, root, data):
    roots, core, raw, _names = division_context(context, root)
    _material, thickness = scene_divisions.configured(context.scene, root)
    added = dv.add(roots, core, data['space'], data['orientation'], thickness,
                   use_front=data.get('use_front', False), front=data.get('front', dv.DEFAULT_SETBACK),
                   use_back=data.get('use_back', False), back=data.get('back', dv.DEFAULT_SETBACK))[-1]
    entry = dict(dv.to_dict(added), thickness=0.0, material="")
    scene_divisions.apply(context, root, raw + [entry])
    return []


def edit_division(context, root, data):
    raw = scene_divisions.read(root)
    changes = {k: v for k, v in data.items() if k != 'uid'}
    scene_divisions.apply(context, root, [dict(d, **changes) if d['uid'] == data['uid'] else d for d in raw])
    return []


def remove_division(context, root, data):
    _roots, core, raw, _names = division_context(context, root)
    _rest, removed = dv.remove(core, data['uid'])
    scene_divisions.apply(context, root, [d for d in raw if d['uid'] not in removed])
    return []


EDIT_006 = {'ADD_DIVISION': add_division, 'EDIT_DIVISION': edit_division, 'REMOVE_DIVISION': remove_division,
            'EDIT_PART': edit_part, 'REMOVE_PART': remove_part, 'RESTORE_PART': restore_part}
