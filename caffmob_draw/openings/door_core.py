"""Porta paramétrica da parede (feature 010, T012; RN-01, RN-02, D-07). Python puro, sem `bpy`.

Peças tiradas do gerador da porta realista do projeto (`docs/porta_realista_080x210/gerar_porta.py`, modelo
original): folha de 40 mm a 8 mm do piso com montantes, travessas, 2 almofadas e frisos; marco de 46 mm com 3 mm de
folga; batentes e vedações; guarnições de 72 mm com filete nos dois lados; 3 dobradiças com nós e parafusos;
maçanetas de alavanca, rosetas, cilindro, testa e lingueta. Larguras e alturas seguem a folha; ferragens e perfis têm
tamanho fixo. A profundidade do marco é a espessura da parede.

A medida da porta é a da **folha** ("porta de 80"). O furo na parede (a caixa) é a folha mais o marco e a folga:
`hole_size`. Referencial da caixa: x ao longo do furo (0 = borda esquerda), y na espessura da parede (0 a `wall`),
z para cima (0 = piso). As dobradiças e o giro ficam no lado `side` da parede (NEG_Y = y menor).
"""

from dataclasses import dataclass

FRAME, FRAME_HW, LEAF, LEAF_HW = 'FRAME', 'FRAME_HW', 'LEAF', 'LEAF_HW'
WOOD, METAL, RUBBER, SLOT, BRASS = 'WOOD', 'METAL', 'RUBBER', 'SLOT', 'BRASS'
LEAF_T = 0.040                 # espessura da folha
FLOOR_GAP = 0.008              # folga no piso
MARCO = 0.046                  # largura do marco
GAP = 0.003                    # folga lateral entre folha e marco
SIDE = MARCO + GAP             # da borda do furo à folha
TOP = 0.059                    # da folha ao topo do furo (folga, batente e marco superior)
CENTER_GAP = 0.003             # folga entre as folhas da porta dupla
HANDLE_Z = 1.02


@dataclass(frozen=True)
class Part:
    role: str
    name: str
    shape: str                 # 'BOX' ou 'CYL_X' / 'CYL_Y' / 'CYL_Z'
    center: tuple
    size: tuple                # BOX: (dx, dy, dz); CYL: (diâmetro, diâmetro, altura) no eixo do cilindro
    material: str = WOOD
    bevel: float = 0.001
    leaf: int = None
    horizontal: bool = False   # veio da madeira na horizontal

    @property
    def lo(self):
        return tuple(self.center[i] - self.size_xyz[i] / 2 for i in range(3))

    @property
    def hi(self):
        return tuple(self.center[i] + self.size_xyz[i] / 2 for i in range(3))

    @property
    def size_xyz(self):
        if self.shape == 'BOX':
            return self.size
        d, _d, h = self.size
        return {'CYL_X': (h, d, d), 'CYL_Y': (d, h, d), 'CYL_Z': (d, d, h)}[self.shape]


def hole_size(width, height, double=False):
    """Furo na parede (largura, altura) para a folha `width` × `height` (cada folha, na dupla)."""
    leaves = 2 * width + CENTER_GAP if double else width
    return round(leaves + 2 * SIDE, 6), round(height + TOP, 6)


def leaf_size(hole_w, hole_h, double=False):
    leaves = hole_w - 2 * SIDE
    return round((leaves - CENTER_GAP) / 2 if double else leaves, 6), round(hole_h - TOP, 6)


class _Builder:
    """Peças no referencial do gerador (folha de 0 a w em x, centrada em y = 0) e conversão para a caixa."""

    def __init__(self):
        self.parts = []

    def box(self, role, name, center, size, material=WOOD, bevel=0.001, leaf=None, horizontal=False):
        self.parts.append(Part(role, name, 'BOX', tuple(center), tuple(size), material, bevel, leaf, horizontal))

    def cyl(self, role, name, center, radius, depth, axis='Z', material=METAL, leaf=None):
        self.parts.append(Part(role, name, 'CYL_' + axis, tuple(center), (2 * radius, 2 * radius, depth), material,
                               0.00035, leaf))

    def screw_y(self, role, name, x, y, z, leaf=None):
        self.cyl(role, name, (x, y, z), 0.0034, 0.0015, 'Y', leaf=leaf)
        side = -1 if y < 0 else 1
        for size in ((0.0045, 0.0003, 0.0008), (0.0008, 0.0003, 0.0045)):
            self.box(role, name + "_fenda", (x, y + side * 0.00085, z), size, SLOT, 0.0001, leaf)


def _leaf(b, x0, w, h, leaf, hinge_left, lock):
    """Uma folha de x0 a x0 + w. `hinge_left`: dobradiças em x0 (senão em x0 + w); `lock`: tem fechadura."""
    def X(x):                                   # x medido do lado da dobradiça
        return x0 + x if hinge_left else x0 + w - x
    zc = FLOOR_GAP + h / 2
    b.box(LEAF, "Folha_montante_dobradicas", (X(0.055), 0, zc), (0.11, LEAF_T, h), leaf=leaf)
    b.box(LEAF, "Folha_montante_fechadura", (X(w - 0.055), 0, zc), (0.11, LEAF_T, h), leaf=leaf)
    z_low, z_mid, z_top = FLOOR_GAP + 0.07, FLOOR_GAP + h * (0.93 / 2.1), FLOOR_GAP + h - 0.065
    for name, z, height in (('inferior', z_low, 0.14), ('central', z_mid, 0.14), ('superior', z_top, 0.13)):
        b.box(LEAF, "Folha_travessa_" + name, (x0 + w / 2, 0, z), (w - 0.22, LEAF_T, height), leaf=leaf,
              horizontal=True)
    for index, (bottom, top) in enumerate(((z_low + 0.07, z_mid - 0.07), (z_mid + 0.07, z_top - 0.065))):
        b.box(LEAF, f"Almofada_{index}", (x0 + w / 2, 0, (bottom + top) / 2), (w - 0.218, 0.021, top - bottom + 0.002),
              leaf=leaf)
        for side in (-1, 1):
            y = side * 0.014
            for x in (0.117, w - 0.117):
                b.box(LEAF, "Friso_vertical", (x0 + x, y, (bottom + top) / 2), (0.014, 0.010, top - bottom),
                      bevel=0.0025, leaf=leaf)
            for z in (bottom + 0.007, top - 0.007):
                b.box(LEAF, "Friso_horizontal", (x0 + w / 2, y, z), (w - 0.248, 0.010, 0.014), bevel=0.0025,
                      leaf=leaf, horizontal=True)
    b.box(LEAF, "Vedacao_inferior", (x0 + w / 2, 0, FLOOR_GAP + 0.002), (w - 0.02, 0.021, 0.004), RUBBER, leaf=leaf)
    # dobradiças: chapa na folha (gira) e no marco (fixa), nós alternados
    hx = X(0.015)
    knuckle = X(-0.003)
    for z in (0.25, FLOOR_GAP + h / 2 - 0.008, FLOOR_GAP + h - 0.248):
        b.box(LEAF_HW, "Dobradica_folha", (hx, -0.0215, z), (0.032, 0.003, 0.09), METAL, leaf=leaf)
        b.box(FRAME_HW, "Dobradica_marco", (X(-0.019), -0.023, z), (0.032, 0.003, 0.09), METAL)
        for k in range(5):
            role = LEAF_HW if k % 2 == 0 else FRAME_HW
            b.cyl(role, "No_dobradica", (knuckle, -0.025, z - 0.036 + k * 0.018), 0.006, 0.0175,
                  leaf=leaf if role == LEAF_HW else None)
        for dz in (-0.047, 0.047):
            b.cyl(FRAME_HW, "Pino_dobradica", (knuckle, -0.025, z + dz), 0.0064, 0.003)
        for dz in (-0.030, 0.0, 0.030):
            b.screw_y(LEAF_HW, "Parafuso_dobradica", X(0.017), -0.024, z + dz, leaf=leaf)
            b.screw_y(FRAME_HW, "Parafuso_marco", X(-0.021), -0.026, z + dz)
    # maçanetas (as duas faces), roseta de chave, testa e lingueta
    hx = X(w - 0.064)
    lever = X(w - 0.117)
    for side in (-1, 1):
        y = side * 0.024
        b.cyl(LEAF_HW, "Roseta_macaneta", (hx, y, HANDLE_Z), 0.026, 0.008, 'Y', leaf=leaf)
        b.cyl(LEAF_HW, "Anel_macaneta", (hx, side * 0.029, HANDLE_Z), 0.0215, 0.002, 'Y', leaf=leaf)
        b.cyl(LEAF_HW, "Eixo_macaneta", (hx, side * 0.048, HANDLE_Z), 0.009, 0.038, 'Y', leaf=leaf)
        b.box(LEAF_HW, "Alavanca_macaneta", (lever, side * 0.069, HANDLE_Z), (0.125, 0.020, 0.017), METAL, 0.007,
              leaf)
        if lock:
            b.cyl(LEAF_HW, "Roseta_chave", (hx, y, HANDLE_Z - 0.088), 0.024, 0.008, 'Y', leaf=leaf)
            b.cyl(LEAF_HW, "Cilindro_chave", (hx, side * 0.029, HANDLE_Z - 0.084), 0.009, 0.003, 'Y', BRASS, leaf)
            b.box(LEAF_HW, "Rasgo_chave", (hx, side * 0.031, HANDLE_Z - 0.087), (0.002, 0.001, 0.014), SLOT, 0.0003,
                  leaf)
    if lock:
        edge = X(w + 0.001)
        b.box(LEAF_HW, "Testa_fechadura", (edge, 0, HANDLE_Z - 0.042), (0.002, 0.026, 0.18), METAL, leaf=leaf)
        b.box(LEAF_HW, "Lingueta", (X(w + 0.005), 0, HANDLE_Z), (0.010, 0.014, 0.014), BRASS, 0.002, leaf)
        b.box(FRAME_HW, "Contratesta", (X(w + 0.002), 0, HANDLE_Z), (0.002, 0.034, 0.088), METAL)


def _frame(b, span, h, wall, leaves):
    """Marco, batentes, vedações e guarnições em volta das folhas (de 0 a `span` em x, no referencial da folha)."""
    marco_h = h + 0.016
    for x, label in ((-0.026, 'esquerdo'), (span + 0.026, 'direito')):
        b.box(FRAME, "Marco_" + label, (x, 0, marco_h / 2), (MARCO, wall, marco_h))
        if leaves:
            inner = 0.020 if x < 0 else -0.020
            b.box(FRAME, "Batente_" + label, (x + inner, 0.034, marco_h / 2), (0.019, 0.024, marco_h), bevel=0.0015)
            b.box(FRAME, "Vedacao_" + label, (x + (0.023 if x < 0 else -0.023), 0.021, h / 2 + 0.006),
                  (0.010, 0.004, h), RUBBER)
    b.box(FRAME, "Marco_superior", (span / 2, 0, h + 0.036), (span + 0.098, wall, MARCO), horizontal=True)
    if leaves:
        b.box(FRAME, "Batente_superior", (span / 2, 0.034, h + 0.014), (span + 0.006, 0.024, 0.018), horizontal=True)
        b.box(FRAME, "Vedacao_superior", (span / 2, 0.021, h + 0.011), (span, 0.004, 0.004), RUBBER)
    face = wall / 2 + 0.0085
    for side in (-1, 1):
        for x in (-0.043, span + 0.043):
            b.box(FRAME, "Guarnicao_vertical", (x, side * face, (h + 0.044) / 2), (0.072, 0.017, h + 0.044), bevel=0.002)
            b.box(FRAME, "Filete_guarnicao", (x, side * (face + 0.011), (h + 0.04) / 2), (0.043, 0.006, h + 0.04),
                  bevel=0.0015)
        b.box(FRAME, "Guarnicao_superior", (span / 2, side * face, h + 0.08), (span + 0.158, 0.017, 0.072), bevel=0.002,
              horizontal=True)
        b.box(FRAME, "Filete_superior", (span / 2, side * (face + 0.011), h + 0.08), (span + 0.154, 0.006, 0.043),
              bevel=0.0015, horizontal=True)


def door_parts(width, height, wall, hinge='LEFT', side='NEG_Y', double=False, open_door=False):
    """Peças da porta no referencial da caixa. `width` e `height` são da folha (de cada folha, na dupla)."""
    b = _Builder()
    if open_door:
        span = width
    elif double:
        span = 2 * width + CENTER_GAP
        _leaf(b, 0.0, width, height, 0, True, True)
        _leaf(b, width + CENTER_GAP, width, height, 1, False, False)
    else:
        span = width
        _leaf(b, 0.0, width, height, 0, hinge == 'LEFT', True)
    _frame(b, span, height, wall, not open_door)
    flip = -1 if side == 'POS_Y' else 1
    out = []
    for p in b.parts:
        x, y, z = p.center
        out.append(Part(p.role, p.name, p.shape, (x + SIDE, wall / 2 + y * flip, z), p.size, p.material, p.bevel,
                        p.leaf, p.horizontal))
    return out
