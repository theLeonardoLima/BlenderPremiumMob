"""Direção atual do lápis do editor de paredes (feature 009, T013; RN-05, RN-06, D-05). Python puro.

A direção é um ângulo no plano (radianos, 0 = para a direita, sentido anti-horário). Ela nasce do primeiro movimento
(com a trava ortogonal) e depois só muda por clique (direção do trecho criado) ou pelas setas do teclado; o movimento
do mouse sozinho nunca a muda.
"""

import math

ORTHO_TOLERANCE_DEG = 2.5                 # a mesma trava ortogonal do editor (canvas2d.view.ortho_snap)
ARROWS = {'RIGHT_ARROW': 0.0, 'UP_ARROW': math.pi / 2, 'LEFT_ARROW': math.pi, 'DOWN_ARROW': 3 * math.pi / 2}
_SYMBOLS = {0: "→", 90: "↑", 180: "←", 270: "↓"}


def _norm(angle):
    return angle % (2 * math.pi)


def next_point(start, angle, length):
    return (start[0] + math.cos(angle) * length, start[1] + math.sin(angle) * length)


def segment_direction(a, b):
    return _norm(math.atan2(b[1] - a[1], b[0] - a[0]))


def arrow_direction(key):
    return ARROWS.get(key)


def initial_direction(start, cursor, tolerance_deg=ORTHO_TOLERANCE_DEG):
    """Direção do primeiro movimento, encaixada em 0/90/180/270° quando estiver a até `tolerance_deg`."""
    dx, dy = cursor[0] - start[0], cursor[1] - start[1]
    if math.hypot(dx, dy) < 1e-12:
        return None
    degrees = math.degrees(math.atan2(dy, dx)) % 360.0
    nearest = round(degrees / 90.0) * 90.0
    if abs(degrees - nearest) <= tolerance_deg:
        return _norm(math.radians(nearest % 360.0))
    return _norm(math.radians(degrees))


def label(angle):
    """Texto da direção: "→ 0°" nas ortogonais, só o ângulo nas outras."""
    degrees = round(math.degrees(_norm(angle))) % 360
    symbol = _SYMBOLS.get(degrees)
    return f"{symbol} {degrees}°" if symbol else f"{degrees}°"
