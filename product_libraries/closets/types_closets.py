"""Closet starter construction classes.

Phase 1 deliverable: Base / Tall / Hanging / Island starters that build
panels, top and bottom fixed shelves, cleats, toe kicks, openings, and
(Base/Island) countertops. No drivers - all dimension propagation runs
through recalculate(), which reads the hb_closet_starter / hb_closet_bay
PropertyGroups, asks solver_closets for the layout, and writes positions
and GeoNode inputs to every part.

Structure:
    starter root cage (TAG_STARTER_CAGE)
    +-- panel parts 0..N          (shared verticals; panel i left of bay i)
    +-- countertop / applied-back parts (starter-level, per class flags)
    +-- bay cages (TAG_BAY_CAGE, hb_bay_index)
        +-- bottom shelf, top shelf, toe kick, cleat  (bay-local coords)
        +-- opening cage (TAG_OPENING_CAGE)           (interior volume)

Conventions match face_frame: origin back-left at floor, +X right,
-Y forward, +Z up. Vertical panels rotate y=-90 so Length runs up +Z,
Width runs -Y (Mirror Y), Thickness extrudes +X (Mirror Z).
"""
import bpy
import math

from ...hb_types import (GeoNodeCage, GeoNodeCutpart, GeoNodeObject,
                         GeoNodeDrawerBox)
from ...units import inch
from ..frameless.types_frameless import CabinetPart
from . import solver_closets as solver
from . import const_closets as const

from types import SimpleNamespace


# ---------------------------------------------------------------------------
# Identity tags / part roles
# ---------------------------------------------------------------------------
TAG_STARTER_CAGE = 'IS_CLOSET_STARTER_CAGE'
TAG_BAY_CAGE = 'IS_CLOSET_BAY_CAGE'
TAG_OPENING_CAGE = 'IS_CLOSET_OPENING_CAGE'

PART_ROLE_PANEL = 'CLOSET_PANEL'
PART_ROLE_BOTTOM_SHELF = 'CLOSET_BOTTOM_SHELF'
PART_ROLE_TOP_SHELF = 'CLOSET_TOP_SHELF'
PART_ROLE_TOE_KICK = 'CLOSET_TOE_KICK'
PART_ROLE_CLEAT = 'CLOSET_CLEAT'
PART_ROLE_COUNTERTOP = 'CLOSET_COUNTERTOP'
PART_ROLE_APPLIED_BACK = 'CLOSET_APPLIED_BACK'

# Interior parts added by the user (Phase 3). These live under an opening
# cage and carry idprops instead of a PropertyGroup so the whole layer
# stays hot-reloadable:
#   'hb_z_offset'   distance (m) from the opening bottom (or top when
#                   'hb_anchor_top') to the part's underside / rod center
#   'hb_anchor_top' 1 = z_offset measures down from the opening top, so
#                   the part rides the top when the bay height changes
#                   (rods hang; shelves usually anchor to the bottom)
PART_ROLE_FIXED_SHELF = 'CLOSET_FIXED_SHELF'
PART_ROLE_ADJ_SHELF = 'CLOSET_ADJ_SHELF'
PART_ROLE_ROD = 'CLOSET_ROD'
# Inserts (Phase 4). Fronts follow the legacy half-overlay convention.
PART_ROLE_DOOR = 'CLOSET_DOOR_FRONT'
PART_ROLE_DRAWER_FRONT = 'CLOSET_DRAWER_FRONT'
PART_ROLE_DRAWER_BOX = 'CLOSET_DRAWER_BOX'
PART_ROLE_CUBBY_DIVISION = 'CLOSET_CUBBY_DIVISION'
PART_ROLE_CUBBY_SHELF = 'CLOSET_CUBBY_SHELF'
# Double-sided island structure.
PART_ROLE_CENTER_BACK = 'CLOSET_CENTER_BACK'
# Opening idprops: insert configuration, reconciled by regenerators on
# every recalc (create/remove children to match, then lay out).
PROP_ADJ_SHELF_QTY = 'hb_adj_shelf_qty'
PROP_DRAWER_QTY = 'hb_drawer_qty'
PROP_DRAWER_FRONT_HEIGHT = 'hb_drawer_front_height'
PROP_DOOR_SWING = 'hb_door_swing'        # ''|'LEFT'|'RIGHT'|'DOUBLE'
PROP_IS_HAMPER = 'hb_is_hamper'
PROP_CUBBY_COLS = 'hb_cubby_cols'
PROP_CUBBY_ROWS = 'hb_cubby_rows'
# Opening idprop on double islands: which face the opening serves.
PROP_OPENING_SIDE = 'hb_opening_side'    # 'FRONT' (default) | 'BACK'

# Reentrance guards, same pattern as face_frame. Prop writes inside
# recalculate() (bay width redistribution) fire update callbacks that
# would otherwise recurse; the callbacks consult these sets and bail.
_RECALCULATING = set()
_DISTRIBUTING_WIDTHS = set()


def _set_part_hidden(obj, hidden):
    obj.hide_viewport = hidden
    obj.hide_render = hidden


# ---------------------------------------------------------------------------
# Cage classes
# ---------------------------------------------------------------------------
class ClosetBay(GeoNodeCage):
    """Bay cage: one section between two vertical panels. Carries the
    per-bay overrides (width/height/depth/floor_mounted) on
    obj.hb_closet_bay; its parts live in bay-local coordinates."""

    def create(self, name="Bay"):
        super().create(name)
        self.obj[TAG_BAY_CAGE] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_bay_commands'
        self.set_input('Mirror Y', True)


class ClosetOpening(GeoNodeCage):
    """Opening cage: the interior volume of a bay between the fixed top
    and bottom shelves. User-added interior parts (shelves, rods) parent
    here and are laid out in opening-local coordinates."""

    def create(self, name="Opening"):
        super().create(name)
        self.obj[TAG_OPENING_CAGE] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_opening_commands'
        self.set_input('Mirror Y', True)


class ClosetRod(GeoNodeObject):
    """Hang rod. Uses the legacy rod node group (round/oval profile with
    end cups); Dim X is the rod length along local +X."""

    def create(self, name="Closet Rod"):
        super().create('GeoNodeClosetRod', name)
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
        self.set_input('Radius', const.ROD_RADIUS)
        self.set_input('Is Oval', False)


# ---------------------------------------------------------------------------
# Interior part builders (module-level: operators call these directly)
# ---------------------------------------------------------------------------
def add_fixed_shelf(opening_obj, z_offset, anchor_top=False,
                    role=PART_ROLE_FIXED_SHELF):
    """Create a shelf part under an opening. Position/size are written by
    the next recalculate(); only static orientation is set here."""
    shelf = CabinetPart()
    shelf.create('Fixed Shelf' if role == PART_ROLE_FIXED_SHELF
                 else 'Adjustable Shelf')
    shelf.obj.parent = opening_obj
    shelf.obj['hb_part_role'] = role
    shelf.obj['hb_z_offset'] = float(z_offset)
    shelf.obj['hb_anchor_top'] = 1 if anchor_top else 0
    shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
    shelf.set_input('Mirror Y', True)
    return shelf.obj


def add_rod(opening_obj, z_offset):
    """Create a hang rod under an opening, anchored to the opening top so
    it keeps its hang height when the bay grows."""
    rod = ClosetRod()
    rod.create()
    rod.obj.parent = opening_obj
    rod.obj['hb_part_role'] = PART_ROLE_ROD
    rod.obj['hb_z_offset'] = float(z_offset)
    rod.obj['hb_anchor_top'] = 1
    return rod.obj


# ---------------------------------------------------------------------------
# Starter base class
# ---------------------------------------------------------------------------
class ClosetStarter(GeoNodeCage):
    """Base class for all closet starters. No drivers - see module doc."""

    default_closet_type = 'BASE'
    has_toe_kick = True
    floor_mounted = True
    has_countertop = False
    has_applied_back = False
    # Double-sided (island) construction: center back per bay, front and
    # back opening cages, rear toe kick, countertop overhang all around.
    is_double = False
    ctop_overhang_all = False
    # None = use the scene default panel depth at create time.
    default_depth = None

    # -----------------------------------------------------------------
    # Construction
    # -----------------------------------------------------------------
    def default_height(self, scene_props):
        return {
            'BASE': scene_props.base_panel_height,
            'TALL': scene_props.tall_panel_height,
            'HANGING': scene_props.hanging_panel_height,
            'ISLAND': scene_props.base_panel_height,
        }[self.default_closet_type]

    def create_starter(self, name, bay_qty=const.DEFAULT_BAY_QTY):
        """Create the root cage, seed props, and build all parts. The
        body runs under the reentrance guards so prop seeding doesn't
        trigger nested recalcs; the trailing recalculate() lays out
        everything once."""
        super().create(name)
        self.obj[TAG_STARTER_CAGE] = True
        self.obj['CLASS_NAME'] = self.__class__.__name__
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_starter_commands'
        self.obj.display_type = 'WIRE'
        self.set_input('Mirror Y', True)

        scene_props = bpy.context.scene.hb_closets
        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            sp = self.obj.hb_closet_starter
            sp.closet_type = self.default_closet_type
            sp.toe_kick_height = (scene_props.toe_kick_height
                                  if self.has_toe_kick else 0.0)
            sp.toe_kick_setback = scene_props.toe_kick_setback
            sp.include_countertop = self.has_countertop
            sp.width = scene_props.default_closet_width
            sp.height = self.default_height(scene_props)
            sp.depth = (self.default_depth
                        if self.default_depth is not None
                        else scene_props.default_panel_depth)
            self._build_parts(bay_qty, scene_props)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()

    def _build_parts(self, bay_qty, scene_props):
        """Create panels, starter-level parts, and bay subtrees. All
        positions/dimensions are written later by recalculate()."""
        sp = self.obj.hb_closet_starter
        bay_qty = max(1, int(bay_qty))

        # ----- Vertical panels 0..N (panel i = left panel of bay i) -----
        for i in range(bay_qty + 1):
            panel = CabinetPart()
            panel.create(f'Partition {i + 1}')
            panel.obj.parent = self.obj
            panel.obj['hb_part_role'] = PART_ROLE_PANEL
            panel.obj['hb_panel_index'] = i
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.set_input('Mirror Y', True)
            panel.set_input('Mirror Z', True)

        # ----- Starter-level optional parts -----
        if self.has_countertop:
            ctop = CabinetPart()
            ctop.create('Countertop')
            ctop.obj.parent = self.obj
            ctop.obj['hb_part_role'] = PART_ROLE_COUNTERTOP
            ctop.set_input('Mirror Y', True)

        # ----- Bays -----
        equal_width = (sp.width - (bay_qty + 1) * scene_props.panel_thickness) / bay_qty
        for i in range(bay_qty):
            bay = ClosetBay()
            bay.create(f'Bay {i + 1}')
            bay.obj.parent = self.obj
            bay.obj['hb_bay_index'] = i
            bp = bay.obj.hb_closet_bay
            bp.bay_index = i
            bp.width = equal_width
            bp.width_locked = False
            bp.height = sp.height
            bp.depth = sp.depth
            bp.floor_mounted = self.floor_mounted
            self._build_bay_parts(bay.obj)

    def _build_bay_parts(self, bay_obj):
        """One bay's fixed parts + opening cage, in bay-local coords.
        Static rotations/mirrors are set here; recalculate() owns the
        positions and sizes. Toe kick / cleat orientation reproduces the
        legacy build: rot_x -90 stands the kick board up behind the
        setback line; rot_x +90 stands the cleat against the back."""
        bottom = CabinetPart()
        bottom.create('Bottom Shelf')
        bottom.obj.parent = bay_obj
        bottom.obj['hb_part_role'] = PART_ROLE_BOTTOM_SHELF
        bottom.set_input('Mirror Y', True)

        top = CabinetPart()
        top.create('Top Shelf')
        top.obj.parent = bay_obj
        top.obj['hb_part_role'] = PART_ROLE_TOP_SHELF
        top.set_input('Mirror Y', True)

        kick = CabinetPart()
        kick.create('Toe Kick')
        kick.obj.parent = bay_obj
        kick.obj['hb_part_role'] = PART_ROLE_TOE_KICK
        kick.obj.rotation_euler.x = math.radians(-90)
        kick.set_input('Mirror Y', True)

        cleat = CabinetPart()
        cleat.create('Cleat')
        cleat.obj.parent = bay_obj
        cleat.obj['hb_part_role'] = PART_ROLE_CLEAT
        cleat.obj.rotation_euler.x = math.radians(90)
        # A double island has no wall side; the center back stiffens the
        # unit and the cleat would float mid-carcass - skip it.
        if self.is_double:
            _set_part_hidden(cleat.obj, True)
            cleat.obj['hb_always_hidden'] = 1

        if self.has_applied_back:
            back = CabinetPart()
            back.create('Applied Back')
            back.obj.parent = bay_obj
            back.obj['hb_part_role'] = PART_ROLE_APPLIED_BACK
            back.obj.rotation_euler.x = math.radians(90)
            back.set_input('Mirror Z', True)

        if self.is_double:
            rear_kick = CabinetPart()
            rear_kick.create('Rear Toe Kick')
            rear_kick.obj.parent = bay_obj
            rear_kick.obj['hb_part_role'] = PART_ROLE_TOE_KICK
            rear_kick.obj['hb_rear'] = 1
            rear_kick.obj.rotation_euler.x = math.radians(-90)
            rear_kick.set_input('Mirror Y', True)
            rear_kick.set_input('Mirror Z', True)

            center_back = CabinetPart()
            center_back.create('Center Back')
            center_back.obj.parent = bay_obj
            center_back.obj['hb_part_role'] = PART_ROLE_CENTER_BACK
            center_back.obj.rotation_euler.x = math.radians(90)
            center_back.set_input('Mirror Z', True)

            back_opening = ClosetOpening()
            back_opening.create('Opening 1 Back')
            back_opening.obj.parent = bay_obj
            back_opening.obj['hb_opening_index'] = 1
            back_opening.obj[PROP_OPENING_SIDE] = 'BACK'

        opening = ClosetOpening()
        opening.create('Opening 1')
        opening.obj.parent = bay_obj
        opening.obj['hb_opening_index'] = 0

    # -----------------------------------------------------------------
    # Child lookups
    # -----------------------------------------------------------------
    def _sorted_bays(self):
        bays = [c for c in self.obj.children if c.get(TAG_BAY_CAGE)]
        bays.sort(key=lambda o: o.get('hb_bay_index', 0))
        return bays

    def _sorted_panels(self):
        panels = [c for c in self.obj.children
                  if c.get('hb_part_role') == PART_ROLE_PANEL]
        panels.sort(key=lambda o: o.get('hb_panel_index', 0))
        return panels

    def _root_part(self, role):
        for c in self.obj.children:
            if c.get('hb_part_role') == role:
                return c
        return None

    def _bay_part(self, bay_obj, role):
        for c in bay_obj.children:
            if c.get('hb_part_role') == role:
                return c
        return None

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    def _spec_from_props(self, scene_props):
        sp = self.obj.hb_closet_starter
        bays = []
        for bay_obj in self._sorted_bays():
            bp = bay_obj.hb_closet_bay
            bays.append({
                'width': bp.width,
                'locked': bp.width_locked,
                'height': bp.height,
                'depth': bp.depth,
                'floor': bp.floor_mounted,
                'remove_bottom': bp.remove_bottom,
                'remove_cleat': bp.remove_cleat,
            })
        return SimpleNamespace(
            width=sp.width,
            height=sp.height,
            pt=scene_props.panel_thickness,
            st=scene_props.shelf_thickness,
            kick_height=sp.toe_kick_height,
            kick_setback=sp.toe_kick_setback,
            bays=bays,
        )

    def recalculate(self):
        """Read props -> solve layout -> write every part. Safe to call
        repeatedly; guarded against reentry from prop update callbacks."""
        cabinet_id = id(self.obj)
        if cabinet_id in _RECALCULATING:
            return
        _RECALCULATING.add(cabinet_id)
        try:
            scene_props = bpy.context.scene.hb_closets
            sp = self.obj.hb_closet_starter

            # Starter height/depth edits propagate to every bay still at
            # the previous starter value; individually overridden bays
            # keep their override. The last-applied values ride idprops
            # (also used below for the hanging top-anchor). Bay writes
            # here can't recurse - the update callbacks bail while this
            # starter is in _RECALCULATING.
            last_h = self.obj.get('hb_last_height')
            last_d = self.obj.get('hb_last_depth')
            for bay_obj in self._sorted_bays():
                bp = bay_obj.hb_closet_bay
                if (last_h is not None
                        and abs(bp.height - last_h) < 1e-6
                        and abs(sp.height - last_h) > 1e-9):
                    bp.height = sp.height
                if (last_d is not None
                        and abs(bp.depth - last_d) < 1e-6
                        and abs(sp.depth - last_d) > 1e-9):
                    bp.depth = sp.depth
            self.obj['hb_last_depth'] = sp.depth

            spec = self._spec_from_props(scene_props)
            if not spec.bays:
                return
            layout = solver.compute_layout(spec)

            # Write redistributed widths back without auto-locking them.
            _DISTRIBUTING_WIDTHS.add(cabinet_id)
            try:
                for bay_obj, w in zip(self._sorted_bays(), layout['widths']):
                    bay_obj.hb_closet_bay.width = w
            finally:
                _DISTRIBUTING_WIDTHS.discard(cabinet_id)

            self._layout_panels(layout, scene_props)
            self._layout_bays(layout, scene_props, sp)
            self._layout_starter_parts(layout, scene_props, sp)

            # Hanging starters anchor at their TOP (the wall mount): a
            # height edit grows the unit downward. The last-applied
            # height rides an idprop so only true height edits shift the
            # origin - manual moves (G) are untouched.
            if sp.closet_type == 'HANGING':
                last_h = self.obj.get('hb_last_height')
                if last_h is not None and abs(last_h - sp.height) > 1e-9:
                    self.obj.location.z += (last_h - sp.height)
            self.obj['hb_last_height'] = sp.height

            self.set_input('Dim X', sp.width)
            self.set_input('Dim Y', sp.depth)
            self.set_input('Dim Z', sp.height)
        finally:
            _RECALCULATING.discard(cabinet_id)

    def _layout_panels(self, layout, scene_props):
        pt = scene_props.panel_thickness
        for child, panel in zip(self._sorted_panels(), layout['panels']):
            child.location = (panel['x'], 0.0, panel['z'])
            part = GeoNodeCutpart(child)
            part.set_input('Length', panel['length'])
            part.set_input('Width', panel['depth'])
            part.set_input('Thickness', pt)

    def _layout_bays(self, layout, scene_props, sp):
        st = scene_props.shelf_thickness
        for bay_obj, bay in zip(self._sorted_bays(), layout['bays']):
            cage = GeoNodeCage(bay_obj)
            bay_obj.location = (bay['x'], 0.0, bay['z0'])
            cage.set_input('Dim X', bay['width'])
            cage.set_input('Dim Y', bay['depth'])
            cage.set_input('Dim Z', bay['height'])
            bp = bay_obj.hb_closet_bay

            bottom = self._bay_part(bay_obj, PART_ROLE_BOTTOM_SHELF)
            if bottom is not None:
                bottom.location = (0.0, 0.0, bay['bottom_z'])
                part = GeoNodeCutpart(bottom)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['depth'])
                part.set_input('Thickness', st)
                _set_part_hidden(bottom, bp.remove_bottom)

            top = self._bay_part(bay_obj, PART_ROLE_TOP_SHELF)
            if top is not None:
                top.location = (0.0, 0.0, bay['top_z'])
                part = GeoNodeCutpart(top)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['depth'])
                part.set_input('Thickness', st)
                _set_part_hidden(top, False)

            for kick in bay_obj.children:
                if kick.get('hb_part_role') != PART_ROLE_TOE_KICK:
                    continue
                if kick.get('hb_rear'):
                    kick.location = (0.0, -sp.toe_kick_setback, 0.0)
                else:
                    kick.location = (0.0, -bay['depth'] + sp.toe_kick_setback,
                                     0.0)
                part = GeoNodeCutpart(kick)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['kick'])
                part.set_input('Thickness', st)
                _set_part_hidden(kick, (not bay['floor'])
                                 or bp.remove_bottom
                                 or bay['kick'] <= 0.0)

            cleat = self._bay_part(bay_obj, PART_ROLE_CLEAT)
            if cleat is not None:
                cleat.location = (0.0, 0.0, bay['cleat_z'])
                part = GeoNodeCutpart(cleat)
                part.set_input('Length', bay['width'])
                part.set_input('Width', const.CLEAT_WIDTH)
                part.set_input('Thickness', st)
                _set_part_hidden(cleat, bp.remove_cleat
                                 or bool(cleat.get('hb_always_hidden')))

            back = self._bay_part(bay_obj, PART_ROLE_APPLIED_BACK)
            if back is not None:
                back.location = (0.0, 0.0, bay['interior_z'])
                part = GeoNodeCutpart(back)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['interior_h'])
                part.set_input('Thickness', const.APPLIED_BACK_THICKNESS)
                _set_part_hidden(back, False)

            # Center back (double islands): st thick, centered in depth,
            # spanning the interior. Horizontal grain for now; the
            # machining layer decides grain later.
            center_back = self._bay_part(bay_obj, PART_ROLE_CENTER_BACK)
            if center_back is not None:
                center_back.location = (
                    0.0, -(bay['depth'] / 2.0 + st / 2.0), bay['interior_z'])
                part = GeoNodeCutpart(center_back)
                part.set_input('Length', bay['width'])
                part.set_input('Width', bay['interior_h'])
                part.set_input('Thickness', st)

            # Openings. Fixed shelves are SPLITTERS: committed shelves
            # live at bay level and divide the interior into segments,
            # one opening cage per segment (per side on double islands).
            # The reconciler adopts freshly committed shelves, matches
            # the opening count to the segments, and preserves contents
            # when a shelf removal merges segments.
            self._reconcile_bay_openings(bay_obj)
            half_depth = (bay['depth'] - st) / 2.0
            sides = ('FRONT', 'BACK') if self.is_double else ('FRONT',)
            for side in sides:
                if self.is_double:
                    o_depth = half_depth
                    base_y = (0.0 if side == 'BACK'
                              else -(bay['depth'] / 2.0 + st / 2.0))
                else:
                    o_depth = bay['depth']
                    base_y = 0.0

                # Splitting shelves: clamp into the interior, lay out at
                # bay level, and collect the segment boundaries.
                boundaries = []
                for sh in self._bay_split_shelves(bay_obj, side):
                    z_off = max(0.0, min(sh.get('hb_z_offset', 0.0),
                                         bay['interior_h'] - st))
                    sh['hb_z_offset'] = float(z_off)
                    sh.location = (0.0, base_y, bay['interior_z'] + z_off)
                    part = GeoNodeCutpart(sh)
                    part.set_input('Length', bay['width'])
                    part.set_input('Width', o_depth)
                    part.set_input('Thickness', st)
                    _set_part_hidden(sh, False)
                    boundaries.append(z_off)

                openings = sorted(
                    [c for c in bay_obj.children
                     if c.get(TAG_OPENING_CAGE)
                     and c.get(PROP_OPENING_SIDE, 'FRONT') == side],
                    key=lambda o: o.get('hb_opening_index', 0))
                bottoms = [0.0] + [b + st for b in boundaries]
                tops = boundaries + [bay['interior_h']]
                for op_obj, b0, t0 in zip(openings, bottoms, tops):
                    seg_h = max(t0 - b0, 0.01)
                    op_obj['hb_seg_bottom'] = float(b0)
                    op_obj.location = (0.0, base_y,
                                       bay['interior_z'] + b0)
                    op_cage = GeoNodeCage(op_obj)
                    op_cage.set_input('Dim X', bay['width'])
                    op_cage.set_input('Dim Y', o_depth)
                    op_cage.set_input('Dim Z', seg_h)
                    self._layout_opening_parts(op_obj, bay['width'],
                                               o_depth, seg_h, scene_props)

    def _layout_opening_parts(self, opening, width, depth, interior_h,
                              scene_props):
        """Reconcile + lay out user-added parts and inserts in
        opening-local coords.

        Fixed shelves / rods keep their stored offset (from the bottom,
        or from the top when anchored there) clamped into the interior.
        Adjustable shelves / doors / drawers / cubbies are reconciled to
        the opening's config idprops (regenerators create/remove children
        to match, so config edits and old files always converge).

        Fronts use the legacy half-overlay convention: each edge overlays
        its shared panel/shelf by (thickness - gap)/2. On a double
        island's BACK opening the fronts flip to the y=0 face (Mirror Z
        flips the extrude direction, set at part creation).
        """
        st = scene_props.shelf_thickness
        pt = scene_props.panel_thickness
        side = opening.get(PROP_OPENING_SIDE, 'FRONT')

        self._reconcile_adj_shelves(opening)
        self._reconcile_doors(opening, side)
        self._reconcile_drawers(opening, side)
        self._reconcile_cubbies(opening)

        lo = ro = (pt - const.FRONT_GAP) / 2.0
        to = bo = (st - const.FRONT_GAP) / 2.0
        if side == 'BACK':
            front_y = const.DOOR_TO_CABINET_GAP
        else:
            front_y = -depth - const.DOOR_TO_CABINET_GAP

        groups = {}
        for child in list(opening.children):
            role = child.get('hb_part_role')
            if role == PART_ROLE_FIXED_SHELF:
                z_off = child.get('hb_z_offset', 0.0)
                z = (interior_h - z_off if child.get('hb_anchor_top')
                     else z_off)
                z = max(0.0, min(z, interior_h - st))
                child.location = (0.0, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)
            elif role == PART_ROLE_ROD:
                z_off = child.get('hb_z_offset', const.ROD_TOP_OFFSET)
                z = (interior_h - z_off if child.get('hb_anchor_top')
                     else z_off)
                z = max(const.ROD_RADIUS,
                        min(z, interior_h - const.ROD_RADIUS))
                child.location = (0.0, -depth / 2.0, z)
                GeoNodeObject(child).set_input('Dim X', width)
            elif role is not None:
                groups.setdefault(role, []).append(child)

        # ----- Adjustable shelves: even spacing bottom-up -----
        adj = groups.get(PART_ROLE_ADJ_SHELF, [])
        if adj:
            adj.sort(key=lambda o: o.get('hb_adj_index', 0))
            spacing = interior_h / (len(adj) + 1)
            for i, child in enumerate(adj):
                z = max(0.0, min(spacing * (i + 1), interior_h - st))
                child.location = (0.0, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)

        # ----- Doors (1 leaf, or 2 for DOUBLE swing) -----
        doors = groups.get(PART_ROLE_DOOR, [])
        if doors:
            doors.sort(key=lambda o: o.get('hb_door_index', 0))
            full = width + lo + ro
            if len(doors) == 2:
                leaf = (full - const.FRONT_GAP) / 2.0
            else:
                leaf = full
            for i, child in enumerate(doors):
                x = -lo + i * (leaf + const.FRONT_GAP)
                child.location = (x, front_y, -bo)
                part = GeoNodeCutpart(child)
                part.set_input('Length', leaf)
                part.set_input('Width', interior_h + to + bo)
                part.set_input('Thickness', const.FRONT_THICKNESS)

        # ----- Drawer stack (bottom-up fronts + boxes) -----
        fronts = groups.get(PART_ROLE_DRAWER_FRONT, [])
        boxes = {c.get('hb_drawer_index', 0): c
                 for c in groups.get(PART_ROLE_DRAWER_BOX, [])}
        if fronts:
            fronts.sort(key=lambda o: o.get('hb_drawer_index', 0))
            dh = opening.get(PROP_DRAWER_FRONT_HEIGHT,
                             const.DRAWER_FRONT_HEIGHT)
            box_w = max(width - 2 * const.DRAWER_SLIDE_GAP, inch(2.0))
            box_d = max(depth - const.DRAWER_BOX_DEPTH_DEDUCT, inch(2.0))
            box_h = max(dh - const.DRAWER_BOX_HEIGHT_DEDUCT, inch(2.0))
            for i, child in enumerate(fronts):
                z = -bo + i * (dh + const.FRONT_GAP)
                child.location = (-lo, front_y, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width + lo + ro)
                part.set_input('Width', dh)
                part.set_input('Thickness', const.FRONT_THICKNESS)
                box = boxes.get(i)
                if box is not None:
                    # GeoNodeDrawerBox extrudes +Y from its origin, so
                    # anchor the origin at the face the drawer serves:
                    # box spans [y_box, y_box + box_d], front edge flush
                    # with the opening face, DEDUCT clearance at the rear.
                    y_box = (-box_d if side == 'BACK' else -depth)
                    box.location = (const.DRAWER_SLIDE_GAP, y_box,
                                    max(z, 0.0) + const.DRAWER_BOX_Z_LIFT)
                    gb = GeoNodeObject(box)
                    gb.set_input('Dim X', box_w)
                    gb.set_input('Dim Y', box_d)
                    gb.set_input('Dim Z', box_h)

        # ----- Cubby grid (divisions full height, shelves full width) -----
        divs = groups.get(PART_ROLE_CUBBY_DIVISION, [])
        if divs:
            divs.sort(key=lambda o: o.get('hb_cubby_index', 0))
            cols = len(divs) + 1
            cell_w = (width - len(divs) * st) / cols
            for j, child in enumerate(divs):
                x = cell_w * (j + 1) + st * j
                child.location = (x, 0.0, 0.0)
                part = GeoNodeCutpart(child)
                part.set_input('Length', interior_h)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)
        cub_shelves = groups.get(PART_ROLE_CUBBY_SHELF, [])
        if cub_shelves:
            cub_shelves.sort(key=lambda o: o.get('hb_cubby_index', 0))
            rows = len(cub_shelves) + 1
            cell_h = (interior_h - len(cub_shelves) * st) / rows
            for k, child in enumerate(cub_shelves):
                z = cell_h * (k + 1) + st * k
                child.location = (0.0, 0.0, z)
                part = GeoNodeCutpart(child)
                part.set_input('Length', width)
                part.set_input('Width', depth)
                part.set_input('Thickness', st)

    # ----- regenerators (create/remove children to match config) -----

    def _reconcile_adj_shelves(self, opening):
        qty = max(0, int(opening.get(PROP_ADJ_SHELF_QTY, 0)))
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_ADJ_SHELF]
        existing.sort(key=lambda o: o.get('hb_adj_index', 0))
        while len(existing) > qty:
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        while len(existing) < qty:
            obj = add_fixed_shelf(opening, 0.0, role=PART_ROLE_ADJ_SHELF)
            obj['hb_adj_index'] = len(existing)
            existing.append(obj)

    def _make_front(self, opening, name, role, side):
        """Vertical slab front. rot_x 90 stands the part up (thickness
        extrudes -Y); BACK-side fronts Mirror Z to extrude +Y instead."""
        front = CabinetPart()
        front.create(name)
        front.obj.parent = opening
        front.obj['hb_part_role'] = role
        front.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
        front.obj.rotation_euler.x = math.radians(90)
        if side == 'BACK':
            front.set_input('Mirror Z', True)
        return front.obj

    def _reconcile_doors(self, opening, side):
        swing = opening.get(PROP_DOOR_SWING, '')
        qty = {'LEFT': 1, 'RIGHT': 1, 'DOUBLE': 2}.get(swing, 0)
        existing = [c for c in opening.children
                    if c.get('hb_part_role') == PART_ROLE_DOOR]
        existing.sort(key=lambda o: o.get('hb_door_index', 0))
        while len(existing) > qty:
            bpy.data.objects.remove(existing.pop(), do_unlink=True)
        while len(existing) < qty:
            name = 'Hamper Front' if opening.get(PROP_IS_HAMPER) else 'Door'
            obj = self._make_front(opening, name, PART_ROLE_DOOR, side)
            obj['hb_door_index'] = len(existing)
            obj['hb_is_hamper'] = 1 if opening.get(PROP_IS_HAMPER) else 0
            existing.append(obj)

    def _reconcile_drawers(self, opening, side):
        qty = max(0, int(opening.get(PROP_DRAWER_QTY, 0)))
        fronts = [c for c in opening.children
                  if c.get('hb_part_role') == PART_ROLE_DRAWER_FRONT]
        boxes = [c for c in opening.children
                 if c.get('hb_part_role') == PART_ROLE_DRAWER_BOX]
        fronts.sort(key=lambda o: o.get('hb_drawer_index', 0))
        boxes.sort(key=lambda o: o.get('hb_drawer_index', 0))
        while len(fronts) > qty:
            bpy.data.objects.remove(fronts.pop(), do_unlink=True)
        while len(boxes) > qty:
            bpy.data.objects.remove(boxes.pop(), do_unlink=True)
        while len(fronts) < qty:
            obj = self._make_front(opening, 'Drawer Front',
                                   PART_ROLE_DRAWER_FRONT, side)
            obj['hb_drawer_index'] = len(fronts)
            fronts.append(obj)
        while len(boxes) < qty:
            box = GeoNodeDrawerBox()
            box.create('Drawer Box')
            box.obj.parent = opening
            box.obj['hb_part_role'] = PART_ROLE_DRAWER_BOX
            box.obj['hb_drawer_index'] = len(boxes)
            boxes.append(box.obj)

    def _reconcile_cubbies(self, opening):
        cols = max(1, int(opening.get(PROP_CUBBY_COLS, 1)))
        rows = max(1, int(opening.get(PROP_CUBBY_ROWS, 1)))
        want_divs = cols - 1
        want_shelves = rows - 1
        divs = [c for c in opening.children
                if c.get('hb_part_role') == PART_ROLE_CUBBY_DIVISION]
        shelves = [c for c in opening.children
                   if c.get('hb_part_role') == PART_ROLE_CUBBY_SHELF]
        divs.sort(key=lambda o: o.get('hb_cubby_index', 0))
        shelves.sort(key=lambda o: o.get('hb_cubby_index', 0))
        while len(divs) > want_divs:
            bpy.data.objects.remove(divs.pop(), do_unlink=True)
        while len(shelves) > want_shelves:
            bpy.data.objects.remove(shelves.pop(), do_unlink=True)
        while len(divs) < want_divs:
            div = CabinetPart()
            div.create('Cubby Division')
            div.obj.parent = opening
            div.obj['hb_part_role'] = PART_ROLE_CUBBY_DIVISION
            div.obj['hb_cubby_index'] = len(divs)
            div.obj['MENU_ID'] = 'HOME_BUILDER_MT_closet_part_commands'
            div.obj.rotation_euler.y = math.radians(-90)
            div.set_input('Mirror Y', True)
            div.set_input('Mirror Z', True)
            divs.append(div.obj)
        while len(shelves) < want_shelves:
            obj = add_fixed_shelf(opening, 0.0, role=PART_ROLE_CUBBY_SHELF)
            obj['hb_cubby_index'] = len(shelves)
            shelves.append(obj)

    def _bay_split_shelves(self, bay_obj, side):
        """Committed splitting shelves of one side, bottom-up."""
        shelves = [c for c in bay_obj.children
                   if c.get('hb_part_role') == PART_ROLE_FIXED_SHELF
                   and c.get(PROP_OPENING_SIDE, 'FRONT') == side
                   and not c.get('hb_preview')]
        shelves.sort(key=lambda o: o.get('hb_z_offset', 0.0))
        return shelves

    def _reconcile_bay_openings(self, bay_obj):
        """Adopt committed fixed shelves up to bay level (they arrive as
        opening children from the add-part modal / older files) and keep
        exactly one opening cage per interior segment on each side.
        Removing a shelf merges segments; the removed opening's contents
        re-home into the lowest surviving opening rather than dying."""
        for opening in [c for c in bay_obj.children
                        if c.get(TAG_OPENING_CAGE)]:
            seg_bottom = opening.get('hb_seg_bottom', 0.0)
            side = opening.get(PROP_OPENING_SIDE, 'FRONT')
            for child in list(opening.children):
                if (child.get('hb_part_role') == PART_ROLE_FIXED_SHELF
                        and not child.get('hb_preview')):
                    child.parent = bay_obj
                    # Opening-local -> bay-interior datum. Top-anchored
                    # offsets convert via the segment the shelf was in.
                    z_off = child.get('hb_z_offset', 0.0)
                    if child.get('hb_anchor_top'):
                        try:
                            seg_h = GeoNodeCage(opening).get_input('Dim Z')
                        except Exception:
                            seg_h = 0.0
                        z_off = max(0.0, seg_h - z_off)
                    child['hb_z_offset'] = float(seg_bottom + z_off)
                    child['hb_anchor_top'] = 0
                    child[PROP_OPENING_SIDE] = side

        sides = ('FRONT', 'BACK') if self.is_double else ('FRONT',)
        for side in sides:
            want = len(self._bay_split_shelves(bay_obj, side)) + 1
            openings = sorted(
                [c for c in bay_obj.children
                 if c.get(TAG_OPENING_CAGE)
                 and c.get(PROP_OPENING_SIDE, 'FRONT') == side],
                key=lambda o: o.get('hb_opening_index', 0))
            while len(openings) > want:
                extra = openings.pop()
                for child in list(extra.children):
                    child.parent = openings[0]
                bpy.data.objects.remove(extra, do_unlink=True)
            while len(openings) < want:
                op = ClosetOpening()
                op.create(f'Opening {len(openings) + 1}')
                op.obj.parent = bay_obj
                if side == 'BACK':
                    op.obj[PROP_OPENING_SIDE] = 'BACK'
                openings.append(op.obj)
            for i, op_obj in enumerate(openings):
                op_obj['hb_opening_index'] = i

    def _layout_starter_parts(self, layout, scene_props, sp):
        ctop = self._root_part(PART_ROLE_COUNTERTOP)
        if ctop is None and sp.include_countertop:
            # Lazily create the part so include_countertop works on
            # starters whose class didn't seed one (Tall/Hanging, and
            # units placed before this landed).
            part = CabinetPart()
            part.create('Countertop')
            part.obj.parent = self.obj
            part.obj['hb_part_role'] = PART_ROLE_COUNTERTOP
            part.set_input('Mirror Y', True)
            ctop = part.obj
        if ctop is not None:
            part = GeoNodeCutpart(ctop)
            if self.ctop_overhang_all:
                oh = const.ISLAND_CTOP_OVERHANG
                ctop.location = (-oh, oh, sp.height)
                part.set_input('Length', sp.width + 2 * oh)
                part.set_input('Width', sp.depth + 2 * oh)
            else:
                ctop.location = (0.0, 0.0, sp.height)
                part.set_input('Length', sp.width)
                part.set_input('Width',
                               sp.depth + const.COUNTERTOP_OVERHANG_FRONT)
            part.set_input('Thickness', scene_props.countertop_thickness)
            _set_part_hidden(ctop, not sp.include_countertop)


    # -----------------------------------------------------------------
    # Structural mutation (insert / delete bay)
    # -----------------------------------------------------------------
    def insert_bay(self, anchor_index, direction):
        """Insert a new bay next to an existing one.

        direction: 'BEFORE' (new bay takes the anchor's slot) or 'AFTER'.
        The new bay copies the anchor's height/depth/floor_mounted and
        comes in unlocked at width 0, so the redistributor immediately
        gives it an equal share. Panel i is the LEFT panel of bay i, so
        inserting at index k adds one panel at index k+1 and bumps every
        panel index >= k+1 and bay index >= k.
        """
        bays = self._sorted_bays()
        if not bays:
            return None
        anchor_index = max(0, min(anchor_index, len(bays) - 1))
        anchor_bay = bays[anchor_index]
        k = anchor_index if direction == 'BEFORE' else anchor_index + 1

        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            for bay_obj in bays:
                idx = bay_obj.get('hb_bay_index', 0)
                if idx >= k:
                    bay_obj['hb_bay_index'] = idx + 1
                    bay_obj.hb_closet_bay.bay_index = idx + 1
            for panel_obj in self._sorted_panels():
                idx = panel_obj.get('hb_panel_index', 0)
                if idx >= k + 1:
                    panel_obj['hb_panel_index'] = idx + 1

            panel = CabinetPart()
            panel.create(f'Partition {k + 2}')
            panel.obj.parent = self.obj
            panel.obj['hb_part_role'] = PART_ROLE_PANEL
            panel.obj['hb_panel_index'] = k + 1
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.set_input('Mirror Y', True)
            panel.set_input('Mirror Z', True)

            bay = ClosetBay()
            bay.create(f'Bay {k + 1}')
            bay.obj.parent = self.obj
            bay.obj['hb_bay_index'] = k
            src = anchor_bay.hb_closet_bay
            bp = bay.obj.hb_closet_bay
            bp.bay_index = k
            bp.width = 0.0
            bp.width_locked = False
            bp.height = src.height
            bp.depth = src.depth
            bp.floor_mounted = src.floor_mounted
            self._build_bay_parts(bay.obj)
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()
        return bay.obj

    def delete_bay(self, bay_index):
        """Delete the bay at bay_index plus one shared panel. Refuses to
        leave zero bays. Deleting bay k removes panel k+1 (the panel to
        its right), except for the last bay which removes panel k."""
        bays = self._sorted_bays()
        if len(bays) <= 1:
            return False
        bay_index = max(0, min(bay_index, len(bays) - 1))
        removed_panel_idx = (bay_index + 1
                             if bay_index < len(bays) - 1 else bay_index)

        cabinet_id = id(self.obj)
        _RECALCULATING.add(cabinet_id)
        _DISTRIBUTING_WIDTHS.add(cabinet_id)
        try:
            bay_obj = bays[bay_index]
            for child in list(bay_obj.children_recursive):
                bpy.data.objects.remove(child, do_unlink=True)
            bpy.data.objects.remove(bay_obj, do_unlink=True)

            for panel_obj in self._sorted_panels():
                idx = panel_obj.get('hb_panel_index', 0)
                if idx == removed_panel_idx:
                    bpy.data.objects.remove(panel_obj, do_unlink=True)
                    break
            for panel_obj in self._sorted_panels():
                idx = panel_obj.get('hb_panel_index', 0)
                if idx > removed_panel_idx:
                    panel_obj['hb_panel_index'] = idx - 1
            for other in self._sorted_bays():
                idx = other.get('hb_bay_index', 0)
                if idx > bay_index:
                    other['hb_bay_index'] = idx - 1
                    other.hb_closet_bay.bay_index = idx - 1
        finally:
            _RECALCULATING.discard(cabinet_id)
            _DISTRIBUTING_WIDTHS.discard(cabinet_id)

        self.recalculate()
        return True


# ---------------------------------------------------------------------------
# Starter subclasses
# ---------------------------------------------------------------------------
class BaseClosetStarter(ClosetStarter):
    default_closet_type = 'BASE'
    has_countertop = True


class TallClosetStarter(ClosetStarter):
    default_closet_type = 'TALL'


class HangingClosetStarter(ClosetStarter):
    default_closet_type = 'HANGING'
    has_toe_kick = False
    floor_mounted = False


class IslandClosetStarter(ClosetStarter):
    """Single-sided island: Base geometry plus an applied back closing
    the rear face."""
    default_closet_type = 'ISLAND'
    has_countertop = True
    has_applied_back = True


class DoubleIslandClosetStarter(IslandClosetStarter):
    """Double-sided island: deep carcass accessible from both faces with
    a center back in each bay, rear toe kick, and a countertop that
    overhangs all around. Each bay carries FRONT and BACK openings."""
    has_applied_back = False
    is_double = True
    ctop_overhang_all = True
    default_depth = const.ISLAND_DOUBLE_DEPTH


CLOSET_NAME_DISPATCH = {
    'Base': BaseClosetStarter,
    'Tall': TallClosetStarter,
    'Hanging': HangingClosetStarter,
    'Island': IslandClosetStarter,
    'Island Double': DoubleIslandClosetStarter,
}

WRAP_CLASS_REGISTRY = {cls.__name__: cls for cls in CLOSET_NAME_DISPATCH.values()}
WRAP_CLASS_REGISTRY['ClosetStarter'] = ClosetStarter


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------
def get_starter_class(starter_name):
    """Return the ClosetStarter subclass for a library item name."""
    return CLOSET_NAME_DISPATCH.get(starter_name)


def auto_bay_qty(width):
    """Bay count for a given total width, aiming near the legacy 20"
    bay (80" default / 4 bays). Used by the placement modal's fill mode."""
    target = inch(20.0)
    return max(1, min(9, int(round(width / target))))


def find_bay_cage(obj):
    """Walk up parents from obj to the containing bay cage, or None."""
    current = obj
    while current is not None:
        if current.get(TAG_BAY_CAGE):
            return current
        current = current.parent
    return None


def find_opening_cage(obj):
    """Resolve the opening cage for any object in a closet hierarchy:
    the object's own opening if it's under one, else the (single)
    opening of its bay."""
    current = obj
    while current is not None:
        if current.get(TAG_OPENING_CAGE):
            return current
        current = current.parent
    bay = find_bay_cage(obj)
    if bay is None:
        return None
    for child in bay.children:
        if child.get(TAG_OPENING_CAGE):
            return child
    return None


def find_starter_root(obj):
    """Walk up parents from obj to the closet starter root, or None."""
    current = obj
    while current is not None:
        if current.get(TAG_STARTER_CAGE):
            return current
        current = current.parent
    return None


def _wrap_starter(obj):
    """Wrap a starter root Object as its ClosetStarter subclass."""
    cls = WRAP_CLASS_REGISTRY.get(obj.get('CLASS_NAME', ''), ClosetStarter)
    instance = cls.__new__(cls)
    GeoNodeCage.__init__(instance, obj)
    return instance


def recalculate_closet_starter(obj):
    """Public recalc entry point for prop update callbacks and operators.
    Accepts the root or any descendant; no-ops while that starter is
    already mid-recalc."""
    root = find_starter_root(obj)
    if root is None or id(root) in _RECALCULATING:
        return
    _wrap_starter(root).recalculate()


def delete_starter(root_obj):
    """Remove a starter root and every descendant object."""
    for child in list(root_obj.children_recursive):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(root_obj, do_unlink=True)
