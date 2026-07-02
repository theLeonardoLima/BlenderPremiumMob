from . import props_closets
from . import menus_closets
from . import operators

NAMESPACE = "hb_closets"
MENU_NAME = "Closet"


def register():
    props_closets.register()
    menus_closets.register()
    operators.register()


def unregister():
    operators.unregister()
    menus_closets.unregister()
    props_closets.unregister()
