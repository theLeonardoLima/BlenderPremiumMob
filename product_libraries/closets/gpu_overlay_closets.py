"""Editable dimension overlay for closet Starters / Bays / Openings modes.

Step 1 of the closet GPU editing surface (dims; toggles and content chips
follow). While the closet selection mode is active, a POST_PIXEL draw
handler paints value labels:

- Starters mode: W / H / D on every starter root. Committing writes the
  hb_closet_starter props, so bay propagation and the hanging top-anchor
  behave exactly like a sidebar edit.
- Bays mode: every bay's width (auto-locks on commit, pinned labels carry
  a bullet and right-click / 0-Enter resets to auto) PLUS every opening's
  height, so both are editable without a mode switch.
- Openings mode: opening heights.

Opening height is a DERIVED value in closets (bay height minus kick and
the two fixed shelves), so committing one inverse-writes the bay height.
Typing back the displayed value is a no-op by construction.

Architecture mirrors face_frame/dim_edit_overlay.py deliberately: a
permanent draw handler plus addon-keymap click operators that
PASS_THROUGH anything that isn't a label hit, so selection and tools are
untouched and no persistent modal blocks autosave. Labels are recomputed
on click rather than cached, so draw and hit-test can never drift.
"""

import bpy
import blf
import gpu
from mathutils import Vector
from bpy_extras import view3d_utils

from ... import units
from ... import hb_placement
from ...hb_types import GeoNodeCutpart
from ...hb_gpu_draw import get_visible_window_bounds
from . import types_closets
from . import const_closets as const
# Stale-matrix-safe cage readers (valid for cages created while hidden).
from ..face_frame import split_preview

# ---- Style (matches face_frame's overlay) ---------------------------------

FONT_SIZE       = 12
PAD_X           = 6
PAD_Y           = 4
LABEL_BG        = (0.13, 0.13, 0.14, 0.85)
LABEL_BG_DIM    = (0.13, 0.13, 0.14, 0.45)
LABEL_BORDER    = (1.0, 1.0, 1.0, 0.25)
EDIT_BG         = (0.20, 0.43, 0.70, 0.95)
TEXT_COLOR      = (0.95, 0.95, 0.95, 1.0)
TEXT_COLOR_DIM  = (0.95, 0.95, 0.95, 0.45)
EDIT_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)

_INPUT_CHARS = set("0123456789./-'\" ")

_HUD_MARGIN_Y = 12
_HUD_BTN_H = 24
_HUD_ROW_GAP = 6
_PILL_GAP = 4

# Widget-family filters. Each is (pill label, scene idprop key, kind
# prefixes it controls, modes it applies to). Scene idprops (default on)
# need no registration and save with the file.
_FILTERS = [
    ("Dims", 'hb_ov_show_dims',
     ('STARTER_', 'BAY_W', 'OPEN_H', 'PART_Z', 'DRAWER_H', 'TOGGLE_LOCK'),
     ('Starters', 'Bays', 'Openings')),
    ("Mount", 'hb_ov_show_mount',
     ('TOGGLE_FLOOR',), ('Bays',)),
    ("Contents", 'hb_ov_show_contents',
     ('CHIP_CONTENTS',), ('Bays', 'Openings')),
    ("Bays +/-", 'hb_ov_show_structure',
     ('PILL_INS', 'PILL_DELETE'), ('Bays',)),
]


def _filter_on(scene, key):
    return bool(scene.get(key, 1))


def _kind_visible(scene, kind):
    for _label, key, prefixes, _modes in _FILTERS:
        if kind.startswith(prefixes):
            return _filter_on(scene, key)
    return True

# Label kinds. STARTER_* commit hb_closet_starter props; BAY_W commits
# the bay width (auto-lock); OPEN_H inverse-writes the bay height.
KIND_ITEMS = [
    ('STARTER_W', "Starter Width", ""),
    ('STARTER_H', "Starter Height", ""),
    ('STARTER_D', "Starter Depth", ""),
    ('BAY_W', "Bay Width", ""),
    ('OPEN_H', "Opening Height", ""),
    # Per-part height (fixed shelf underside / rod center, opening-local)
    ('PART_Z', "Part Height", ""),
    # Drawer stack front height (opening idprop)
    ('DRAWER_H', "Drawer Front Height", ""),
]

# ---- Module state ----------------------------------------------------------

_draw_handle = None
_shutdown = False
_edit = None   # {'name', 'kind', 'typed', 'owner'} while an edit runs
_addon_keymaps = []


class _DistanceParser:
    """Borrow the placement mixin's typed-distance grammar. All four
    methods are needed - parse_typed_distance calls the other three
    through self (face_frame's overlay lends the same set)."""
    parse_typed_distance = hb_placement.PlacementMixin.parse_typed_distance
    _parse_feet_inches = hb_placement.PlacementMixin._parse_feet_inches
    _extract_number = hb_placement.PlacementMixin._extract_number
    _number_to_scene_units = hb_placement.PlacementMixin._number_to_scene_units
    typed_value = ""


_parser = _DistanceParser()


def parse_distance(text):
    """Typed string -> metres, or None. Same grammar as placement typing."""
    try:
        return _parser.parse_typed_distance(text)
    except Exception:
        return None


# ---- Gating ----------------------------------------------------------------

def _active_mode(context):
    """'Starters' / 'Bays' / 'Openings' when the overlay should draw."""
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return None
    hb = getattr(scene, 'home_builder', None)
    if getattr(hb, 'product_tab', '') != 'CLOSET':
        return None
    props = getattr(scene, 'hb_closets', None)
    if props is None or not getattr(props, 'closet_selection_mode_enabled', False):
        return None
    mode = getattr(props, 'closet_selection_mode', '')
    return mode if mode in ('Starters', 'Bays', 'Openings') else None


def _filter_pill_rects(context, area, mode):
    """[(label, key, rect)] for the filter pills applicable to the
    active mode - one centered row below the HUD's mode picker. The
    trailing 'Grab' pill (key None sentinel '__grab__') toggles the
    boundary-grab modal instead of a visibility family."""
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    x_min, x_max, _y_min, y_max = get_visible_window_bounds(area)
    blf.size(0, FONT_SIZE * s)
    pills = [(label, key) for label, key, _p, modes in _FILTERS
             if mode in modes]
    pills.append(("Grab", '__grab__'))
    widths = [blf.dimensions(0, label)[0] + 24 * s for label, _k in pills]
    h = _HUD_BTN_H * s
    total = sum(widths) + _PILL_GAP * s * max(0, len(pills) - 1)
    row1_y = y_max - _HUD_MARGIN_Y * s - h
    y = row1_y - (h + _HUD_ROW_GAP * s)
    x = x_min + ((x_max - x_min) - total) / 2.0
    rects = []
    for (label, key), w in zip(pills, widths):
        rects.append((label, key, (x, y, w, h)))
        x += w + _PILL_GAP * s
    return rects


# ---- Label collection --------------------------------------------------------

def _iter_starter_roots(scene):
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            yield obj


def _iter_bay_cages(starter):
    for child in starter.children:
        if child.get(types_closets.TAG_BAY_CAGE):
            yield child


def _iter_opening_cages(bay):
    for child in bay.children:
        if child.get(types_closets.TAG_OPENING_CAGE):
            yield child


def _anchor_world(cage, fx, fz):
    """World point on a cage's front face at fractional X / Z."""
    dim_x, dim_z = split_preview._cage_dims(cage)
    if dim_x <= 0.0 or dim_z <= 0.0:
        return None
    mw = split_preview._world_matrix(cage)
    return mw @ Vector((dim_x * fx, -0.003, dim_z * fz))


def _starter_label_targets(starter):
    """(kind, anchor, value) for the three starter dims. Each label sits
    where its edit ACTS (Andrew's layout): H at the top edge centered -
    the edge that moves when you change the height; W dead-center of the
    front face; D on the bottom-front edge centered on the width. Values
    come from the SAME props a commit writes so typing them back is a
    no-op."""
    sp = starter.hb_closet_starter
    return [
        ('STARTER_H', _anchor_world(starter, 0.5, 1.0), sp.height, "H "),
        ('STARTER_W', _anchor_world(starter, 0.5, 0.5), sp.width, "W "),
        ('STARTER_D', _anchor_world(starter, 0.5, 0.0), sp.depth, "D "),
    ]


def compute_labels(context, region, rv3d):
    """[(obj_name, kind, editable, locked, rect, text)] currently on
    screen. Shared by draw and the click operators."""
    mode = _active_mode(context)
    if mode is None or rv3d is None:
        return []
    scene = context.scene
    unit_settings = scene.unit_settings
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    blf.size(0, FONT_SIZE * s)

    targets = []   # (obj, kind, editable, locked, anchor, value, prefix)
    for starter in _iter_starter_roots(scene):
        if mode == 'Starters':
            for kind, anchor, value, prefix in _starter_label_targets(starter):
                targets.append((starter, kind, True, False,
                                anchor, value, prefix))
            continue
        # Same placement rule as the starter labels: a label sits where
        # its edit ACTS. Bay width = mid-face of the bay (panels move
        # sideways around it); opening height = the opening's top edge;
        # part labels ride the part they move.
        for bay in _iter_bay_cages(starter):
            if mode == 'Bays':
                bp = bay.hb_closet_bay
                targets.append((bay, 'BAY_W', True, bp.width_locked,
                                _anchor_world(bay, 0.5, 0.5),
                                bp.width, ""))
            if mode == 'Openings':
                # Splitting fixed shelves live at BAY level; their label
                # rides the shelf and edits its bay-interior offset.
                b_mw = split_preview._world_matrix(bay)
                b_w, _bh = split_preview._cage_dims(bay)
                for child in bay.children:
                    if (child.get('hb_part_role')
                            == types_closets.PART_ROLE_FIXED_SHELF
                            and not child.get('hb_preview')):
                        anchor = b_mw @ Vector(
                            (b_w / 2.0, -0.003, child.location.z))
                        targets.append((child, 'PART_Z', True, False,
                                        anchor,
                                        child.get('hb_z_offset', 0.0), ""))
            for opening in _iter_opening_cages(bay):
                o_w, interior_h = split_preview._cage_dims(opening)
                targets.append((opening, 'OPEN_H', True, False,
                                _anchor_world(opening, 0.5, 1.0),
                                interior_h, ""))
                if mode != 'Openings':
                    continue
                # Per-part labels: fixed shelves and rods show their
                # opening-local height at the part itself; a drawer
                # stack shows its front height at the stack's top edge.
                o_mw = split_preview._world_matrix(opening)
                top_front_z = None
                for child in opening.children:
                    role = child.get('hb_part_role')
                    if (role == types_closets.PART_ROLE_ROD
                            and not child.get('hb_preview')):
                        anchor = o_mw @ Vector(
                            (o_w / 2.0, -0.003, child.location.z))
                        targets.append((child, 'PART_Z', True, False,
                                        anchor, child.location.z, ""))
                    elif role == types_closets.PART_ROLE_DRAWER_FRONT:
                        if (top_front_z is None
                                or child.location.z > top_front_z):
                            top_front_z = child.location.z
                if top_front_z is not None:
                    dh = opening.get(
                        types_closets.PROP_DRAWER_FRONT_HEIGHT,
                        const.DRAWER_FRONT_HEIGHT)
                    anchor = o_mw @ Vector(
                        (o_w / 2.0, -0.003, top_front_z + dh))
                    targets.append((opening, 'DRAWER_H', True, False,
                                    anchor, dh, ""))

    labels = []
    for obj, kind, editable, locked, anchor, value, prefix in targets:
        if anchor is None:
            continue
        pt = view3d_utils.location_3d_to_region_2d(region, rv3d, anchor)
        if pt is None:
            continue
        text = prefix + units.unit_to_string(unit_settings, value)
        # BAY_W carries a dedicated lock glyph (added below) instead of
        # the bullet prefix.
        if locked and kind != 'BAY_W':
            text = "• " + text
        tw, th = blf.dimensions(0, text)
        w = tw + 2 * PAD_X * s
        h = th + 2 * PAD_Y * s
        rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
        if rect[0] + w < 0 or rect[0] > region.width:
            continue
        if rect[1] + h < 0 or rect[1] > region.height:
            continue
        labels.append((obj.name, kind, editable, locked, rect, text))

    # ----- Toggle widgets (Bays mode). Reuses the label tuple shape:
    # editable=False keeps them out of the edit modal; the ``locked``
    # slot carries the ACTIVE state for pill coloring. -----
    if mode == 'Bays':
        bay_w_rects = {name: rect for name, kind, _e, _l, rect, _t in labels
                       if kind == 'BAY_W'}
        for starter in _iter_starter_roots(scene):
            for bay in _iter_bay_cages(starter):
                bp = bay.hb_closet_bay
                # Lock glyph flush right of the bay's width label.
                lrect = bay_w_rects.get(bay.name)
                if lrect is not None:
                    glyph = "•" if bp.width_locked else "○"
                    gw, _gh = blf.dimensions(0, glyph)
                    gh = lrect[3]
                    grect = (lrect[0] + lrect[2] + 2 * s, lrect[1],
                             gw + 2 * PAD_X * s, gh)
                    labels.append((bay.name, 'TOGGLE_LOCK', False,
                                   bp.width_locked, grect, glyph))
                # Floor/Hung pill straddling the bay's bottom edge -
                # where the mount condition acts.
                anchor = _anchor_world(bay, 0.5, 0.0)
                if anchor is None:
                    continue
                pt = view3d_utils.location_3d_to_region_2d(
                    region, rv3d, anchor)
                if pt is None:
                    continue
                text = "Floor" if bp.floor_mounted else "Hung"
                tw, th = blf.dimensions(0, text)
                w = tw + 2 * PAD_X * s
                h = th + 2 * PAD_Y * s
                rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
                if (rect[0] + w < 0 or rect[0] > region.width
                        or rect[1] + h < 0 or rect[1] > region.height):
                    continue
                labels.append((bay.name, 'TOGGLE_FLOOR', False,
                               not bp.floor_mounted, rect, text))

    # ----- Structural pills (Bays mode): a "+" on every panel inserts a
    # bay at that boundary (panel i = left panel of bay i, so the last
    # panel inserts AFTER the last bay); an "x" at each bay's top-left
    # deletes the bay. Both invoke the registered UNDO operators. -----
    if mode == 'Bays':
        for starter in _iter_starter_roots(scene):
            bays_sorted = sorted(
                _iter_bay_cages(starter),
                key=lambda o: o.get('hb_bay_index', 0))
            if not bays_sorted:
                continue
            panels = sorted(
                [c for c in starter.children
                 if c.get('hb_part_role') == types_closets.PART_ROLE_PANEL],
                key=lambda o: o.get('hb_panel_index', 0))
            smw = split_preview._world_matrix(starter)
            pt_half = scene.hb_closets.panel_thickness / 2.0
            for i, panel in enumerate(panels):
                try:
                    length = GeoNodeCutpart(panel).get_input('Length')
                except Exception:
                    continue
                anchor = smw @ Vector((panel.location.x + pt_half, -0.003,
                                       panel.location.z + length * 0.5))
                pt2 = view3d_utils.location_3d_to_region_2d(
                    region, rv3d, anchor)
                if pt2 is None:
                    continue
                glyph = "+"
                gw, gh = blf.dimensions(0, glyph)
                w = gw + 2.5 * PAD_X * s
                h = gh + 2.5 * PAD_Y * s
                rect = (pt2.x - w / 2.0, pt2.y - h / 2.0, w, h)
                if (rect[0] + w < 0 or rect[0] > region.width
                        or rect[1] + h < 0 or rect[1] > region.height):
                    continue
                if i < len(bays_sorted):
                    labels.append((bays_sorted[i].name, 'PILL_INS_BEFORE',
                                   False, False, rect, glyph))
                else:
                    labels.append((bays_sorted[-1].name, 'PILL_INS_AFTER',
                                   False, False, rect, glyph))
            for bay in bays_sorted:
                anchor = _anchor_world(bay, 0.08, 0.94)
                if anchor is None:
                    continue
                pt2 = view3d_utils.location_3d_to_region_2d(
                    region, rv3d, anchor)
                if pt2 is None:
                    continue
                glyph = "×"
                gw, gh = blf.dimensions(0, glyph)
                w = gw + 2.5 * PAD_X * s
                h = gh + 2.5 * PAD_Y * s
                rect = (pt2.x - w / 2.0, pt2.y - h / 2.0, w, h)
                if (rect[0] + w < 0 or rect[0] > region.width
                        or rect[1] + h < 0 or rect[1] > region.height):
                    continue
                labels.append((bay.name, 'PILL_DELETE', False, False,
                               rect, glyph))

    # ----- Contents chip, top-right of every opening (Bays and
    # Openings modes). Click pops the insert menu at the cursor.
    # Labeled "Add..." (Andrew's pick) so it can't be confused with
    # the bare "+" add-bay pills on the panels. -----
    if mode in ('Bays', 'Openings'):
        for starter in _iter_starter_roots(scene):
            for bay in _iter_bay_cages(starter):
                for opening in _iter_opening_cages(bay):
                    anchor = _anchor_world(opening, 0.9, 0.94)
                    if anchor is None:
                        continue
                    pt = view3d_utils.location_3d_to_region_2d(
                        region, rv3d, anchor)
                    if pt is None:
                        continue
                    glyph = "Add..."
                    gw, gh = blf.dimensions(0, glyph)
                    w = gw + 2.5 * PAD_X * s
                    h = gh + 2.5 * PAD_Y * s
                    rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
                    if (rect[0] + w < 0 or rect[0] > region.width
                            or rect[1] + h < 0 or rect[1] > region.height):
                        continue
                    labels.append((opening.name, 'CHIP_CONTENTS', False,
                                   False, rect, glyph))

    # Per-family visibility filters (the pills below the HUD).
    return [entry for entry in labels if _kind_visible(scene, entry[1])]


# ---- Draw handler ------------------------------------------------------------

def _draw_label_rect(shader, rect, bg):
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    from gpu_extras.batch import batch_for_shader
    shader.uniform_float("color", bg)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", LABEL_BORDER)
    batch_for_shader(shader, 'LINE_LOOP', {"pos": verts}).draw(shader)


def _grab_active():
    try:
        from .operators import op_grab_closet
        return op_grab_closet.grab_is_active()
    except Exception:
        return False


def _draw_filter_pills(shader, context, area, font_sz, mode):
    """One pill per widget family applicable to the mode; active blue
    while that family is shown. The Grab pill mirrors the modal state."""
    for label, key, rect in _filter_pill_rects(context, area, mode):
        on = (_grab_active() if key == '__grab__'
              else _filter_on(context.scene, key))
        _draw_label_rect(shader, rect, EDIT_BG if on else LABEL_BG)
        blf.size(0, font_sz)
        blf.color(0, *(EDIT_TEXT_COLOR if on else TEXT_COLOR))
        tw, th = blf.dimensions(0, label)
        blf.position(0, rect[0] + (rect[2] - tw) / 2.0,
                     rect[1] + (rect[3] - th) / 2.0, 0)
        blf.draw(0, label)


def _draw():
    """Permanent POST_PIXEL callback; cheap no-op outside closet modes.
    Fully exception-guarded - a draw error must never spam the viewport."""
    if _shutdown:
        return
    try:
        context = bpy.context
        area = context.area
        region = context.region
        if area is None or area.type != 'VIEW_3D':
            return
        if region is None or region.type != 'WINDOW':
            return
        mode = _active_mode(context)
        if mode is None:
            return
        labels = compute_labels(context, region, context.region_data)

        s = 1.0
        try:
            s = bpy.context.preferences.system.ui_scale
        except AttributeError:
            pass
        font_sz = FONT_SIZE * s
        gpu.state.blend_set('ALPHA')
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        _draw_filter_pills(shader, context, area, font_sz, mode)
        for name, kind, editable, _locked, rect, text in labels:
            if kind.startswith(('TOGGLE_', 'CHIP_', 'PILL_')):
                # Toggle pill/glyph: ``_locked`` slot = active state.
                _draw_label_rect(shader, rect,
                                 EDIT_BG if _locked else LABEL_BG)
                blf.size(0, font_sz)
                blf.color(0, *(EDIT_TEXT_COLOR if _locked else TEXT_COLOR))
                tw, th = blf.dimensions(0, text)
                blf.position(0, rect[0] + (rect[2] - tw) / 2.0,
                             rect[1] + (rect[3] - th) / 2.0, 0)
                blf.draw(0, text)
                continue
            editing = (_edit is not None and _edit['name'] == name
                       and _edit['kind'] == kind)
            if editing:
                typed = _edit['typed']
                shown = (typed + "|") if typed else text
                blf.size(0, font_sz)
                tw, _th = blf.dimensions(0, shown)
                w = max(rect[2], tw + 2 * PAD_X * s)
                rect = (rect[0], rect[1], w, rect[3])
                _draw_label_rect(shader, rect, EDIT_BG)
                blf.color(0, *EDIT_TEXT_COLOR)
                blf.position(0, rect[0] + PAD_X * s, rect[1] + PAD_Y * s, 0)
                blf.draw(0, shown)
            else:
                _draw_label_rect(shader, rect,
                                 LABEL_BG if editable else LABEL_BG_DIM)
                blf.size(0, font_sz)
                blf.color(0, *(TEXT_COLOR if editable else TEXT_COLOR_DIM))
                blf.position(0, rect[0] + PAD_X * s, rect[1] + PAD_Y * s, 0)
                blf.draw(0, text)
        gpu.state.blend_set('NONE')
    except Exception:
        pass


# ---- Commit ------------------------------------------------------------------

def _commit(obj, kind, value):
    """Write the typed value through the same property paths the dialogs
    use, so update callbacks / redistribution / regenerators all fire."""
    if kind == 'STARTER_W':
        obj.hb_closet_starter.width = value
        return True
    if kind == 'STARTER_H':
        obj.hb_closet_starter.height = value
        return True
    if kind == 'STARTER_D':
        obj.hb_closet_starter.depth = value
        return True
    if kind == 'BAY_W':
        # Fires _update_bay_width: auto-locks + redistributes the rest.
        obj.hb_closet_bay.width = value
        return True
    if kind == 'OPEN_H':
        # Segment-aware: when a splitting shelf caps this opening,
        # editing the opening height MOVES that shelf. Only the topmost
        # segment (no shelf above) falls back to resizing the bay:
        # bay_height = value + seg_bottom + 2*shelf (+ kick when floor).
        bay = types_closets.find_bay_cage(obj)
        root = types_closets.find_starter_root(obj)
        if bay is None or root is None:
            return False
        seg_bottom = obj.get('hb_seg_bottom', 0.0)
        side = obj.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
        shelves = sorted(
            [c for c in bay.children
             if c.get('hb_part_role') == types_closets.PART_ROLE_FIXED_SHELF
             and c.get(types_closets.PROP_OPENING_SIDE, 'FRONT') == side
             and not c.get('hb_preview')],
            key=lambda o: o.get('hb_z_offset', 0.0))
        above = next((sh for sh in shelves
                      if sh.get('hb_z_offset', 0.0) >= seg_bottom - 1e-6),
                     None)
        if above is not None:
            above['hb_z_offset'] = float(seg_bottom + value)
            types_closets.recalculate_closet_starter(root)
            return True
        scene_props = bpy.context.scene.hb_closets
        bp = bay.hb_closet_bay
        kick = (root.hb_closet_starter.toe_kick_height
                if bp.floor_mounted else 0.0)
        bp.height = (value + seg_bottom
                     + 2.0 * scene_props.shelf_thickness + kick)
        return True
    if kind == 'PART_Z':
        root = types_closets.find_starter_root(obj)
        if root is None:
            return False
        parent = obj.parent
        if parent is not None and parent.get(types_closets.TAG_BAY_CAGE):
            # Splitting shelf: value IS the bay-interior offset.
            obj['hb_z_offset'] = float(max(0.0, value))
            types_closets.recalculate_closet_starter(root)
            return True
        # Opening-child part (rod): displayed value is opening-local Z;
        # convert to its anchor convention (rods ride the opening top).
        if parent is None:
            return False
        _w, interior_h = split_preview._cage_dims(parent)
        if obj.get('hb_anchor_top'):
            obj['hb_z_offset'] = float(max(0.0, interior_h - value))
        else:
            obj['hb_z_offset'] = float(max(0.0, value))
        types_closets.recalculate_closet_starter(root)
        return True
    if kind == 'DRAWER_H':
        # obj is the opening; the regenerator relays the stack out.
        root = types_closets.find_starter_root(obj)
        if root is None:
            return False
        obj[types_closets.PROP_DRAWER_FRONT_HEIGHT] = float(value)
        types_closets.recalculate_closet_starter(root)
        return True
    return False


def _reset_to_auto(obj, kind):
    """BAY_W only: clear the width lock so redistribution owns the value
    again. width_locked has no update callback, so recalc explicitly."""
    if kind == 'BAY_W' and obj.hb_closet_bay.width_locked:
        obj.hb_closet_bay.width_locked = False
        types_closets.recalculate_closet_starter(obj)
        return True
    return False


# ---- Edit modal ----------------------------------------------------------------

class hb_closets_OT_edit_dim_label(bpy.types.Operator):
    """Type a new value for the clicked dimension label. Enter commits,
    0-Enter / X resets a bay width to auto, Esc / click-away cancels."""
    bl_idname = "hb_closets.edit_dim_label"
    bl_label = "Edit Closet Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    kind: bpy.props.EnumProperty(items=KIND_ITEMS, options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        global _edit
        if bpy.data.objects.get(self.target_name) is None:
            return {'CANCELLED'}
        _edit = {'name': self.target_name, 'kind': self.kind, 'typed': "",
                 'owner': id(self)}
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('TEXT')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        global _edit
        _edit = None
        try:
            context.window.cursor_set('DEFAULT')
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        global _edit
        if _edit is None or _edit.get('owner') != id(self):
            return {'CANCELLED'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER'}:
            return {'PASS_THROUGH'}

        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'}:
            typed = _edit['typed']
            obj = bpy.data.objects.get(self.target_name)
            value = parse_distance(typed) if typed else None
            if not typed:
                self._finish(context)
                return {'FINISHED'}
            if obj is not None and value == 0.0:
                self._finish(context)
                _reset_to_auto(obj, self.kind)
                return {'FINISHED'}
            if obj is None or value is None or value <= 0.0:
                self.report({'WARNING'},
                            f"Could not read '{typed}' as a size")
                self._finish(context)
                return {'CANCELLED'}
            self._finish(context)
            _commit(obj, self.kind, value)
            return {'FINISHED'}

        if event.type in {'X', 'DEL'}:
            obj = bpy.data.objects.get(self.target_name)
            self._finish(context)
            if obj is not None:
                _reset_to_auto(obj, self.kind)
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'BACK_SPACE':
            _edit['typed'] = _edit['typed'][:-1]
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        ch = event.unicode
        if ch and ch in _INPUT_CHARS:
            _edit['typed'] += ch
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}


# ---- Click routing --------------------------------------------------------------

def _open_contents_popup(context, opening_name):
    """Activate the clicked opening (or its bay when the cage is hidden
    in Bays mode) and pop the insert menu at the cursor."""
    opening = bpy.data.objects.get(opening_name)
    if opening is None:
        return
    target = opening
    if opening.hide_viewport:
        target = types_closets.find_bay_cage(opening) or opening
    try:
        for o in context.selected_objects:
            o.select_set(False)
        target.select_set(True)
        context.view_layer.objects.active = target
    except Exception:
        pass

    def _draw_menu(menu, _ctx):
        from . import menus_closets
        layout = menu.layout
        # Menu items in a wm.popup_menu invoke with the POPUP's context
        # by default, which has no 3D region - the add-part modal then
        # cancels on init ("no viewport"). INVOKE_REGION_WIN re-targets
        # invocation at the viewport's window region (the same context a
        # right-click context menu provides).
        layout.operator_context = 'INVOKE_REGION_WIN'
        menus_closets._draw_add_part_entries(layout)

    context.window_manager.popup_menu(
        _draw_menu, title="Opening Contents", icon='PLUS')


class hb_closets_OT_dim_label_click(bpy.types.Operator):
    """Routes a viewport left-press to overlay labels; everything else
    passes through untouched."""
    bl_idname = "hb_closets.dim_label_click"
    bl_label = "Closet Dimension Label Click"
    bl_options = {'INTERNAL'}

    _pending_chip = None

    @classmethod
    def poll(cls, context):
        return (not _shutdown
                and context.area is not None
                and context.area.type == 'VIEW_3D'
                and context.region is not None
                and context.region.type == 'WINDOW'
                and _active_mode(context) is not None)

    def modal(self, context, event):
        # Waiting out the press that hit a contents chip: the menu opens
        # on RELEASE so it gets normal click-to-choose interaction.
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            name = self._pending_chip
            self._pending_chip = None
            if name is not None:
                _open_contents_popup(context, name)
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._pending_chip = None
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if _edit is not None:
            return {'PASS_THROUGH'}
        try:
            from ...operators import viewport_hud
            if viewport_hud.click_hits_widget(
                    context, context.area,
                    event.mouse_region_x, event.mouse_region_y):
                return {'PASS_THROUGH'}
        except Exception:
            pass
        mx, my = event.mouse_region_x, event.mouse_region_y
        mode = _active_mode(context)
        for _label, key, (tx, ty, tw, th) in _filter_pill_rects(
                context, context.area, mode):
            if tx <= mx <= tx + tw and ty <= my <= ty + th:
                if key == '__grab__':
                    from .operators import op_grab_closet
                    if op_grab_closet.grab_is_active():
                        op_grab_closet.request_grab_exit()
                    else:
                        bpy.ops.hb_closets.grab_mode('INVOKE_DEFAULT')
                else:
                    context.scene[key] = (0 if _filter_on(context.scene, key)
                                          else 1)
                context.area.tag_redraw()
                return {'FINISHED'}
        for name, kind, editable, _locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if kind in ('PILL_INS_BEFORE', 'PILL_INS_AFTER', 'PILL_DELETE'):
                bay = bpy.data.objects.get(name)
                if bay is None:
                    return {'PASS_THROUGH'}
                try:
                    for o in context.selected_objects:
                        o.select_set(False)
                    bay.select_set(True)
                    context.view_layer.objects.active = bay
                except Exception:
                    return {'PASS_THROUGH'}
                if kind == 'PILL_DELETE':
                    bpy.ops.hb_closets.delete_bay('INVOKE_DEFAULT')
                else:
                    direction = ('BEFORE' if kind == 'PILL_INS_BEFORE'
                                 else 'AFTER')
                    bpy.ops.hb_closets.insert_bay(
                        'INVOKE_DEFAULT', direction=direction)
                context.area.tag_redraw()
                return {'FINISHED'}
            if kind == 'CHIP_CONTENTS':
                # Consume the PRESS and open the menu on RELEASE via a
                # tiny modal - popping the menu on the press puts Blender
                # in hold-and-drag menu selection, which reads as broken.
                self._pending_chip = name
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            if kind == 'TOGGLE_FLOOR':
                bay = bpy.data.objects.get(name)
                if bay is not None:
                    bp = bay.hb_closet_bay
                    # Update callback runs the recalc.
                    bp.floor_mounted = not bp.floor_mounted
                    context.area.tag_redraw()
                return {'FINISHED'}
            if kind == 'TOGGLE_LOCK':
                bay = bpy.data.objects.get(name)
                if bay is not None:
                    bp = bay.hb_closet_bay
                    if bp.width_locked:
                        _reset_to_auto(bay, 'BAY_W')
                    else:
                        # Pin at the current width; a no-op until a
                        # neighboring edit tries to redistribute it.
                        bp.width_locked = True
                    context.area.tag_redraw()
                return {'FINISHED'}
            if not editable:
                return {'PASS_THROUGH'}
            bpy.ops.hb_closets.edit_dim_label(
                'INVOKE_DEFAULT', target_name=name, kind=kind)
            return {'FINISHED'}
        return {'PASS_THROUGH'}


class hb_closets_OT_dim_label_reset(bpy.types.Operator):
    """Right-click on a pinned (•) bay width resets it to auto."""
    bl_idname = "hb_closets.dim_label_reset"
    bl_label = "Reset Closet Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_closets_OT_dim_label_click.poll(context)

    def invoke(self, context, event):
        if _edit is not None:
            return {'PASS_THROUGH'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        for name, kind, editable, locked, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if not (editable and locked):
                return {'PASS_THROUGH'}
            obj = bpy.data.objects.get(name)
            if obj is not None and _reset_to_auto(obj, kind):
                context.area.tag_redraw()
                return {'FINISHED'}
            return {'PASS_THROUGH'}
        return {'PASS_THROUGH'}


# ---- Lifecycle --------------------------------------------------------------------

classes = (
    hb_closets_OT_edit_dim_label,
    hb_closets_OT_dim_label_click,
    hb_closets_OT_dim_label_reset,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        hb_closets_OT_dim_label_click.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        hb_closets_OT_dim_label_reset.bl_idname, 'RIGHTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    global _draw_handle, _shutdown
    _shutdown = False
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
    _register_keymaps()


def unregister():
    global _draw_handle, _shutdown, _edit
    _shutdown = True
    _edit = None
    _unregister_keymaps()
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
