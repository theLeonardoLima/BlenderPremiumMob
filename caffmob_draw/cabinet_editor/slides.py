"""Portas de correr (deslizantes) do armário (feature 008, T016; RN-13b, D-18). Python puro, sem `bpy`.

As folhas ficam **dentro** do vão interno, na frente, uma por trilho, com profundidade escalonada (`PITCH` por
trilho) e sobreposição `OVERLAP` entre vizinhas. Largura da folha = (largura do vão + (N − 1)·sobreposição) / N.
Trilhos superior e inferior ocupam a faixa de todos os trilhos. A folha 0 (esquerda) fica no trilho da frente; com
"invertido", a da direita vai para a frente. Estilos com gola, cava, perfil ou puxador integrado ganham um rasgo
vertical simples na borda de encontro (geometria simplificada; o estilo fica gravado).
"""

from dataclasses import dataclass

from . import catalog

PITCH = 0.020          # profundidade por trilho (folha de 18 + folga)
LEAF_THICKNESS = 0.018
OVERLAP = 0.030
TRACK_HEIGHT = 0.010
DEPTH_MARGIN = 0.050   # além dos trilhos, para não encostar no fundo
GROOVE = (0.020, 0.008)  # largura e profundidade do rasgo (m)


@dataclass(frozen=True)
class Leaf:
    index: int
    track: int
    box: tuple
    groove: tuple = None           # (x0, x1) do rasgo, no referencial da raiz; None = sem rasgo


@dataclass(frozen=True)
class Track:
    box: tuple


@dataclass(frozen=True)
class Layout:
    leaves: tuple
    tracks: tuple


def missing_depth(space, leaves):
    """None se o vão tem profundidade para os trilhos; senão a profundidade necessária (m)."""
    need = leaves * PITCH + DEPTH_MARGIN
    return None if space.size(1) + 1e-9 >= need else need


def layout(space, leaves, style_id, invert=False):
    (x0, y0, z0), (x1, _y1, z1) = space.lo, space.hi
    n = int(leaves)
    width = ((x1 - x0) + (n - 1) * OVERLAP) / n
    item = catalog.get(style_id)
    out = []
    for i in range(n):
        lx0 = x0 + i * (width - OVERLAP)
        track = (n - 1 - i) if invert else i
        fy0 = y0 + track * PITCH
        box = ((lx0, fy0, z0 + TRACK_HEIGHT), (lx0 + width, fy0 + LEAF_THICKNESS, z1 - TRACK_HEIGHT))
        groove = None
        if item is not None and item.groove:
            edge = lx0 + width if i == 0 else lx0                  # borda de encontro com a vizinha
            groove = (edge - GROOVE[0], edge) if i == 0 else (edge, edge + GROOVE[0])
        out.append(Leaf(i, track, box, groove))
    band = y0 + n * PITCH
    tracks = (Track(((x0, y0, z0), (x1, band, z0 + TRACK_HEIGHT))),
              Track(((x0, y0, z1 - TRACK_HEIGHT), (x1, band, z1))))
    return Layout(tuple(out), tracks)
