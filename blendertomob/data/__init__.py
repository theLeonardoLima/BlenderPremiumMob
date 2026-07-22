# Módulo de Dados - Blender to Mob

# Recarrega submódulos se já importados
if "properties" in locals():
    import importlib
    importlib.reload(properties)
if "i18n" in locals():
    import importlib
    importlib.reload(i18n)

from . import properties
from . import i18n


def register():
    i18n.register()
    properties.register()


def unregister():
    properties.unregister()
    i18n.unregister()
