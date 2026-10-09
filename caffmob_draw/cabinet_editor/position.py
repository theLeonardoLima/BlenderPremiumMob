"""Posição e movimentação da divisão selecionada (feature 008, T019; RN-07c, D-16). Python puro, sem `bpy`.

Cotas no subvão onde a divisão está: `front`/`back` são os recuos (anterior/posterior do Construtor); `low`/`high` são
as distâncias às faces de baixo e de cima (horizontal) ou esquerda e direita (vertical). Editar uma cota muda o
`offset`. As setas movem pelo **Passo**; o primeiro toque usa o **Passo inicial** quando ele é maior que zero. A
posição fica sempre na faixa válida (`divisions.offset_range`).
"""

from . import divisions as dv


def _size(space, division):
    return space.size(dv._AXIS[division.orientation])


def cotas(space, division):
    size = _size(space, division)
    return {'front': division.front if division.use_front else 0.0,
            'back': division.back if division.use_back else 0.0,
            'low': division.offset, 'high': size - division.offset - division.thickness}


def offset_from_cota(space, division, which, value):
    if which == 'low':
        return float(value)
    if which == 'high':
        return _size(space, division) - division.thickness - float(value)
    return division.offset


def step_move(space, division, direction, step, initial, first=False):
    """Novo `offset` depois de um toque de seta (`direction` = +1 ou −1), dentro da faixa válida."""
    amount = initial if first and initial > 0.0 else step
    lo, hi = dv.offset_range(space, division)
    return min(max(division.offset + direction * amount, lo), max(lo, hi))
