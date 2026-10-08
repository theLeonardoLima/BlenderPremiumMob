"""Sugestão de grupos de peças pelo nome (feature 007, T010; RN-05, D-04). Python puro, sem `bpy`.

Peças cujo nome começa por `Folha`/`Leaf`/`Sash` são agrupadas pelos dois primeiros tokens do nome separados por `_`
(`Folha_Esquerda_Vidro` → `Folha_Esquerda`); o resto forma a esquadria. Sufixos do Blender (`.001`) são ignorados.
Ordem estável: as folhas por nome, a esquadria por último.
"""

import re

LEAF_WORDS = ('folha', 'leaf', 'sash')
FRAME_NAME = "Esquadria"
_SUFFIX = re.compile(r"\.\d{3}$")


def _clean(name):
    return _SUFFIX.sub("", name or "")


def leaf_key(name):
    """Nome do grupo de folha da peça, ou None se ela é da esquadria."""
    tokens = _clean(name).split("_")
    if len(tokens) >= 2 and tokens[0].lower() in LEAF_WORDS:
        return "_".join(tokens[:2])
    return None


def suggest(names):
    """[(nome do grupo, 'LEAF' | 'FRAME', [nomes])]."""
    leaves, frame = {}, []
    for name in names:
        key = leaf_key(name)
        if key is None:
            frame.append(name)
        else:
            leaves.setdefault(key, []).append(name)
    out = [(key, 'LEAF', members) for key, members in sorted(leaves.items())]
    if frame:
        out.append((FRAME_NAME, 'FRAME', frame))
    return out
