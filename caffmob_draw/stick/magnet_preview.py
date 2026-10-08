"""Prévia do ímã durante o arraste (feature 005, T030; RF-14, RF-15, RN-10, D-15).

Enquanto um movimento modal está rodando (G nativo, posicionamento do plugin) e o ímã está ligado, a viewport mostra a
face plana que o ímã alcança (contorno) e a caixa do item já girada e encostada nela (`magnet.preview_pose`), com o nome
do hospedeiro em texto. Nada no objeto muda: é só desenho, e some sozinho quando o movimento termina ou é cancelado; o
vínculo continua sendo gravado ao soltar (`settle.py`). Módulo posto na parede pela biblioteca e item já grudado não
têm prévia.
"""

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras.view3d_utils import location_3d_to_region_2d  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore

from ..data.i18n import tr
from ..selection import classify
from . import link, magnet, migrate

FACE_COLOR = (0.35, 0.85, 1.0, 1.0)
BOX_COLOR = (0.35, 0.85, 1.0, 0.75)
_EDGES = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))
_KINDS = (classify.MODULE, classify.GEOMETRY)
_handles = []
_last = [None]          # (hospedeiro, ponto, cantos da face, cantos da caixa) do último quadro


def _moving_item(context):
    """O item sendo arrastado: a prévia do posicionamento do plugin ou o objeto ativo durante um G."""
    from . import settle
    from .. import hb_placement
    running = False
    for window in context.window_manager.windows:
        for op in getattr(window, 'modal_operators', ()):
            if not settle.is_move_operator(op):
                continue
            running = True
            if isinstance(op, hb_placement.PlacementMixin):
                for name in ('preview_cage', 'cabinet', 'obj'):
                    candidate = getattr(op, name, None)
                    candidate = getattr(candidate, 'obj', candidate)
                    if isinstance(candidate, bpy.types.Object):
                        return candidate
    if not running:
        return None
    obj = context.active_object
    if obj is None:
        return None
    info = classify.classify(obj)
    if info is None or info.kind not in _KINDS or info.root is None:
        return None
    return info.root


def compute(context):
    enabled, distance = magnet.preferences()
    if not enabled:
        return None
    item = _moving_item(context)
    if item is None or item.btm_stick.is_stuck or migrate.wall_of(item) is not None:
        return None
    try:
        found = magnet.find(item, distance)
    except (ReferenceError, RuntimeError):
        return None
    if found is None:
        return None
    obj, location, normal, polygon = found
    try:
        box = magnet.preview_pose(item, location, normal)
    except (ReferenceError, RuntimeError, ValueError):
        return None
    return link.host_for(obj), location, polygon or [], box


def _lines(shader, coords, color, width, region):
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    shader.bind()
    shader.uniform_float("color", color)
    shader.uniform_float("lineWidth", width)
    shader.uniform_float("viewportSize", (region.width, region.height))
    batch.draw(shader)


def _draw_3d():
    context = bpy.context
    region = context.region
    _last[0] = compute(context) if region is not None else None
    data = _last[0]
    if data is None:
        return
    _host, _location, face, box = data
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('ALPHA')
    if len(face) >= 3:
        _lines(shader, [p for i in range(len(face)) for p in (face[i], face[(i + 1) % len(face)])], FACE_COLOR, 3.0,
               region)
    _lines(shader, [box[i] for edge in _EDGES for i in edge], BOX_COLOR, 2.0, region)
    gpu.state.blend_set('NONE')


def _draw_2d():
    context = bpy.context
    data = _last[0]
    region, rv3d = context.region, context.region_data
    if data is None or region is None or rv3d is None or data[0] is None:
        return
    co = location_3d_to_region_2d(region, rv3d, data[1])
    if co is None:
        return
    text = tr("Grudar em: {}").format(data[0].name)
    blf.size(0, 13)
    blf.color(0, 0.0, 0.0, 0.0, 0.85)
    blf.position(0, co.x + 11, co.y + 9, 0)
    blf.draw(0, text)
    blf.color(0, *FACE_COLOR)
    blf.position(0, co.x + 10, co.y + 10, 0)
    blf.draw(0, text)


def register():
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_3d, (), 'WINDOW', 'POST_VIEW'))
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_2d, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
    _last[0] = None
