"""Validação do editor de armário (feature 004, T008; RN-03, D-24). Python puro, sem `bpy`.

Cada mensagem traz código, gravidade, componente, parâmetro, valor atual, faixa permitida e ação sugerida. Só erro
(`ERROR`) impede o Confirmar (`blocks`).

Códigos:
- `DIM-001` medida vazia; `DIM-002` não é número; `DIM-003` fora da faixa;
- `GEO-001` componente fora do volume do módulo (na vista frontal, com 1 mm de folga);
- `GEO-002` componentes internos (prateleiras, divisórias) sobrepostos mais que 1 mm;
- `CAT-001` seção sem suporte nesta biblioteca.
"""

from dataclasses import dataclass

from ..collision import obb as _obb
from ..data import units
from ..data.i18n import tr
from . import elevation

ERROR = 'ERROR'
WARNING = 'WARNING'
INFO = 'INFO'

TOLERANCE = 0.001       # m
DEFAULT_LIMITS = {'width': (0.01, 10.0), 'height': (0.01, 10.0), 'depth': (0.005, 10.0)}   # = selection.editing


@dataclass(frozen=True)
class Message:
    code: str
    severity: str
    component: str
    parameter: str = ''
    value: str = ''
    range: str = ''
    action: str = ''

    @property
    def blocks(self):
        return self.severity == ERROR


def limits_for(library_limits=None):
    """Faixa geral estreitada pela faixa da biblioteca, campo a campo."""
    out = dict(DEFAULT_LIMITS)
    for name, (lo, hi) in (library_limits or {}).items():
        base_lo, base_hi = out.get(name, (lo, hi))
        out[name] = (max(base_lo, lo), min(base_hi, hi))
    return out


def _fmt(value, unit):
    return units.format_length(value, unit)


def parse_dimension(name, text, limits, unit='MM'):
    """(valor em metros ou None, [mensagens]) para o texto digitado num campo de medida."""
    if text is None or not str(text).strip():
        return None, [Message('DIM-001', ERROR, '', name, '', '', tr("Digite uma medida"))]
    try:
        value = units.parse_length(text, default_unit=unit)
    except ValueError:
        return None, [Message('DIM-002', ERROR, '', name, str(text), '', tr("Use números com mm, cm ou m"))]
    return value, check_dimension(name, value, limits, unit)


def check_dimension(name, value, limits, unit='MM'):
    lo, hi = limits[name]
    if lo - 1e-9 <= value <= hi + 1e-9:
        return []
    span = "{} – {}".format(_fmt(lo, unit), _fmt(hi, unit))
    return [Message('DIM-003', ERROR, '', name, _fmt(value, unit), span, tr("Use um valor dentro da faixa"))]


def outside_volume(root_size, parts):
    """GEO-001: peça que passa da largura ou da altura do módulo (a frente pode passar em profundidade: puxador)."""
    width, _depth, height = root_size
    out = []
    for part in parts:
        if part.kind in (elevation.AGGREGATE, elevation.OPENING):
            continue
        x0, z0, x1, z1 = part.rect
        if x0 < -TOLERANCE or z0 < -TOLERANCE or x1 > width + TOLERANCE or z1 > height + TOLERANCE:
            severity = ERROR if part.kind in elevation.INTERIOR else WARNING
            out.append(Message('GEO-001', severity, part.name, '', '', '',
                               tr("Mova ou reduza o componente para dentro do módulo")))
    return out


def _box(part):
    return _obb.from_box((0.0, 0.0, 0.0), ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), part.lo, part.hi)


def internal_overlaps(parts):
    """GEO-002: prateleiras e divisórias que entram umas nas outras mais que 1 mm."""
    inner = sorted((p for p in parts if p.kind in elevation.INTERIOR), key=lambda p: p.name)
    out = []
    for i, a in enumerate(inner):
        for b in inner[i + 1:]:
            result = _obb.overlap(_box(a), _box(b))
            if result is not None and result['depth'] > TOLERANCE:
                out.append(Message('GEO-002', ERROR, a.name, '', b.name, '',
                                   tr("Mude a posição ou a quantidade das divisões")))
    return out


def unsupported(section, reason):
    """CAT-001: a seção não existe nesta biblioteca (o painel já a mostra desabilitada)."""
    return Message('CAT-001', WARNING, '', section, '', '', reason)


def blocking(messages):
    return any(m.blocks for m in messages)


def sort_messages(messages):
    order = {ERROR: 0, WARNING: 1, INFO: 2}
    return sorted(messages, key=lambda m: (order[m.severity], m.code, m.component, m.parameter))
