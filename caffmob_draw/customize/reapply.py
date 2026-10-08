"""Reaplicar a personalização depois que a biblioteca reconstrói frentes ou materiais (feature 003, T026; D-04).

As bibliotecas chamam `after_rebuild(context, obj)` no fim das operações que recriam frentes ou reatribuem materiais;
o adaptador relê `btm_custom` (vãos, peças e raiz) e reaplica estilo, puxador e materiais. Módulo sem personalização
sai sem custo.

Feature 006 (T029; D-07, D-10): módulo com estrutura editada (`btm_structure`) ou com divisões também conta como
personalizado; depois de reaplicar, o adaptador reafirma remoções e espessuras e as divisões são reposicionadas.
"""

from . import adapters

_running = set()


DIVISION_SIGNATURE = 'btm_division_sig'     # = cabinet_editor.scene_divisions.SIGNATURE_PROP


def has_structure(root):
    structure = getattr(root, 'btm_structure', None)
    return bool(structure is not None and structure.components) or DIVISION_SIGNATURE in root


def has_custom(root):
    if has_structure(root):
        return True
    if root.btm_custom.group_materials or root.btm_custom.pull_all_fronts:
        return True
    for obj in [root] + list(root.children_recursive):
        custom = getattr(obj, 'btm_custom', None)
        if custom is None:
            continue
        if (custom.door_style or custom.drawer_style or custom.pull_model or custom.pull_position != 'DEFAULT'
                or custom.front_material or custom.material or custom.interior):
            return True
    return False


def reapply(context, root):
    """Reaplica pelo adaptador da biblioteca; devolve a lista de avisos."""
    adapter = adapters.for_root(root)
    if adapter is None or root.name in _running:
        return []
    _running.add(root.name)
    try:
        return adapter.reapply(context, root)
    finally:
        _running.discard(root.name)


def after_rebuild(context, obj):
    """Gancho das bibliotecas: `obj` é a raiz ou qualquer objeto do módulo."""
    root = adapters.module_root(obj)
    if root is None or not hasattr(root, 'btm_custom') or not has_custom(root):
        return []
    messages = reapply(context, root)
    if has_structure(root) and root.name not in _running:
        _running.add(root.name)
        try:
            from ..cabinet_editor import scene_divisions
            from .adapters import common
            messages += common.call(adapters.for_root(root), 'reaffirm', context, root)
            scene_divisions.reflow(context, root)
        finally:
            _running.discard(root.name)
    return messages
