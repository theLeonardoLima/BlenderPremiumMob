"""Destaque das colisões na viewport (feature 004, T041; RF-22, D-17).

Enquanto houver ocorrências em `btm_collision`, desenha o contorno da caixa dos itens envolvidos (`POST_VIEW`) e, no
ponto da colisão, um rótulo de texto com o tipo e os nomes (`POST_PIXEL`): o estado não depende só de cor. Os handlers
ficam registrados com o add-on (mesmo padrão de `aggregates/overlay.py`) e não desenham nada sem ocorrências.
"""

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras.view3d_utils import location_3d_to_region_2d  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore

from ..data.i18n import tr
from . import props

COLOR = (1.0, 0.25, 0.2, 1.0)
STALE_COLOR = (1.0, 0.65, 0.2, 0.8)
_EDGES = ((0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7))
MAX_ROWS = 30
_handles = []
_LABELS = {key: label for key, label, _desc in props.KIND_ITEMS}


def _rows(context):
    state = getattr(context.window_manager, 'btm_collision', None)
    if state is None or not state.items:
        return None, ()
    return state, list(state.items)[:MAX_ROWS]


def _draw_3d():
    context = bpy.context
    state, rows = _rows(context)
    region = context.region
    if not rows or region is None:
        return
    from . import scan
    depsgraph = context.evaluated_depsgraph_get()
    coords = []
    seen = set()
    for row in rows:
        for name in (row.name_a, row.name_b):
            obj = bpy.data.objects.get(name)
            if obj is None or name in seen or not obj.visible_get():
                continue
            seen.add(name)
            corners = scan.box_of(obj, depsgraph).corners()
            coords.extend(corners[i] for edge in _EDGES for i in edge)
    if not coords:
        return
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('ALPHA')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    shader.bind()
    shader.uniform_float("color", STALE_COLOR if state.stale else COLOR)
    shader.uniform_float("lineWidth", 2.5)
    shader.uniform_float("viewportSize", (region.width, region.height))
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _draw_2d():
    context = bpy.context
    state, rows = _rows(context)
    region, rv3d = context.region, context.region_data
    if not rows or region is None or rv3d is None:
        return
    blf.size(0, 13)
    for row in rows:
        co = location_3d_to_region_2d(region, rv3d, row.location)
        if co is None:
            continue
        text = "{}: {} × {}".format(tr(_LABELS.get(row.kind, row.kind)), row.name_a, row.name_b)
        if state.stale:
            text = tr("{} (desatualizado)").format(text)
        blf.color(0, 0.0, 0.0, 0.0, 0.85)
        blf.position(0, co.x + 11, co.y + 9, 0)
        blf.draw(0, text)
        blf.color(0, *(STALE_COLOR if state.stale else COLOR))
        blf.position(0, co.x + 10, co.y + 10, 0)
        blf.draw(0, text)


def register():
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_3d, (), 'WINDOW', 'POST_VIEW'))
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_2d, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
