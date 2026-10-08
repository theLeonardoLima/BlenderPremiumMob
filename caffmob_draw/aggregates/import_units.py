"""Unidade do modelo importado (feature 007, T009; RN-01, D-01). Python puro, sem `bpy`.

Fornecedores mandam OBJ em milímetros; o Blender trabalha em metros. `AUTO` mede o modelo importado em escala 1: se a
maior medida passar de `AUTO_LIMIT` unidades, ele está em milímetros (uma janela de 1400 mm viraria 1400 m).
"""

SCALE = {'MM': 0.001, 'CM': 0.01, 'M': 1.0, 'IN': 0.0254}
AUTO_LIMIT = 50.0


def suggest(largest):
    """Unidade sugerida pela maior medida do modelo em escala 1."""
    return 'MM' if float(largest) > AUTO_LIMIT else 'M'


def scale_for(unit, largest):
    """Fator para metros; `AUTO` usa a sugestão."""
    return SCALE[suggest(largest) if unit == 'AUTO' else unit]
