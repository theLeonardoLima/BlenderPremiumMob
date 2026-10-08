"""Varredura da abertura de uma folha com parada no primeiro contato (feature 003, T004; RN-11a, D-19).

Python puro: o teste de contato é uma função injetada `hit(value)` que devolve o objeto atingido (ou algo
verdadeiro) quando a folha, na abertura `value`, encosta em algo, e None/False quando está livre.
Unidades: graus no giro, metros no correr; quem chama escolhe `step` e `tolerance` coerentes.
"""

SWING_STEP, SWING_TOLERANCE = 2.0, 0.25        # graus
SLIDE_STEP, SLIDE_TOLERANCE = 0.01, 0.001      # metros


def sweep(current, target, hit, step, tolerance, close=False, floor=0.0, floor_contact=None):
    """Anda de `current` até `target`; devolve (valor alcançado, contato ou None).

    Sem `close`, fechar (target ≤ current) é livre (RN-11a da 003). Abrindo, avança em passos de `step`; no primeiro
    passo com contato refina por bissecção até o intervalo ser ≤ `tolerance` e para no último valor livre.

    Com `close` (feature 007, D-10), fechar também testa contato e não passa de `floor`; parar no `floor` devolve
    `floor_contact` como contato.
    """
    current, target = float(current), float(target)
    if target <= current:
        if not close:
            return target, None
        stop = max(target, float(floor))
        if stop >= current:
            return current, (floor_contact if float(floor) > target else None)
        reached, contact = sweep(-current, -stop, lambda v: hit(-v), step, tolerance)
        reached = -reached
        if contact is None and float(floor) > target:
            contact = floor_contact
        return reached, contact
    free = current
    while free < target:
        probe = min(free + step, target)
        contact = hit(probe)
        if contact:
            blocked = probe
            while blocked - free > tolerance:
                middle = (free + blocked) / 2.0
                found = hit(middle)
                if found:
                    blocked, contact = middle, found
                else:
                    free = middle
            return free, contact
        free = probe
    return target, None
