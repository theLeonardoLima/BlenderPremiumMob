"""Número de vãos do armário (feature 008, T015; RN-07b, D-15). Python puro, sem `bpy`.

N vãos = N − 1 divisórias verticais de vão inteiro, marcadas `bay`, em cadeia pelo espaço-raiz `s0`: a primeira
corta `s0`, a segunda corta a metade direita (`s0.b`), e assim por diante, todas com a mesma largura de vão. Mudar N
mantém as divisórias de vão que já existem (com a posição nova) e acrescenta ou tira só as do fim; as divisões comuns
(não `bay`) não são tocadas, exceto as que estavam dentro de uma divisória de vão removida (saem com ela).
"""

from dataclasses import replace

from . import divisions as dv

ROOT = 's0'
MAX_BAYS = 10


def _chain(index):
    return ROOT + ".b" * index


def plan(space, count, thickness):
    """[(caminho, offset)] das divisórias de vão para `count` vãos iguais no espaço `space` (Box)."""
    count = max(1, min(MAX_BAYS, int(count)))
    width = (space.size(0) - (count - 1) * thickness) / count
    return [(_chain(i), width) for i in range(count - 1)]


def count(divisions):
    return 1 + sum(1 for d in divisions if d.bay)


def apply(roots, divisions, count_, thickness):
    """Divisões com exatamente `count_` vãos."""
    if ROOT not in roots:
        return list(divisions)
    wanted = plan(roots[ROOT], count_, thickness)
    bays = sorted((d for d in divisions if d.bay), key=lambda d: dv.depth_of(d.space))
    out = list(divisions)
    for extra in bays[len(wanted):]:
        out, _removed = dv.remove(out, extra.uid)
    kept = {d.uid for d in bays[:len(wanted)]}
    for index, (space, offset) in enumerate(wanted):
        if index < len(bays) and bays[index].uid in kept:
            out = [replace(d, space=space, offset=offset, thickness=thickness) if d.uid == bays[index].uid else d
                   for d in out]
        else:
            out.append(dv.Division(dv.new_uid(), space, dv.VERTICAL, offset, thickness, bay=True))
    return out


def removed(before, after):
    """Uids das divisórias de vão que saíram (para os Ajustes automáticos)."""
    now = {d.uid for d in after}
    return [d.uid for d in before if d.bay and d.uid not in now]
