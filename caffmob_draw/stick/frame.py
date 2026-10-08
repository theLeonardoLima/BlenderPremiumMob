"""Referencial da face em que um item está grudado (feature 004, T002, T003; D-01, D-02, RN-05, RN-06, RN-08a).

Python puro, sem `bpy`. Tudo é medido no referencial local do hospedeiro.

Uma face é um referencial `(origem, U, V, N)`: U e V estão no plano da face e N aponta para fora do hospedeiro.
- `BOX_SIDE`: um dos seis lados da caixa local avaliada do hospedeiro (`POS_X` ... `NEG_Z`). O plano acompanha o lado
  quando o hospedeiro muda de medida (espessura da parede, largura do painel); `u`/`v` são medidos a partir da origem
  local do hospedeiro, que não se move quando ele é redimensionado, então o item fica no lugar (RN-08a).
- `PLANE`: um plano fixo no referencial do hospedeiro, para face inclinada de uma malha qualquer; acompanha mover e
  girar, não acompanha mudança de medida.

A posição do item na face é `(u, v, distance)`: `u`/`v` vão da origem da face ao canto mínimo da pegada do item no plano,
e `distance` é a distância da face à parte do item mais próxima dela (0 = encostado; negativo = entra no hospedeiro).
"""

import math

from ..aggregates import limits

BOX_SIDE = 'BOX_SIDE'
PLANE = 'PLANE'
FACES = limits.FACES

PLANAR_TOLERANCE = 0.0005      # m; RN-05: vértices a até 0,5 mm do plano
ANGLE_TOLERANCE_DEG = 1.0      # normal a até 1° de um lado da caixa conta como esse lado
SIDE_TOLERANCE = 0.0005        # m; ponto a até 0,5 mm do lado da caixa
OUT_TOLERANCE = 0.001          # m; folga do teste "fora da face"


# Vetores ---------------------------------------------------------------------------------------------------
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _length(a):
    return math.sqrt(_dot(a, a))


def _normalized(a):
    length = _length(a)
    if length < 1e-12:
        raise ValueError("vetor nulo")
    return _scale(a, 1.0 / length)


def _axis(index, sign=1.0):
    v = [0.0, 0.0, 0.0]
    v[index] = sign
    return tuple(v)


# Referenciais ----------------------------------------------------------------------------------------------
def box_frame(host_box, face):
    """Referencial do lado `face` da caixa `host_box` = ((x, y, z) mín., (x, y, z) máx.)."""
    lo, hi = host_box
    n, sign, ua, va = limits.face_axes(face)
    origin = [0.0, 0.0, 0.0]
    origin[n] = hi[n] if sign > 0 else lo[n]
    return tuple(origin), _axis(ua), _axis(va), _axis(n, sign)


def plane_frame(origin, normal, up=(0.0, 0.0, 1.0)):
    """Referencial de um plano qualquer: U é a projeção de `up` no plano (ou X, se `up` for a normal)."""
    n = _normalized(normal)
    hint = up if abs(_dot(_normalized(up), n)) < 0.999 else (1.0, 0.0, 0.0)
    u = _normalized(_sub(hint, _scale(n, _dot(hint, n))))
    v = _cross(n, u)
    return tuple(origin), u, v, n


def frame_to_matrix(frame):
    """Matriz 4×4 (16 valores, por linha) com U, V, N e a origem nas colunas."""
    o, u, v, n = frame
    rows = [(u[i], v[i], n[i], o[i]) for i in range(3)] + [(0.0, 0.0, 0.0, 1.0)]
    return tuple(value for row in rows for value in row)


def matrix_to_frame(values):
    m = [tuple(values[r * 4:(r + 1) * 4]) for r in range(4)]
    column = [tuple(m[r][c] for r in range(3)) for c in range(4)]
    return column[3], column[0], column[1], column[2]


def frame_for(host_box, face_kind, face, plane_values):
    if face_kind == BOX_SIDE:
        return box_frame(host_box, face)
    return matrix_to_frame(plane_values)


# Posição do item na face -----------------------------------------------------------------------------------
def to_frame(frame, point):
    o, u, v, n = frame
    d = _sub(point, o)
    return _dot(d, u), _dot(d, v), _dot(d, n)


def from_frame(frame, coords):
    o, u, v, n = frame
    return _add(o, _add(_scale(u, coords[0]), _add(_scale(v, coords[1]), _scale(n, coords[2]))))


def footprint(frame, corners):
    """Caixa do item no referencial da face: ((u, v, n) mín., (u, v, n) máx.)."""
    coords = [to_frame(frame, c) for c in corners]
    return (tuple(min(c[i] for c in coords) for i in range(3)), tuple(max(c[i] for c in coords) for i in range(3)))


def params(frame, corners):
    """(u, v, distance) da posição atual do item (cantos no referencial do hospedeiro)."""
    lo, _hi = footprint(frame, corners)
    return lo


def shift(frame, corners, u=None, v=None, distance=None):
    """Deslocamento (no referencial do hospedeiro) que leva o item aos valores pedidos; `None` mantém o atual."""
    cur = params(frame, corners)
    target = (cur[0] if u is None else u, cur[1] if v is None else v, cur[2] if distance is None else distance)
    _o, ua, va, na = frame
    delta = (target[0] - cur[0], target[1] - cur[1], target[2] - cur[2])
    return _add(_scale(ua, delta[0]), _add(_scale(va, delta[1]), _scale(na, delta[2])))


def face_extent(host_box, face):
    """((mín. U, máx. U), (mín. V, máx. V)) do lado da caixa, no referencial da face."""
    _n, _sign, ua, va = limits.face_axes(face)
    lo, hi = host_box
    return (lo[ua], hi[ua]), (lo[va], hi[va])


def out_of_face(frame, corners, extent):
    """RN-08a: o centro da pegada do item saiu do retângulo da face. Face `PLANE` (sem extensão) nunca."""
    if extent is None:
        return False
    lo, hi = footprint(frame, corners)
    cu = (lo[0] + hi[0]) / 2.0
    cv = (lo[1] + hi[1]) / 2.0
    (u0, u1), (v0, v1) = extent
    tol = OUT_TOLERANCE
    return not (u0 - tol <= cu <= u1 + tol and v0 - tol <= cv <= v1 + tol)


# Escolha da face -------------------------------------------------------------------------------------------
def is_planar(points, normal, tolerance=PLANAR_TOLERANCE):
    """RN-05: todos os pontos a até `tolerance` do plano que passa pelo primeiro ponto com a normal dada."""
    if not points:
        return False
    try:
        n = _normalized(normal)
    except ValueError:
        return False
    base = points[0]
    return all(abs(_dot(_sub(p, base), n)) <= tolerance for p in points)


def choose_face(host_box, point, normal):
    """(`BOX_SIDE`, face) quando a normal e o ponto coincidem com um lado da caixa; senão (`PLANE`, None)."""
    try:
        n = _normalized(normal)
    except ValueError:
        return PLANE, None
    cos_tol = math.cos(math.radians(ANGLE_TOLERANCE_DEG))
    lo, hi = host_box
    for face in FACES:
        axis, sign, _u, _v = limits.face_axes(face)
        if _dot(n, _axis(axis, sign)) < cos_tol:
            continue
        plane = hi[axis] if sign > 0 else lo[axis]
        if abs(point[axis] - plane) <= SIDE_TOLERANCE:
            return BOX_SIDE, face
    return PLANE, None


def contact_axis(normal, up=(0.0, 0.0, 1.0)):
    """Qual lado do item encosta: 'BACK' (o fundo do módulo, +Y local) em face de pé; 'BOTTOM' em face deitada."""
    n = _normalized(normal)
    return 'BOTTOM' if abs(_dot(n, up)) >= 0.7 else 'BACK'
