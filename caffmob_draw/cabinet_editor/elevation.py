"""Vista frontal do módulo no editor de armário (feature 004, T007; D-23, D-25). Python puro, sem `bpy`.

Cada peça entra como uma caixa no referencial local da raiz do módulo (X largura, Y profundidade com a frente em −Y,
Z altura). A vista frontal é a projeção em (x, z). O nome do objeto é a identidade do componente: a lista do painel e a
vista usam o mesmo nome (RF-02).

`diff` compara as peças antes e depois de uma edição e devolve o que o recálculo mudou sozinho (RF-07, RN-02).
"""

from dataclasses import dataclass

TOLERANCE = 0.0001      # m; abaixo disso a peça não mudou

# Tipos de componente (a partir do código de `cutting/part_roles`)
FRONT = 'FRONT'
SHELF = 'SHELF'
DIVIDER = 'DIVIDER'
STRUCTURE = 'STRUCTURE'
OPENING = 'OPENING'
AGGREGATE = 'AGGREGATE'
PART = 'PART'
INTERIOR = {SHELF, DIVIDER}

_FROM_ROLE = {'POR': FRONT, 'PRAT': SHELF, 'DIV': DIVIDER, 'LAT': STRUCTURE, 'BAS': STRUCTURE, 'ROD': STRUCTURE,
              'TRA': STRUCTURE, 'FUN_INF': STRUCTURE, 'FUN_SUP': STRUCTURE, 'FUN_ALT': STRUCTURE,
              'TAMPON': STRUCTURE, 'SAR': STRUCTURE}

# Mudanças
MOVED = 'MOVED'
RESIZED = 'RESIZED'
ADDED = 'ADDED'
REMOVED = 'REMOVED'


def kind_from_role(code):
    return _FROM_ROLE.get(code or '', PART)


@dataclass(frozen=True)
class Part:
    name: str
    kind: str
    lo: tuple
    hi: tuple

    @property
    def rect(self):
        """(x0, z0, x1, z1) na vista frontal."""
        return self.lo[0], self.lo[2], self.hi[0], self.hi[2]

    @property
    def size(self):
        return tuple(self.hi[i] - self.lo[i] for i in range(3))


def draw_order(parts):
    """Do fundo para a frente (Y maior primeiro), para a frente ficar por cima no desenho."""
    return sorted(parts, key=lambda p: (-p.lo[1], p.name))


def hit(parts, x, z):
    """Componente sob o ponto (x, z) da vista: o mais à frente (menor Y); entre iguais, o menor em área."""
    inside = [p for p in parts if p.lo[0] <= x <= p.hi[0] and p.lo[2] <= z <= p.hi[2]]
    if not inside:
        return None
    best = min(inside, key=lambda p: (round(p.lo[1], 4), (p.hi[0] - p.lo[0]) * (p.hi[2] - p.lo[2]), p.name))
    return best.name


def bounds(parts):
    """(x0, z0, x1, z1) de todas as peças, ou None sem peças."""
    if not parts:
        return None
    return (min(p.lo[0] for p in parts), min(p.lo[2] for p in parts),
            max(p.hi[0] for p in parts), max(p.hi[2] for p in parts))


def _close(a, b):
    return all(abs(a[i] - b[i]) <= TOLERANCE for i in range(3))


def diff(before, after, targets=()):
    """[(nome, mudança)] em ordem de nome; `targets` (o que o usuário editou) fica de fora."""
    old = {p.name: p for p in before}
    new = {p.name: p for p in after}
    skip = set(targets)
    out = []
    for name in sorted(set(old) | set(new)):
        if name in skip:
            continue
        a, b = old.get(name), new.get(name)
        if a is None:
            out.append((name, ADDED))
        elif b is None:
            out.append((name, REMOVED))
        elif not _close(a.size, b.size):
            out.append((name, RESIZED))
        elif not _close(a.lo, b.lo):
            out.append((name, MOVED))
    return out
