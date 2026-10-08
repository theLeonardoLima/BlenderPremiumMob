"""Divisões acompanham o vão quando o módulo muda fora do editor (feature 006, T030; D-10, RN-16).

O frameless muda medidas por driver, sem passar por `after_rebuild`, e força os drivers trocando de quadro
(`hb_utils.run_calc_fix`), o que não gera `depsgraph_update_post`. Por isso há dois handlers:
- `depsgraph_update_post`: módulos com divisão que apareceram na atualização;
- `frame_change_post`: todos os módulos com divisão da cena.
Os dois chamam `scene_divisions.reflow`, que só trabalha quando a assinatura dos vãos mudou. Dentro do editor quem
reposiciona é a ponte; fora dele, estes handlers.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import props, scene_divisions

_running = [False]


def _roots(depsgraph):
    from ..customize import adapters
    seen = {}
    for update in depsgraph.updates:
        if not isinstance(update.id, bpy.types.Object):
            continue
        root = adapters.module_root(update.id.original)
        if root is None or root.name in seen:
            continue
        if scene_divisions.SIGNATURE_PROP in root:
            seen[root.name] = root
    return list(seen.values())


def _reflow(roots):
    if not roots:
        return
    _running[0] = True
    try:
        for root in roots:
            scene_divisions.reflow(bpy.context, root)
    except (ReferenceError, RuntimeError):
        pass                    # objeto apagado no meio da atualização: a próxima atualização refaz
    finally:
        _running[0] = False


@persistent
def on_depsgraph_update(scene, depsgraph):
    if _running[0] or props.session() is not None:
        return
    _reflow(_roots(depsgraph))


@persistent
def on_frame_change(scene, depsgraph=None):
    if _running[0] or props.session() is not None:
        return
    _reflow([obj for obj in scene.objects if scene_divisions.SIGNATURE_PROP in obj])


_HANDLERS = (('depsgraph_update_post', on_depsgraph_update), ('frame_change_post', on_frame_change))


def register():
    for name, fn in _HANDLERS:
        handlers = getattr(bpy.app.handlers, name)
        if fn not in handlers:
            handlers.append(fn)


def unregister():
    for name, fn in _HANDLERS:
        handlers = getattr(bpy.app.handlers, name)
        if fn in handlers:
            handlers.remove(fn)
