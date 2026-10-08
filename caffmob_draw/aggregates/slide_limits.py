"""Limites da folha de correr numa esquadria (feature 007, T011; RN-07, RN-07a, RN-09, D-08, D-10). Python puro.

Tudo em 1D, no eixo do trilho (X da esquadria). Intervalos são (mín., máx.).

- Sentido padrão: para o próprio lado (centro da folha comparado ao da esquadria).
- Pouco curso: curso livre menor que `LOW_TRAVEL_RATIO` da largura da folha (o painel avisa; nada muda sozinho).
- Batente de fechar pela outra folha: as folhas correm em trilhos distintos e nunca se tocam em 3D; o batente é manter
  entre os montantes a mesma relação do arquivo. Com a folha A abrindo no sentido `sA` (±1) e a outra folha deslocada
  `dB` da posição do arquivo, A não fecha além de `t = max(0, sA · dB)` (o quanto ela está aberta). Com a outra folha
  no lugar, é a própria posição do arquivo.
"""

LOW_TRAVEL_RATIO = 0.10


def default_direction(leaf, frame):
    center = (leaf[0] + leaf[1]) / 2.0
    return 'NEG_X' if center < (frame[0] + frame[1]) / 2.0 else 'POS_X'


def sign(direction):
    return 1.0 if direction == 'POS_X' else -1.0


def low_travel(free, leaf_width):
    return free < LOW_TRAVEL_RATIO * leaf_width


def rest_overlap(a, b):
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def close_stop(open_sign, other_shift):
    """Abertura mínima (no mesmo sentido e unidade do curso) a que a folha pode voltar ao fechar."""
    return max(0.0, open_sign * other_shift)
