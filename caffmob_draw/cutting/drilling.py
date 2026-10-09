"""Furação das divisórias móveis (feature 008, T057; RN-10a, D-22, D-24).

Uma divisória **móvel** é regulável: as peças vizinhas do subvão onde ela corre recebem linhas de furos para pino de
prateleira, a 37 mm da frente e de trás, passo 32, na faixa do subvão.
- prateleira móvel (`HORIZONTAL`): furos nas peças à esquerda e à direita, ao longo de Z;
- divisória móvel (`VERTICAL`): furos nas peças de baixo e de cima, ao longo de X.

Núcleo puro (`pin_lines`, `to_json`) e o coletor da cena (`scene_drilling`), que acha a peça vizinha de cada lado
pela caixa no referencial da raiz e converte a linha para o referencial da peça (JSON `parts[].drilling`).
Contrato: `_reversa_forward/008-editor-armario-construtor/interfaces/cut-plan-json.md`.
"""

FRONT_MM = 37.0
PITCH_MM = 32.0
DIAMETER_MM = 5.0
DEPTH_MM = 10.0
TOUCH = 0.002                     # m: folga para considerar que a peça encosta na face do subvão

_SIDES = {'HORIZONTAL': (('LEFT', 0, 0), ('RIGHT', 0, 1)), 'VERTICAL': (('BOTTOM', 2, 0), ('TOP', 2, 1))}
_RUN_AXIS = {'HORIZONTAL': 2, 'VERTICAL': 0}
_AXIS_NAME = 'XYZ'


def pin_lines(space, orientation):
    """Linhas de furos (m, referencial da raiz) para uma divisória móvel no subvão `space` ((lo), (hi)).

    Cada linha: {side, normal_axis, normal_pos, axis, depth_pos, start, end}; a frente é o menor Y.
    """
    lo, hi = space
    run = _RUN_AXIS[orientation]
    front = FRONT_MM / 1000.0
    lines = []
    for side, normal_axis, end in _SIDES[orientation]:
        for depth_pos in (lo[1] + front, hi[1] - front):
            lines.append({"side": side, "normal_axis": normal_axis, "normal_pos": (lo, hi)[end][normal_axis],
                          "axis": _AXIS_NAME[run], "depth_pos": depth_pos, "start": lo[run], "end": hi[run]})
    return lines


def to_json(side_face, front_mm, start_mm, end_mm, source):
    return {"kind": "SHELF_PIN_LINE", "face": side_face, "diameter_mm": DIAMETER_MM, "depth_mm": DEPTH_MM,
            "x_mm": front_mm, "y_start_mm": start_mm, "y_end_mm": end_mm, "pitch_mm": PITCH_MM,
            "source_name": source}


def neighbor(line, boxes):
    """Chave da peça cuja face encosta na face do subvão e cobre a linha; None se não houver."""
    axis, pos = line["normal_axis"], line["normal_pos"]
    run = _AXIS_NAME.index(line["axis"])
    for key, (lo, hi) in boxes:
        face = hi[axis] if line["side"] in ('LEFT', 'BOTTOM') else lo[axis]
        if abs(face - pos) > TOUCH:
            continue
        if lo[1] - TOUCH <= line["depth_pos"] <= hi[1] + TOUCH and lo[run] < line["end"] and hi[run] > line["start"]:
            return key
    return None


def part_entry(line, box, face, source, precision=1):
    """(entrada JSON no referencial da peça, recortada?) — a faixa é cortada ao comprimento da peça."""
    run = _AXIS_NAME.index(line["axis"])
    start, end = max(line["start"], box[0][run]), min(line["end"], box[1][run])
    clipped = (start, end) != (line["start"], line["end"])
    mm = 1000.0
    return to_json(face, round((line["depth_pos"] - box[0][1]) * mm, precision),
                   round((start - box[0][run]) * mm, precision), round((end - box[0][run]) * mm, precision),
                   source), clipped


def sort_entries(entries):
    return sorted(entries, key=lambda e: (e["source_name"], e["x_mm"], e["y_start_mm"]))


# Coletor da cena -------------------------------------------------------------------------------------------------
_SYNTHETIC = {'LEFT': "Lateral esquerda", 'RIGHT': "Lateral direita", 'BOTTOM': "Base inferior",
              'TOP': "Base superior"}


def _face(obj, root, box, space):
    """TOP se a face +Z local da peça olha para o subvão; senão BOTTOM."""
    normal = (root.matrix_world.inverted().to_3x3() @ obj.matrix_world.to_3x3()).col[2]
    center = [(box[0][i] + box[1][i]) / 2.0 for i in range(3)]
    target = [(space[0][i] + space[1][i]) / 2.0 for i in range(3)]
    return 'TOP' if sum(normal[i] * (target[i] - center[i]) for i in range(3)) >= 0.0 else 'BOTTOM'


def scene_drilling(context, module):
    """{chave da peça: ([entradas], recortada?)} do módulo; chave = nome do objeto ou "synthetic:<papel>"."""
    from ..cabinet_editor import divisions as dv
    from ..cabinet_editor import scene_divisions
    from ..customize.adapters import common
    from . import part_sources
    root = module.obj
    data = [d for d in scene_divisions.read(root) if d.get('kind') == 'MOVABLE']
    if not data:
        return {}
    roots = scene_divisions.roots(context, root) or {}
    _spaces, cuts, _orphans = dv.resolve(roots, scene_divisions.core(context.scene, root))
    names = scene_divisions.names(root)
    depsgraph = context.evaluated_depsgraph_get()
    boxes, objs = [], {}
    for obj in root.children_recursive:
        if obj.type != 'MESH' or part_sources._cutpart_modifier(obj) is None or not part_sources._visible(obj):
            continue
        box = common.local_box(root, obj, depsgraph)
        if box:
            boxes.append((obj.name, box))
            objs[obj.name] = obj
    inner = None
    if module.library == "BTM" and roots:
        inner = roots[min(roots)]
    out = {}
    for entry in data:
        cut = cuts.get(entry['uid'])
        if cut is None:
            continue
        space = (tuple(cut[0].lo), tuple(cut[0].hi))
        source = names.get(entry['uid'], scene_divisions.NAME)
        for line in pin_lines(space, entry['orientation']):
            key = neighbor(line, [(k, b) for k, b in boxes if k != names.get(entry['uid'])])
            if key is not None:
                box = dict(boxes)[key]
                face = _face(objs[key], root, box, space)
            elif inner is not None and abs(line["normal_pos"] - (inner.lo, inner.hi)[
                    line["side"] in ('RIGHT', 'TOP')][line["normal_axis"]]) <= TOUCH:
                key = "synthetic:" + _SYNTHETIC[line["side"]]
                lo = list(inner.lo)
                if line["side"] in ('LEFT', 'RIGHT'):
                    lo[2] = 0.0                       # a lateral vai do chão ao topo do módulo
                box, face = (tuple(lo), tuple(inner.hi)), 'TOP'
            else:
                continue
            item, clipped = part_entry(line, box, face, source)
            entries, was = out.get(key, ([], False))
            out[key] = (entries + [item], was or clipped)
    return {k: (sort_entries(v[0]), v[1]) for k, v in out.items()}
