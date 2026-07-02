"""Closet library properties.

Three PropertyGroups:
- Closets_Scene_Props (Scene.hb_closets): library defaults + library UI.
- Closet_Starter_Props (Object.hb_closet_starter): live dimensions and
  starter-level options on each starter root cage.
- Closet_Bay_Props (Object.hb_closet_bay): per-bay overrides on each bay
  cage (width/lock, height, depth, floor-mounted, remove flags).

No drivers: every update callback routes through
types_closets.recalculate_closet_starter, which is guarded against
reentry (system writes during a recalc don't loop back here).
"""
import bpy
from bpy.types import PropertyGroup
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        EnumProperty,
        )

import os

from . import const_closets as const
from . import starter_presets


# ---------------------------------------------------------------------------
# Thumbnail previews (mirrors face_frame's preview-collection pattern)
# ---------------------------------------------------------------------------
preview_collections = {}


def get_starter_previews():
    if "starter_previews" not in preview_collections:
        import bpy.utils.previews
        preview_collections["starter_previews"] = bpy.utils.previews.new()
    return preview_collections["starter_previews"]


def get_thumbnail_path():
    return os.path.join(os.path.dirname(__file__), "closet_thumbnails")


def load_starter_thumbnail(name):
    """Icon id for a starter thumbnail (closet_thumbnails/<name>.png),
    or 0 when no render exists yet - callers fall back to a text button."""
    pcoll = get_starter_previews()
    if name in pcoll:
        return pcoll[name].icon_id
    path = os.path.join(get_thumbnail_path(), f"{name}.png")
    if os.path.exists(path):
        return pcoll.load(name, path, 'IMAGE').icon_id
    return 0


# ---------------------------------------------------------------------------
# Update callbacks
# ---------------------------------------------------------------------------
def _update_starter_prop(self, context):
    """Starter-level prop changed: recalc that starter. Lazy import so
    module load order can't create a cycle."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_bay_prop(self, context):
    """Bay-level prop changed (height/depth/floor/remove flags)."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_bay_width(self, context):
    """Bay width changed. System writes during redistribution are
    ignored; a user edit locks the bay so the value holds when the
    remaining widths are redistributed."""
    from . import types_closets
    root = types_closets.find_starter_root(self.id_data)
    if root is None:
        return
    root_id = id(root)
    if (root_id in types_closets._RECALCULATING
            or root_id in types_closets._DISTRIBUTING_WIDTHS):
        return
    self.width_locked = True
    types_closets.recalculate_closet_starter(root)


def _update_closet_selection_mode(self, context):
    """Apply visibility highlighting for the active closet selection
    mode (mirrors face_frame's update_face_frame_selection_mode)."""
    bpy.ops.hb_closets.toggle_mode(search_obj_name="")


# ---------------------------------------------------------------------------
# Object-level: starter root
# ---------------------------------------------------------------------------
class Closet_Starter_Props(PropertyGroup):

    width: FloatProperty(
        name="Width", description="Starter width (X)",
        default=const.DEFAULT_WIDTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    height: FloatProperty(
        name="Height", description="Panel height (Z)",
        default=const.BASE_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Panel depth (Y)",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    closet_type: EnumProperty(
        name="Closet Type",
        items=[
            ('BASE', "Base", "Floor-mounted base starter"),
            ('TALL', "Tall", "Floor-mounted full-height starter"),
            ('HANGING', "Hanging", "Wall-mounted hanging starter"),
            ('ISLAND', "Island", "Single-sided island starter"),
        ],
        default='BASE')  # type: ignore

    toe_kick_height: FloatProperty(
        name="Toe Kick Height",
        default=const.DEFAULT_TOE_KICK_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback",
        default=const.DEFAULT_TOE_KICK_SETBACK, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    include_countertop: BoolProperty(
        name="Include Countertop", default=False,
        update=_update_starter_prop)  # type: ignore


# ---------------------------------------------------------------------------
# Object-level: bay
# ---------------------------------------------------------------------------
class Closet_Bay_Props(PropertyGroup):

    bay_index: IntProperty(name="Bay Index", default=0)  # type: ignore

    width: FloatProperty(
        name="Width", description="Bay opening width",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_bay_width)  # type: ignore
    width_locked: BoolProperty(
        name="Lock Width",
        description="Hold this bay's width during redistribution",
        default=starter_presets.BAY_PROP_DEFAULTS['width_locked'])  # type: ignore

    height: FloatProperty(
        name="Height", description="Bay height (envelope, floor to top shelf)",
        default=const.BASE_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Bay depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore

    floor_mounted: BoolProperty(
        name="Floor Mounted",
        description="Bay sits on the floor with a toe kick; off = the bay "
                    "hangs from its top height (top and bottom fixed shelves)",
        default=True, update=_update_bay_prop)  # type: ignore
    remove_bottom: BoolProperty(
        name="Remove Bottom", default=starter_presets.BAY_PROP_DEFAULTS['remove_bottom'],
        update=_update_bay_prop)  # type: ignore
    remove_cleat: BoolProperty(
        name="Remove Cleat", default=starter_presets.BAY_PROP_DEFAULTS['remove_cleat'],
        update=_update_bay_prop)  # type: ignore


# ---------------------------------------------------------------------------
# Scene-level: defaults + library UI
# ---------------------------------------------------------------------------
class Closets_Scene_Props(PropertyGroup):

    # ----- Defaults (seed new starters; existing starters keep their values) -----
    default_closet_width: FloatProperty(
        name="Default Width", default=const.DEFAULT_WIDTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_bay_qty: IntProperty(
        name="Bays", description="Bay count for newly placed starters",
        default=const.DEFAULT_BAY_QTY, min=1, max=9)  # type: ignore
    default_panel_depth: FloatProperty(
        name="Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    base_panel_height: FloatProperty(
        name="Base Panel Height", default=const.BASE_PANEL_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    tall_panel_height: FloatProperty(
        name="Tall Panel Height", default=const.TALL_PANEL_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    hanging_panel_height: FloatProperty(
        name="Hanging Panel Height", default=const.HANGING_PANEL_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    hanging_top_height: FloatProperty(
        name="Hanging Top Height",
        description="Floor to the top of wall-mounted hanging starters",
        default=const.HANGING_TOP_HEIGHT, unit='LENGTH', precision=4)  # type: ignore
    panel_thickness: FloatProperty(
        name="Panel Thickness", default=const.PANEL_THICKNESS,
        unit='LENGTH', precision=4)  # type: ignore
    shelf_thickness: FloatProperty(
        name="Shelf Thickness", default=const.SHELF_THICKNESS,
        unit='LENGTH', precision=4)  # type: ignore
    countertop_thickness: FloatProperty(
        name="Countertop Thickness", default=const.COUNTERTOP_THICKNESS,
        unit='LENGTH', precision=4)  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height", default=const.DEFAULT_TOE_KICK_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback", default=const.DEFAULT_TOE_KICK_SETBACK,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Selection modes -----
    closet_selection_mode: EnumProperty(
        name="Closet Selection Mode",
        items=[
            ('Starters', "Starters", "Select whole closet starters"),
            ('Bays', "Bays", "Select bay cages"),
            ('Openings', "Openings", "Select opening cages"),
            ('Parts', "Parts", "Select individual parts"),
        ],
        default='Starters',
        update=_update_closet_selection_mode)  # type: ignore
    closet_selection_mode_enabled: BoolProperty(
        name="Enable Closet Selection Mode",
        description="Highlight objects matching the active selection mode",
        default=False,
        update=_update_closet_selection_mode)  # type: ignore

    # ----- Library UI state -----
    library_view_mode: EnumProperty(
        name="Library View",
        items=[
            ('THUMBNAIL', "Thumbnail", "Thumbnail tiles with previews",
             'IMGDISPLAY', 0),
            ('LIST', "List", "Compact text buttons", 'COLLAPSEMENU', 1),
        ],
        default='THUMBNAIL')  # type: ignore
    show_closet_sizes: BoolProperty(name="Show Closet Sizes", default=False)  # type: ignore
    show_starter_library: BoolProperty(name="Show Closet Starters", default=True)  # type: ignore

    def draw_library_ui(self, layout, context):
        col = layout.column(align=True)

        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, 'show_closet_sizes', text="Closet Sizes",
                 icon='TRIA_DOWN' if self.show_closet_sizes else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_closet_sizes:
            for prop_name in ('default_closet_width', 'default_panel_depth',
                              'base_panel_height', 'tall_panel_height',
                              'hanging_panel_height', 'hanging_top_height',
                              'panel_thickness', 'shelf_thickness',
                              'countertop_thickness', 'toe_kick_height',
                              'toe_kick_setback'):
                box.prop(self, prop_name)

        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, 'show_starter_library', text="Closet Starters",
                 icon='TRIA_DOWN' if self.show_starter_library else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_starter_library:
            row = box.row()
            row.label(text="Bays:")
            row.prop(self, 'default_bay_qty', text="")
            view = row.row(align=True)
            view.alignment = 'RIGHT'
            view.prop(self, 'library_view_mode', expand=True, icon_only=True)

            entries = starter_presets.STARTER_MENU_ENTRIES
            if self.library_view_mode == 'LIST':
                starters = box.column(align=True)
                starters.scale_y = 1.3
                for name, label, _desc in entries:
                    op = starters.operator('hb_closets.place_starter',
                                           text=label)
                    op.starter_name = name
                    op.bay_qty = self.default_bay_qty
            else:
                # Two tiles per row; tiles without a rendered thumbnail
                # degrade to the plain button.
                for i in range(0, len(entries), 2):
                    row = box.row(align=True)
                    for name, label, _desc in entries[i:i + 2]:
                        cell = row.column(align=True)
                        icon_id = load_starter_thumbnail(name)
                        if icon_id:
                            cell.template_icon(icon_value=icon_id, scale=4.0)
                        op = cell.operator('hb_closets.place_starter',
                                           text=label)
                        op.starter_name = name
                        op.bay_qty = self.default_bay_qty
                    if len(entries[i:i + 2]) == 1:
                        row.column(align=True)


classes = (
    Closet_Starter_Props,
    Closet_Bay_Props,
    Closets_Scene_Props,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hb_closets = PointerProperty(
        name="Closets Props", type=Closets_Scene_Props)
    bpy.types.Object.hb_closet_starter = PointerProperty(
        name="Closet Starter Props", type=Closet_Starter_Props)
    bpy.types.Object.hb_closet_bay = PointerProperty(
        name="Closet Bay Props", type=Closet_Bay_Props)


def unregister():
    for pcoll in preview_collections.values():
        try:
            bpy.utils.previews.remove(pcoll)
        except Exception:
            pass
    preview_collections.clear()
    if hasattr(bpy.types.Scene, 'hb_closets'):
        del bpy.types.Scene.hb_closets
    if hasattr(bpy.types.Object, 'hb_closet_starter'):
        del bpy.types.Object.hb_closet_starter
    if hasattr(bpy.types.Object, 'hb_closet_bay'):
        del bpy.types.Object.hb_closet_bay
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
