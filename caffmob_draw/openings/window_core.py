"""Janela paramétrica da parede (feature 010, T013; RN-10, D-14). Python puro, sem `bpy`. Modelo original.

Janela de correr de alumínio no furo da parede (a caixa): marco de 40 mm com a profundidade da parede, trilhos
superior e inferior, 2 folhas de perfil de 35 mm com vidro de 4 mm em trilhos diferentes (sobreposição de 50 mm no
meio), puxadores concha, guarnição na face interna e peitoril de granito de 20 mm com pingadeira, saindo 30 mm para os
dois lados. Mesmo referencial da porta (`door_core`): x ao longo do furo, y na espessura da parede, z para cima.
"""

from .door_core import FRAME, LEAF, LEAF_HW, Part

ALU, GLASS, STONE = 'ALU', 'GLASS', 'STONE'
PROFILE = 0.040                # marco
SASH = 0.035                   # perfil da folha
SASH_DEPTH = 0.030
GLASS_T = 0.004
OVERLAP = 0.050
SILL_T = 0.020
SILL_OUT = 0.030


def _box(parts, role, name, lo, hi, material, leaf=None, bevel=0.0008):
    center = tuple((lo[i] + hi[i]) / 2 for i in range(3))
    size = tuple(hi[i] - lo[i] for i in range(3))
    parts.append(Part(role, name, 'BOX', center, size, material, bevel, leaf))


def travel(width):
    """Curso de cada folha: do lugar fechado até o batente do marco do outro lado."""
    inner = width - 2 * PROFILE
    return round(inner - (inner / 2 + OVERLAP / 2), 6)


def window_parts(width, height, wall):
    """Peças da janela no furo `width` × `height` de uma parede `wall`."""
    w, h, P = width, height, PROFILE
    parts = []
    _box(parts, FRAME, "Marco_esquerdo", (0, 0, 0), (P, wall, h), ALU)
    _box(parts, FRAME, "Marco_direito", (w - P, 0, 0), (w, wall, h), ALU)
    _box(parts, FRAME, "Marco_inferior", (P, 0, 0), (w - P, wall, P), ALU)
    _box(parts, FRAME, "Marco_superior", (P, 0, h - P), (w - P, wall, h), ALU)
    mid = wall / 2
    tracks = (mid - 0.020, mid + 0.020)                  # eixo de cada trilho
    for name, z0, z1 in (("Trilho_inferior", P, P + 0.008), ("Trilho_superior", h - P - 0.008, h - P)):
        for y in tracks:
            _box(parts, FRAME, name, (P, y - 0.0015, z0), (w - P, y + 0.0015, z1), ALU)
    inner = w - 2 * P
    sash_w = inner / 2 + OVERLAP / 2
    z0, z1 = P + 0.005, h - P - 0.005
    for leaf, (x0, y) in enumerate(((P, tracks[0]), (w - P - sash_w, tracks[1]))):
        x1 = x0 + sash_w
        ya, yb = y - SASH_DEPTH / 2, y + SASH_DEPTH / 2
        _box(parts, LEAF, "Folha_montante", (x0, ya, z0), (x0 + SASH, yb, z1), ALU, leaf)
        _box(parts, LEAF, "Folha_montante", (x1 - SASH, ya, z0), (x1, yb, z1), ALU, leaf)
        _box(parts, LEAF, "Folha_travessa", (x0 + SASH, ya, z0), (x1 - SASH, yb, z0 + SASH), ALU, leaf)
        _box(parts, LEAF, "Folha_travessa", (x0 + SASH, ya, z1 - SASH), (x1 - SASH, yb, z1), ALU, leaf)
        _box(parts, LEAF, "Vidro", (x0 + SASH - 0.006, y - GLASS_T / 2, z0 + SASH - 0.006),
             (x1 - SASH + 0.006, y + GLASS_T / 2, z1 - SASH + 0.006), GLASS, leaf, 0.0)
        grip_x = x0 + SASH / 2 if leaf == 0 else x1 - SASH / 2          # no montante de fora de cada folha
        zc = (z0 + z1) / 2
        _box(parts, LEAF_HW, "Puxador_concha", (grip_x - 0.008, ya - 0.006, zc - 0.06), (grip_x + 0.008, ya, zc + 0.06),
             ALU, leaf, 0.003)
    face = wall
    for name, lo, hi in (("Guarnicao_esquerda", (-0.05, face, 0), (0, face + 0.012, h + 0.05)),
                         ("Guarnicao_direita", (w, face, 0), (w + 0.05, face + 0.012, h + 0.05)),
                         ("Guarnicao_superior", (-0.05, face, h), (w + 0.05, face + 0.012, h + 0.05))):
        _box(parts, FRAME, name, lo, hi, ALU)
    _box(parts, FRAME, "Peitoril", (-SILL_OUT, -SILL_OUT, -SILL_T), (w + SILL_OUT, wall + SILL_OUT, 0.0), STONE,
         bevel=0.002)
    _box(parts, FRAME, "Peitoril_pingadeira", (-SILL_OUT + 0.01, -SILL_OUT + 0.008, -SILL_T - 0.004),
         (w + SILL_OUT - 0.01, -SILL_OUT + 0.014, -SILL_T), STONE, bevel=0.0)
    return parts
