"""Closet door/drawer front style selection.

One scene-level dropdown styles every closet front. Styles are
parameter presets for the shared CPM_5PIECEDOOR part modifier (the same
node group the cabinet libraries use):

  Narrow Shaker/Miter        2.25" frame all around
  Wide Shaker/Miter          3" frame all around
  Contemporary Shaker/Miter  2.5" stiles, 3" rails (2" on drawers)
  Combination                2.5" stiles, 3" rails (2" on drawers)
  Slab                       flat (no modifier)

Panel: 1/4" thick, flush inset. Each style carries a MINIMUM front
size; a front smaller than the minimum stays a slab so short drawer
stacks never grow squeezed frames.

AXIS NOTE: closet front cutparts run Length ACROSS and Width UP (the
opposite of the cabinet door parts the modifier was authored for), so
the 'Left/Right Stile' sockets render along the top/bottom edges here
and 'Top/Bottom Rail' along the sides. The writer below swaps the
values so the visible result matches the style names. For the
equal-width styles the swap is invisible; Contemporary/Combination is
where it matters.
"""
import bpy

from ...units import inch


FRONT_STYLES = [
    ('SLAB', "Slab", "Flat fronts"),
    ('NARROW_SHAKER', "Narrow Shaker", ""),
    ('NARROW_MITER', "Narrow Miter", ""),
    ('CONTEMPORARY_SHAKER', "Contemporary Shaker", ""),
    ('CONTEMPORARY_MITER', "Contemporary Miter", ""),
    ('WIDE_SHAKER', "Wide Shaker", ""),
    ('WIDE_MITER', "Wide Miter", ""),
    ('COMBINATION', "Combination", ""),
]

# stile / door rail / drawer rail widths (inches) + miter flag.
_SPECS = {
    'NARROW_SHAKER': (2.25, 2.25, 2.25, False),
    'NARROW_MITER': (2.25, 2.25, 2.25, True),
    'WIDE_SHAKER': (3.0, 3.0, 3.0, False),
    'WIDE_MITER': (3.0, 3.0, 3.0, True),
    'CONTEMPORARY_SHAKER': (2.5, 3.0, 2.0, False),
    'CONTEMPORARY_MITER': (2.5, 3.0, 2.0, True),
    'COMBINATION': (2.5, 3.0, 2.0, False),
}

# Minimum front sizes (height, width in inches) per style; smaller
# fronts stay slabs.
_MIN_SIZES = {
    'NARROW_SHAKER': (5.5, 8.0625),
    'NARROW_MITER': (6.23, 6.23),
    'WIDE_SHAKER': (9.5, 9.5),
    'WIDE_MITER': (9.5, 9.5),
    'CONTEMPORARY_SHAKER': (5.5, 8.5),
    'CONTEMPORARY_MITER': (6.23, 6.0625),
    'COMBINATION': (7.0, 7.0),
}

_PANEL_THICKNESS = inch(0.25)
_PANEL_INSET = 0.0


def current_style():
    return getattr(bpy.context.scene.hb_closets,
                   'closet_front_style', 'SLAB')


def _strip_style(front_obj):
    for mod in list(front_obj.modifiers):
        if mod.type == 'NODES' and 'Door Style' in mod.name:
            front_obj.modifiers.remove(mod)


def apply_style_to_front(front_obj, is_drawer, style=None):
    """Apply the selected style to one closet front cutpart. SLAB (and
    any front below the style's minimum size) strips the 'Door Style'
    modifier; otherwise the shared CPM_5PIECEDOOR modifier is
    added/updated with the style's widths. Called from the drawer/door
    layout passes every recalc, after the front's dims are written."""
    from ... import hb_types
    if style is None:
        style = current_style()
    spec = _SPECS.get(style)
    if spec is None:  # SLAB / unknown
        _strip_style(front_obj)
        return
    stile_in, rail_in, drawer_rail_in, miter = spec
    rail_in = drawer_rail_in if is_drawer else rail_in
    stile = inch(stile_in)
    rail = inch(rail_in)

    part = hb_types.GeoNodeCutpart(front_obj)
    try:
        f_width = part.get_input('Length')   # across
        f_height = part.get_input('Width')   # up
    except Exception:
        return
    min_h, min_w = _MIN_SIZES.get(style, (0.0, 0.0))
    if (f_height < inch(min_h) or f_width < inch(min_w)
            or f_width < 2.0 * stile + inch(1.0)
            or f_height < 2.0 * rail + inch(1.0)):
        _strip_style(front_obj)
        return

    existing = None
    for mod in front_obj.modifiers:
        if mod.type == 'NODES' and 'Door Style' in mod.name:
            existing = mod
            break
    if existing is not None:
        style_mod = hb_types.CabinetPartModifier()
        style_mod.obj = front_obj
        style_mod.mod = existing
    else:
        style_mod = part.add_part_modifier('CPM_5PIECEDOOR', 'Door Style')

    # Axis swap (see module docstring): the modifier's stile sockets run
    # along this part's horizontal edges, so rails go into the stile
    # sockets and stiles into the rail sockets.
    style_mod.set_input('Left Stile Width', rail)
    style_mod.set_input('Right Stile Width', rail)
    style_mod.set_input('Top Rail Width', stile)
    style_mod.set_input('Bottom Rail Width', stile)
    style_mod.set_input('Use Miter', miter)
    style_mod.set_input('Panel Thickness', _PANEL_THICKNESS)
    style_mod.set_input('Panel Inset', _PANEL_INSET)
    front_obj['DOOR_STYLE_NAME'] = style


def update_room(self=None, context=None):
    """Dropdown update callback: recalculate every starter - the front
    layout passes re-apply the style to each front."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.recalculate_closet_starter(obj)
