# Custom metadata for Blender add-on registration (fallback for legacy Blender versions)
bl_info = {
    "name": "Blender to Mob",
    "author": "TheLeoInfo",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > Blender to Mob",
    "description": "Parametric cabinetry and interior design CAD tools, including walls, floor, snapping, and nesting optimization.",
    "category": "Object",
}

# Handle automatic module reloading when developer runs "reload" in Blender
if "bpy" in locals():
    import importlib
    if "geometry" in locals():
        importlib.reload(geometry)
    if "cutting" in locals():
        importlib.reload(cutting)
    if "data" in locals():
        importlib.reload(data)
    if "operators" in locals():
        importlib.reload(operators)
    if "ui" in locals():
        importlib.reload(ui)
    if "overlays" in locals():
        importlib.reload(overlays)

import bpy
from . import geometry
from . import cutting
from . import data
from . import operators
from . import ui
from . import overlays

def register():
    # 1. Register data layer custom property groups
    data.register()
    
    # 2. Register operators
    operators.register()
    
    # 3. Register user interface panels and panel operators
    ui.register()
    
    # 4. Register GPU overlay draw handlers
    overlays.register()
    
    print("BlenderToMob: Add-on registered successfully.")

def unregister():
    # 1. Unregister GPU overlays first
    overlays.unregister()
    
    # 2. Unregister user interface
    ui.unregister()
    
    # 3. Unregister operators
    operators.unregister()
    
    # 4. Unregister data layer properties
    data.unregister()
    
    print("BlenderToMob: Add-on unregistered successfully.")

if __name__ == "__main__":
    register()
