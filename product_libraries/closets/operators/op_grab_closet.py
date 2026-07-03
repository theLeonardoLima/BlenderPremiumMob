"""Modal operator: grab and stretch closet geometry.

Ported from face_frame's op_modify_cabinet pattern (hover-highlighted
boundaries, LMB-drag with fractional snap, typed numeric override,
Esc/RMB cancel, Enter/release commit) trimmed to the closet boundary
set:

- Interior PANELS   drag X: the two adjacent bays trade width; release
                    auto-locks both (same as typing their labels).
- End panels        drag X: overall starter width. The LEFT end keeps
                    the right edge planted by shifting the starter.
- TOP edge          drag Z: overall starter height (hanging starters
                    stay top-anchored via the recalc rule).
- Fixed SHELVES     drag Z: the shelf slides between its neighbors;
                    the two openings trade height.

All writes go through the same props/idprops the overlay labels commit,
so locking, propagation, and the split reconciler behave identically.
The entry point is the "Grab" pill in the closet overlay's filter row -
no HUD (core) changes.
"""
import bpy
import gpu
import blf
import math
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

from .... import units
from ....units import inch
from ....hb_types import GeoNodeCage, GeoNodeCutpart
from .. import types_closets
from ...face_frame import split_preview

# ---- Tunables (mirror face_frame's grab) ----------------------------------
HIT_TOLERANCE_PX = 12.0
MIN_BAY_WIDTH = inch(2.0)
MIN_OPENING = inch(1.0)
MIN_STARTER_WIDTH = inch(6.0)
MIN_STARTER_HEIGHT = inch(6.0)
SNAP_STEPS = {'COARSE': inch(0.25), 'FINE': inch(0.125)}
GHOST_LINE = (0.85, 0.85, 0.85, 0.35)
HOVER_LINE = (1.00, 0.85, 0.20, 1.00)
ACTIVE_LINE = (1.00, 0.65, 0.10, 1.00)
DIM_TEXT = (1.00, 1.00, 1.00, 1.00)
_DIGIT_KEYS = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX',
               'SEVEN', 'EIGHT', 'NINE',
               'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4',
               'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9')

# Active-instance registry so the overlay's Grab pill can reflect and
# toggle the modal.
_active = None


def grab_is_active():
    return _active is not None


def request_grab_exit():
    if _active is not None:
        _active._exit_requested = True


# ---- Boundary collection ---------------------------------------------------

def _starter_dims(root):
    sp = root.hb_closet_starter
    return sp.width, sp.height, sp.depth


def _collect_boundaries(scene):
    """List of boundary dicts with world-space line segments. Recomputed
    per pick so it can't drift from the geometry."""
    out = []
    for root in scene.objects:
        if not root.get(types_closets.TAG_STARTER_CAGE):
            continue
        mw = split_preview._world_matrix(root)
        w, h, d = _starter_dims(root)
        bays = sorted([c for c in root.children
                       if c.get(types_closets.TAG_BAY_CAGE)],
                      key=lambda o: o.get('hb_bay_index', 0))
        panels = sorted([c for c in root.children
                         if c.get('hb_part_role')
                         == types_closets.PART_ROLE_PANEL],
                        key=lambda o: o.get('hb_panel_index', 0))
        n = len(bays)

        # Panels: verticals on the front face. Interior panels trade the
        # two adjacent bays; end panels stretch the starter width.
        for i, panel in enumerate(panels):
            try:
                length = GeoNodeCutpart(panel).get_input('Length')
                thick = GeoNodeCutpart(panel).get_input('Thickness')
            except Exception:
                continue
            x = panel.location.x + thick / 2.0
            z0 = panel.location.z
            p0 = mw @ Vector((x, -d, z0))
            p1 = mw @ Vector((x, -d, z0 + length))
            axis = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
            if i == 0:
                out.append(dict(kind='END_L', root=root.name,
                                p0=p0, p1=p1, axis=axis))
            elif i == len(panels) - 1:
                out.append(dict(kind='END_R', root=root.name,
                                p0=p0, p1=p1, axis=axis))
            elif i - 1 < n and i < n:
                out.append(dict(kind='PANEL', root=root.name,
                                left=bays[i - 1].name, right=bays[i].name,
                                p0=p0, p1=p1, axis=axis))

        # Top edge: horizontal across the starter front at height.
        p0 = mw @ Vector((0.0, -d, h))
        p1 = mw @ Vector((w, -d, h))
        z_axis = (mw.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        out.append(dict(kind='TOP', root=root.name,
                        p0=p0, p1=p1, axis=z_axis))

        # Splitting shelves: horizontals across their bay.
        for bay in bays:
            b_mw = split_preview._world_matrix(bay)
            b_w, _bh = split_preview._cage_dims(bay)
            try:
                b_d = GeoNodeCage(bay).get_input('Dim Y')
            except Exception:
                b_d = d
            for side in (('FRONT', 'BACK')
                         if root.get('CLASS_NAME') == 'DoubleIslandClosetStarter'
                         else ('FRONT',)):
                for sh in [c for c in bay.children
                           if c.get('hb_part_role')
                           == types_closets.PART_ROLE_FIXED_SHELF
                           and c.get(types_closets.PROP_OPENING_SIDE,
                                     'FRONT') == side
                           and not c.get('hb_preview')]:
                    z = sh.location.z
                    y_face = -b_d if side != 'BACK' else 0.0
                    p0 = b_mw @ Vector((0.0, y_face, z))
                    p1 = b_mw @ Vector((b_w, y_face, z))
                    out.append(dict(kind='SHELF', root=root.name,
                                    bay=bay.name, shelf=sh.name, side=side,
                                    p0=p0, p1=p1, axis=z_axis))
    return out


def _screen_seg(region, rv3d, b):
    a = view3d_utils.location_3d_to_region_2d(region, rv3d, b['p0'])
    c = view3d_utils.location_3d_to_region_2d(region, rv3d, b['p1'])
    return a, c


def _point_seg_dist(p, a, b):
    ab = b - a
    l2 = ab.length_squared
    if l2 <= 0.0:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
    return (p - (a + ab * t)).length


# ---- Draw ------------------------------------------------------------------

def _draw_line(shader, p1, p2, color, width):
    gpu.state.line_width_set(width)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES',
                     {"pos": (tuple(p1), tuple(p2))}).draw(shader)
    gpu.state.line_width_set(1.0)


def _draw_callback(op, context):
    try:
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return
        gpu.state.blend_set('ALPHA')
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        for b in (op._boundaries or []):
            a, c = _screen_seg(region, rv3d, b)
            if a is None or c is None:
                continue
            if op._drag_active and b is op._drag_boundary:
                _draw_line(shader, a, c, ACTIVE_LINE, 3.0)
            elif b is op._hover_boundary:
                _draw_line(shader, a, c, HOVER_LINE, 2.0)
            else:
                _draw_line(shader, a, c, GHOST_LINE, 1.0)
        # Value readout near the cursor during a drag.
        if op._drag_active and op._drag_text:
            x, y = op._last_mouse
            blf.size(0, 13)
            blf.color(0, *DIM_TEXT)
            blf.position(0, x + 16, y + 12, 0)
            blf.draw(0, op._drag_text)
        gpu.state.blend_set('NONE')
    except Exception:
        pass


# ---- Operator ---------------------------------------------------------------

class hb_closets_OT_grab_mode(bpy.types.Operator):
    """Grab mode: drag panels, shelves, or the starter's edges to
    stretch closets. Tab cycles snap, Shift holds it off, typed digits
    override, Enter/click-release commits, Esc/right-click cancels."""
    bl_idname = "hb_closets.grab_mode"
    bl_label = "Grab Closet"
    bl_options = {'UNDO'}

    _boundaries = None
    _hover_boundary = None
    _drag_boundary = None
    _drag_active = False
    _drag_text = ""
    _last_mouse = (0, 0)
    _snap_mode = 'COARSE'
    _typed = ''
    _exit_requested = False
    _snapshot = None
    _px_per_unit = 1.0
    _mouse0 = None

    @classmethod
    def poll(cls, context):
        return any(o.get(types_closets.TAG_STARTER_CAGE)
                   for o in context.scene.objects)

    # ---- lifecycle ----
    def invoke(self, context, event):
        global _active
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run from a 3D Viewport")
            return {'CANCELLED'}
        self._boundaries = _collect_boundaries(context.scene)
        if not self._boundaries:
            self.report({'INFO'}, "No closet boundaries found")
            return {'CANCELLED'}
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set(
            "Grab Closet  |  LMB-drag: panel / shelf / edge"
            "  |  Type: numeric  |  Tab: snap 1/4 - 1/8 - off"
            "  |  Shift: hold to disable snap"
            "  |  Enter / Esc: finish")
        context.window.cursor_modal_set('SCROLL_XY')
        _active = self
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _cleanup(self, context):
        global _active
        _active = None
        if getattr(self, '_draw_handle', None) is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(
                    self._draw_handle, 'WINDOW')
            except Exception:
                pass
            self._draw_handle = None
        try:
            context.area.header_text_set(None)
        except Exception:
            pass
        try:
            context.window.cursor_modal_restore()
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    # ---- picking / drag ----
    def _pick(self, context, event):
        region, rv3d = context.region, context.region_data
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        best = None
        for b in self._boundaries:
            a, c = _screen_seg(region, rv3d, b)
            if a is None or c is None:
                continue
            dist = _point_seg_dist(mouse, a, c)
            if dist <= HIT_TOLERANCE_PX and (best is None or dist < best[0]):
                best = (dist, b)
        return best[1] if best else None

    def _start_drag(self, context, event, b):
        region, rv3d = context.region, context.region_data
        self._drag_boundary = b
        self._drag_active = True
        self._typed = ''
        self._mouse0 = Vector((event.mouse_region_x, event.mouse_region_y))
        # Pixels per world unit along the drag axis at the grab point.
        mid = (b['p0'] + b['p1']) / 2.0
        a2 = view3d_utils.location_3d_to_region_2d(region, rv3d, mid)
        c2 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, mid + b['axis'])
        if a2 is None or c2 is None:
            self._drag_active = False
            return
        self._axis2d = (c2 - a2)
        self._px_per_unit = max(self._axis2d.length, 1e-6)
        self._axis2d.normalize()
        self._snapshot = self._take_snapshot(b)

    def _take_snapshot(self, b):
        snap = {'kind': b['kind']}
        root = bpy.data.objects.get(b['root'])
        sp = root.hb_closet_starter
        snap['width'] = sp.width
        snap['height'] = sp.height
        snap['loc'] = tuple(root.location)
        if b['kind'] == 'PANEL':
            left = bpy.data.objects.get(b['left'])
            right = bpy.data.objects.get(b['right'])
            snap['lw'] = left.hb_closet_bay.width
            snap['rw'] = right.hb_closet_bay.width
            snap['ll'] = left.hb_closet_bay.width_locked
            snap['rl'] = right.hb_closet_bay.width_locked
        elif b['kind'] == 'SHELF':
            sh = bpy.data.objects.get(b['shelf'])
            snap['z'] = sh.get('hb_z_offset', 0.0)
        return snap

    def _snap_value(self, value, event):
        if event.shift or self._snap_mode == 'OFF':
            return value
        step = SNAP_STEPS.get(self._snap_mode, inch(0.25))
        return round(value / step) * step

    def _apply_drag(self, context, event):
        b = self._drag_boundary
        snap = self._snapshot
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self._last_mouse = (mouse.x, mouse.y)
        delta = (mouse - self._mouse0).dot(self._axis2d) / self._px_per_unit
        root = bpy.data.objects.get(b['root'])
        if root is None:
            return
        us = context.scene.unit_settings

        if b['kind'] == 'PANEL':
            left = bpy.data.objects.get(b['left'])
            right = bpy.data.objects.get(b['right'])
            new_left = self._snap_value(snap['lw'] + delta, event)
            new_left = max(MIN_BAY_WIDTH,
                           min(new_left,
                               snap['lw'] + snap['rw'] - MIN_BAY_WIDTH))
            new_right = snap['lw'] + snap['rw'] - new_left
            lb, rb = left.hb_closet_bay, right.hb_closet_bay
            lb.width_locked = True
            rb.width_locked = True
            self._write_guarded(root, lambda: (
                setattr(lb, 'width', new_left),
                setattr(rb, 'width', new_right)))
            self._drag_text = "%s | %s" % (
                units.unit_to_string(us, new_left),
                units.unit_to_string(us, new_right))
        elif b['kind'] in ('END_L', 'END_R'):
            sp = root.hb_closet_starter
            sign = 1.0 if b['kind'] == 'END_R' else -1.0
            new_w = self._snap_value(snap['width'] + sign * delta, event)
            new_w = max(MIN_STARTER_WIDTH, new_w)
            if b['kind'] == 'END_L':
                # Keep the right edge planted: shift the origin by the
                # width change along the starter's local X.
                shift = (snap['width'] - new_w)
                axis_local = Vector((1.0, 0.0, 0.0))
                world_axis = (root.matrix_world.to_3x3() @ axis_local)
                root.location = (Vector(snap['loc'])
                                 + world_axis * shift)
            sp.width = new_w
            self._drag_text = "W " + units.unit_to_string(us, new_w)
        elif b['kind'] == 'TOP':
            sp = root.hb_closet_starter
            new_h = self._snap_value(snap['height'] + delta, event)
            new_h = max(MIN_STARTER_HEIGHT, new_h)
            sp.height = new_h
            self._drag_text = "H " + units.unit_to_string(us, new_h)
        elif b['kind'] == 'SHELF':
            sh = bpy.data.objects.get(b['shelf'])
            bay = bpy.data.objects.get(b['bay'])
            if sh is None or bay is None:
                return
            new_z = self._snap_value(snap['z'] + delta, event)
            new_z = self._clamp_shelf(bay, sh, new_z)
            sh['hb_z_offset'] = float(new_z)
            types_closets.recalculate_closet_starter(root)
            below, above = self._shelf_gaps(bay, sh)
            self._drag_text = "%s below | %s above" % (
                units.unit_to_string(us, below),
                units.unit_to_string(us, above))
        if context.area:
            context.area.tag_redraw()

    def _write_guarded(self, root, fn):
        """Write bay widths without the auto-lock callback churn, then
        run one recalc."""
        rid = id(root)
        types_closets._RECALCULATING.add(rid)
        types_closets._DISTRIBUTING_WIDTHS.add(rid)
        try:
            fn()
        finally:
            types_closets._RECALCULATING.discard(rid)
            types_closets._DISTRIBUTING_WIDTHS.discard(rid)
        types_closets.recalculate_closet_starter(root)

    def _clamp_shelf(self, bay, sh, new_z):
        scene_props = bpy.context.scene.hb_closets
        st = scene_props.shelf_thickness
        side = sh.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
        shelves = [c for c in bay.children
                   if c.get('hb_part_role')
                   == types_closets.PART_ROLE_FIXED_SHELF
                   and c.get(types_closets.PROP_OPENING_SIDE,
                             'FRONT') == side
                   and not c.get('hb_preview') and c is not sh]
        lo, hi = 0.0, None
        old = sh.get('hb_z_offset', 0.0)
        for other in shelves:
            oz = other.get('hb_z_offset', 0.0)
            if oz < old:
                lo = max(lo, oz + st + MIN_OPENING)
            else:
                hi = oz - st - MIN_OPENING if hi is None \
                    else min(hi, oz - st - MIN_OPENING)
        new_z = max(lo + 0.0, new_z)
        if hi is not None:
            new_z = min(new_z, hi)
        bp = bay.hb_closet_bay
        root = types_closets.find_starter_root(bay)
        kick = (root.hb_closet_starter.toe_kick_height
                if bp.floor_mounted else 0.0)
        interior_h = bp.height - 2.0 * st - kick
        new_z = min(new_z, interior_h - st - MIN_OPENING)
        return max(new_z, MIN_OPENING)

    def _shelf_gaps(self, bay, sh):
        """(clear below, clear above) for the drag readout."""
        scene_props = bpy.context.scene.hb_closets
        st = scene_props.shelf_thickness
        side = sh.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
        z = sh.get('hb_z_offset', 0.0)
        bp = bay.hb_closet_bay
        root = types_closets.find_starter_root(bay)
        kick = (root.hb_closet_starter.toe_kick_height
                if bp.floor_mounted else 0.0)
        interior_h = bp.height - 2.0 * st - kick
        below_bound, above_bound = 0.0, interior_h
        for other in bay.children:
            if (other.get('hb_part_role')
                    != types_closets.PART_ROLE_FIXED_SHELF
                    or other is sh or other.get('hb_preview')
                    or other.get(types_closets.PROP_OPENING_SIDE,
                                 'FRONT') != side):
                continue
            oz = other.get('hb_z_offset', 0.0)
            if oz < z:
                below_bound = max(below_bound, oz + st)
            else:
                above_bound = min(above_bound, oz)
        return z - below_bound, above_bound - (z + st)

    def _end_drag(self, context, commit):
        if not self._drag_active:
            return
        b = self._drag_boundary
        if not commit:
            snap = self._snapshot
            root = bpy.data.objects.get(b['root'])
            if root is not None:
                sp = root.hb_closet_starter
                if b['kind'] == 'PANEL':
                    left = bpy.data.objects.get(b['left'])
                    right = bpy.data.objects.get(b['right'])
                    lb, rb = left.hb_closet_bay, right.hb_closet_bay
                    self._write_guarded(root, lambda: (
                        setattr(lb, 'width', snap['lw']),
                        setattr(rb, 'width', snap['rw']),
                        setattr(lb, 'width_locked', snap['ll']),
                        setattr(rb, 'width_locked', snap['rl'])))
                elif b['kind'] in ('END_L', 'END_R'):
                    root.location = snap['loc']
                    sp.width = snap['width']
                elif b['kind'] == 'TOP':
                    sp.height = snap['height']
                elif b['kind'] == 'SHELF':
                    sh = bpy.data.objects.get(b['shelf'])
                    if sh is not None:
                        sh['hb_z_offset'] = float(snap['z'])
                        types_closets.recalculate_closet_starter(root)
        self._drag_active = False
        self._drag_boundary = None
        self._drag_text = ""
        self._typed = ''
        # Boundaries move with the geometry; recollect for clean lines.
        self._boundaries = _collect_boundaries(bpy.context.scene)

    def _apply_typed(self, context):
        """Typed value replaces the drag's primary parameter."""
        from ..gpu_overlay_closets import parse_distance
        value = parse_distance(self._typed) if self._typed else None
        self._typed = ''
        if value is None or value <= 0.0 or not self._drag_active:
            return
        b = self._drag_boundary
        snap = self._snapshot
        root = bpy.data.objects.get(b['root'])
        us = context.scene.unit_settings
        if b['kind'] == 'PANEL':
            left = bpy.data.objects.get(b['left'])
            right = bpy.data.objects.get(b['right'])
            new_left = max(MIN_BAY_WIDTH,
                           min(value,
                               snap['lw'] + snap['rw'] - MIN_BAY_WIDTH))
            new_right = snap['lw'] + snap['rw'] - new_left
            lb, rb = left.hb_closet_bay, right.hb_closet_bay
            lb.width_locked = True
            rb.width_locked = True
            self._write_guarded(root, lambda: (
                setattr(lb, 'width', new_left),
                setattr(rb, 'width', new_right)))
        elif b['kind'] in ('END_L', 'END_R'):
            sp = root.hb_closet_starter
            if b['kind'] == 'END_L':
                shift = snap['width'] - value
                world_axis = root.matrix_world.to_3x3() @ Vector((1, 0, 0))
                root.location = Vector(snap['loc']) + world_axis * shift
            sp.width = max(MIN_STARTER_WIDTH, value)
        elif b['kind'] == 'TOP':
            root.hb_closet_starter.height = max(MIN_STARTER_HEIGHT, value)
        elif b['kind'] == 'SHELF':
            sh = bpy.data.objects.get(b['shelf'])
            bay = bpy.data.objects.get(b['bay'])
            if sh is not None and bay is not None:
                sh['hb_z_offset'] = float(self._clamp_shelf(bay, sh, value))
                types_closets.recalculate_closet_starter(root)
        self._end_drag(context, commit=True)

    # ---- modal ----
    def modal(self, context, event):
        if self._exit_requested:
            self._exit_requested = False
            if self._drag_active:
                self._end_drag(context, commit=True)
            self._cleanup(context)
            return {'FINISHED'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            self._last_mouse = (event.mouse_region_x, event.mouse_region_y)
            if self._drag_active:
                self._apply_drag(context, event)
            else:
                self._hover_boundary = self._pick(context, event)
            if context.area:
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # The modal owns all clicks, so route overlay pill hits here:
            # the Grab pill exits, filter pills keep working mid-session.
            try:
                from .. import gpu_overlay_closets as ov
                mode = ov._active_mode(context)
                if mode is not None:
                    mx = event.mouse_region_x
                    my = event.mouse_region_y
                    for _lbl, key, (tx, ty, tw, th) in ov._filter_pill_rects(
                            context, context.area, mode):
                        if tx <= mx <= tx + tw and ty <= my <= ty + th:
                            if key == '__grab__':
                                if self._drag_active:
                                    self._end_drag(context, commit=True)
                                self._cleanup(context)
                                return {'FINISHED'}
                            context.scene[key] = (
                                0 if ov._filter_on(context.scene, key) else 1)
                            context.area.tag_redraw()
                            return {'RUNNING_MODAL'}
            except Exception:
                pass
            pick = self._pick(context, event)
            if pick is not None:
                self._start_drag(context, event, pick)
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self._drag_active:
                self._end_drag(context, commit=True)
                if context.area:
                    context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'TAB' and event.value == 'PRESS':
            self._snap_mode = {'OFF': 'COARSE', 'COARSE': 'FINE',
                               'FINE': 'OFF'}[self._snap_mode]
            self.report({'INFO'}, f"Snap: {self._snap_mode}")
            return {'RUNNING_MODAL'}

        if self._drag_active and event.value == 'PRESS':
            if event.type in _DIGIT_KEYS:
                self._typed += event.type[-1]
                self._drag_text = self._typed + '"?'
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type == 'PERIOD' or (event.type == 'SLASH'):
                self._typed += '.' if event.type == 'PERIOD' else '/'
                return {'RUNNING_MODAL'}
            if event.type == 'BACK_SPACE':
                self._typed = self._typed[:-1]
                return {'RUNNING_MODAL'}
            if event.type in {'RET', 'NUMPAD_ENTER'} and self._typed:
                self._apply_typed(context)
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if self._drag_active:
                self._end_drag(context, commit=False)
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            self._cleanup(context)
            return {'CANCELLED'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if self._drag_active:
                self._end_drag(context, commit=True)
            self._cleanup(context)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


classes = (hb_closets_OT_grab_mode,)

register, unregister = bpy.utils.register_classes_factory(classes)
