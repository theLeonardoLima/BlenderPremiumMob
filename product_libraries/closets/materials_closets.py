"""Closet material selection.

A bundled .blend of asset materials (assets/materials/library.blend)
feeds the scene-level material dropdowns in the closets sidebar: one
selection for the carcass (panels, shelves, kicks, countertops, bridge
shelves) and one for door/drawer fronts. Changing a dropdown re-applies
to every closet in the room; new placements pick the selection up
through ops_closet._apply_finish.

Materials are appended on first use and reused by name afterwards, so
switching back and forth never duplicates datablocks. Enum item tuples
are cached at module level - Blender's dynamic-enum callbacks require
the returned strings to stay referenced (the classic enum-items
lifetime gotcha).
"""
import os
import bpy


MATERIALS_BLEND = os.path.join(os.path.dirname(__file__), 'assets',
                               'materials', 'library.blend')

_names_cache = None
_enum_cache = None


def get_material_names():
    """Material names available in the bundled library blend (cached).
    Empty list when the blend is missing/unreadable - the dropdown then
    shows a single None entry and application no-ops."""
    global _names_cache
    if _names_cache is None:
        names = []
        try:
            # assets_only: the library carries helper datablocks (2D
            # display variants, glass for front panel types) that are
            # not user-facing choices - only asset-marked materials are.
            with bpy.data.libraries.load(
                    MATERIALS_BLEND, assets_only=True) as (src, _dst):
                names = sorted(src.materials)
        except Exception:
            names = []
        _names_cache = names
    return _names_cache


def material_enum_items(self, context):
    global _enum_cache
    if _enum_cache is None:
        items = [(n, n, "") for n in get_material_names()]
        _enum_cache = items or [('NONE', "None", "No materials library")]
    return _enum_cache


def refresh():
    """Drop the caches so a changed library blend re-scans."""
    global _names_cache, _enum_cache
    _names_cache = None
    _enum_cache = None


def load_material(name):
    """Existing-or-appended material by name; None when unavailable."""
    if not name or name == 'NONE':
        return None
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    try:
        with bpy.data.libraries.load(MATERIALS_BLEND) as (src, dst):
            if name in src.materials:
                dst.materials = [name]
    except Exception:
        return None
    return bpy.data.materials.get(name)


def apply_to_starter(root, carcass_name=None, front_name=None):
    """Assign the selected materials to every cutpart under a starter:
    fronts (door/drawer/hamper) get the front material, everything else
    the carcass material, on faces AND edge slots. Non-cutpart meshes
    (cages, rods, pulls, drawer boxes without slots) are skipped by the
    per-part exception guard. Returns True when anything could be
    applied - callers fall back to the cabinet-style finish on False.
    """
    from ... import hb_types
    from . import types_closets
    props = bpy.context.scene.hb_closets
    if carcass_name is None:
        carcass_name = getattr(props, 'closet_material', '')
    if front_name is None:
        front_name = getattr(props, 'closet_front_material', '')
    carcass = load_material(carcass_name)
    front = load_material(front_name)
    if carcass is None and front is None:
        return False
    front_roles = {types_closets.PART_ROLE_DOOR,
                   types_closets.PART_ROLE_DRAWER_FRONT}
    for child in root.children_recursive:
        if child.type != 'MESH':
            continue
        mat = (front if child.get('hb_part_role') in front_roles
               else carcass)
        if mat is None:
            continue
        part = hb_types.GeoNodeCutpart(child)
        try:
            part.set_input('Top Surface', mat)
            part.set_input('Bottom Surface', mat)
            part.set_input('Edge W1', mat)
            part.set_input('Edge W2', mat)
            part.set_input('Edge L1', mat)
            part.set_input('Edge L2', mat)
        except Exception:
            continue
    return True


def update_room(self=None, context=None):
    """Dropdown update callback: re-apply to every starter in the scene."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            apply_to_starter(obj)
