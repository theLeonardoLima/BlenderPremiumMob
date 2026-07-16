"""
Python-built door geometry (no geometry nodes).

First step of moving door construction off the CPM_5PIECEDOOR geometry
node modifier: a door is real parts -- left / right stiles, top / bottom
rails, an optional mid rail, and inset panel(s) -- laid out from a
Face_Frame_Door_Style's construction fields. The wood hood bay doors
build from this now; cabinet fronts can migrate in the wider door
overhaul (outer / inner / panel profiles become sweeps along these same
rects without changing callers).

door_layout returns DATA rather than objects so any consumer can realize
the parts its own way (driven cutparts, static meshes, a future profile
sweep). Every rect dimension is linear in the door's overall width W or
height H, expressed as a (coefficient, offset) pair: value = coef * W +
offset (x / w against W; z / h against H). A static builder just
evaluates the pairs (evaluate_layout, or build_door_mesh for a ready
mesh in cutpart-local space); a driven builder (the wood hood) composes
them into driver expressions so the parts track their cage.
"""

from ...units import inch


# Master switch for the python-built cabinet-front door path: True has
# assign_style_to_front build fronts with build_door_mesh; False
# restores the CPM_5PIECEDOOR modifier path.
USE_PYTHON_DOORS = True


# Construction fields read off a Face_Frame_Door_Style, with the
# fallbacks used when no style resolves (matching the property defaults
# in props_hb_face_frame).
DOOR_STYLE_FALLBACK = {
    'door_type': '5_PIECE',
    'stile_width': inch(3.0),
    'rail_width': inch(3.0),
    'add_mid_rail': False,
    'center_mid_rail': True,
    'mid_rail_width': inch(3.0),
    'mid_rail_location': inch(12.0),
    'panel_thickness': inch(0.5),
    'panel_inset': inch(0.25),
    # Grid dividers (no Face_Frame_Door_Style fields yet -- consumers
    # set these on the info dict): counts of equally spaced mid rails /
    # mid stiles splitting the field into panel cells. mid_rail_count
    # overrides the legacy single add_mid_rail when > 0.
    'mid_rail_count': 0,
    'mid_stile_count': 0,
    # Per-side frame widths, also consumer-set: None falls back to the
    # uniform stile_width / rail_width (mid_stile_width to stile_width).
    # A per-side 0.0 is honored -- it drops that member so adjacent
    # doors can butt.
    'left_stile_width': None,
    'right_stile_width': None,
    'top_rail_width': None,
    'bottom_rail_width': None,
    'mid_stile_width': None,
    # Explicit mid-rail centerline as a (coef, offset) pair against the
    # door height. When set (and mid_rail_count is 0) it forces a single
    # mid rail there, winning over add_mid_rail / center_mid_rail /
    # mid_rail_location.
    'mid_rail_z': None,
}


def _frame_widths(info):
    """Effective member widths (left stile, right stile, mid stile,
    top rail, bottom rail, mid rail). The uniform widths are floored
    at 1/2"; per-side overrides fall back to them when None and are
    only floored at 0.0 so an explicit no-stile side stays empty."""
    sw = max(info['stile_width'], inch(0.5))
    rw = max(info['rail_width'], inch(0.5))
    mrw = max(info['mid_rail_width'], inch(0.5))

    def eff(key, base):
        v = info.get(key)
        return base if v is None else max(v, 0.0)

    return (eff('left_stile_width', sw), eff('right_stile_width', sw),
            eff('mid_stile_width', sw), eff('top_rail_width', rw),
            eff('bottom_rail_width', rw), mrw)


def door_style_info(style=None):
    """Plain-dict snapshot of a door style's construction fields
    (DOOR_STYLE_FALLBACK for None / missing fields), so the layout math
    doesn't hold RNA references."""
    info = dict(DOOR_STYLE_FALLBACK)
    if style is not None:
        for key in info:
            info[key] = getattr(style, key, info[key])
    return info


def layout_min_size(info):
    """(min_width, min_height) below which the 5-piece layout collapses
    (members would overlap); at or under these the caller should build
    the door as a slab instead."""
    if info.get('door_type') == 'SLAB':
        return 0.0, 0.0
    lsw, rsw, msw, trw, brw, mrw = _frame_widths(info)
    k = max(int(info.get('mid_rail_count', 0) or 0), 0)
    if k == 0 and (info.get('add_mid_rail')
                   or info.get('mid_rail_z') is not None):
        k = 1
    m = max(int(info.get('mid_stile_count', 0) or 0), 0)
    return lsw + rsw + m * msw + inch(0.5), trw + brw + k * mrw + inch(0.5)


def door_layout(info):
    """Part rects for one door in door-local space: x across from the
    left edge, z up from the bottom edge. Returns a list of dicts:

      key       -- 'slab' / 'left_stile' / 'right_stile' / 'top_rail' /
                   'bottom_rail' / 'mid_rail' / 'mid_stile' / 'panel'
      name      -- display name ("Left Stile", ...)
      x, w      -- (coef, offset) against the door width
      z, h      -- (coef, offset) against the door height
      thickness -- None = the caller's door thickness (frame members /
                   slab); a float for the thinner panel
      y_inset   -- setback of the part's front face from the door's
                   front face (panels; 0 for frame members)

    Mid rails / mid stiles divide the field into a grid of panel
    cells: mid rails run the full field width, mid stiles run between
    the rails segmented per panel row (six-panel-door construction).
    ``mid_rail_count`` (equally spaced) overrides the legacy single
    add_mid_rail when > 0; an explicit ``mid_rail_z`` centerline pair
    wins over add_mid_rail. Per-side frame widths come from the
    left/right stile and top/bottom rail overrides when set (a 0.0
    side emits a zero-width member the realizers skip); mid stiles
    use mid_stile_width, falling back to the outer stile width.
    """
    if info.get('door_type') == 'SLAB':
        return [dict(key='slab', name="Slab", x=(0.0, 0.0), w=(1.0, 0.0),
                     z=(0.0, 0.0), h=(1.0, 0.0), thickness=None,
                     y_inset=0.0)]
    lsw, rsw, msw, trw, brw, mrw = _frame_widths(info)
    p_th = max(info['panel_thickness'], inch(0.125))
    p_in = max(info['panel_inset'], 0.0)
    k = max(int(info.get('mid_rail_count', 0) or 0), 0)
    m = max(int(info.get('mid_stile_count', 0) or 0), 0)
    mid_z = info.get('mid_rail_z')
    parts = [
        dict(key='left_stile', name="Left Stile", x=(0.0, 0.0), w=(0.0, lsw),
             z=(0.0, 0.0), h=(1.0, 0.0), thickness=None, y_inset=0.0),
        dict(key='right_stile', name="Right Stile", x=(1.0, -rsw),
             w=(0.0, rsw), z=(0.0, 0.0), h=(1.0, 0.0), thickness=None,
             y_inset=0.0),
        dict(key='bottom_rail', name="Bottom Rail", x=(0.0, lsw),
             w=(1.0, -(lsw + rsw)), z=(0.0, 0.0), h=(0.0, brw),
             thickness=None, y_inset=0.0),
        dict(key='top_rail', name="Top Rail", x=(0.0, lsw),
             w=(1.0, -(lsw + rsw)), z=(1.0, -trw), h=(0.0, trw),
             thickness=None, y_inset=0.0),
    ]
    # Panel rows as (z, h) linear pairs, with the mid rails between them.
    if k > 0:
        fh = (1.0, -(trw + brw + k * mrw))    # field height, linear in H
        rows = [((fh[0] * i / (k + 1), fh[1] * i / (k + 1) + brw + i * mrw),
                 (fh[0] / (k + 1), fh[1] / (k + 1)))
                for i in range(k + 1)]
        for i in range(1, k + 1):
            parts.append(dict(
                key='mid_rail',
                name="Mid Rail %d" % i if k > 1 else "Mid Rail",
                x=(0.0, lsw), w=(1.0, -(lsw + rsw)),
                z=(fh[0] * i / (k + 1),
                   fh[1] * i / (k + 1) + brw + (i - 1) * mrw),
                h=(0.0, mrw), thickness=None, y_inset=0.0))
    elif mid_z is not None or info.get('add_mid_rail'):
        # Single mid rail: the explicit centerline pair when given,
        # else the legacy centered / fixed-location fields. mz is the
        # rail's BOTTOM edge as a (coef, offset) pair.
        if mid_z is not None:
            mz = (mid_z[0], mid_z[1] - mrw / 2.0)
        elif info.get('center_mid_rail', True):
            mz = (0.5, -mrw / 2.0)
        else:
            mz = (0.0, max(info['mid_rail_location'], brw))
        parts.append(dict(key='mid_rail', name="Mid Rail", x=(0.0, lsw),
                          w=(1.0, -(lsw + rsw)), z=mz, h=(0.0, mrw),
                          thickness=None, y_inset=0.0))
        rows = [((0.0, brw), (mz[0], mz[1] - brw)),
                ((mz[0], mz[1] + mrw), (1.0 - mz[0], -trw - mz[1] - mrw))]
    else:
        rows = [((0.0, brw), (1.0, -(trw + brw)))]
    # Panel columns as (x, w) linear pairs; mid stiles between them,
    # one set per row (they butt the rails).
    if m > 0:
        cw = (1.0 / (m + 1), -(lsw + rsw + m * msw) / (m + 1))
        cols = [((c * cw[0], c * (cw[1] + msw) + lsw), cw)
                for c in range(m + 1)]
    else:
        cols = [((0.0, lsw), (1.0, -(lsw + rsw)))]
    grid = len(rows) > 1 or len(cols) > 1
    for r, (rz, rh) in enumerate(rows):
        for j in range(1, m + 1):
            name = ("Mid Stile %d-%d" % (r + 1, j) if len(rows) > 1
                    else ("Mid Stile %d" % j if m > 1 else "Mid Stile"))
            parts.append(dict(key='mid_stile', name=name,
                              x=(j * cw[0], j * (cw[1] + msw) + lsw - msw),
                              w=(0.0, msw), z=rz, h=rh,
                              thickness=None, y_inset=0.0))
        for c, (cx, cwid) in enumerate(cols):
            name = "Panel %d-%d" % (r + 1, c + 1) if grid else "Panel"
            parts.append(dict(key='panel', name=name, x=cx, w=cwid,
                              z=rz, h=rh, thickness=p_th, y_inset=p_in))
    return parts


def evaluate_layout(info, width, height):
    """door_layout realized at a concrete door size: the same part
    dicts with absolute rects alongside the linear pairs -- x0/x1
    across from the left edge, z0/z1 up from the bottom edge
    (door-local, meters)."""
    parts = []
    for part in door_layout(info):
        x0 = part['x'][0] * width + part['x'][1]
        z0 = part['z'][0] * height + part['z'][1]
        parts.append(dict(part,
                          x0=x0, x1=x0 + part['w'][0] * width + part['w'][1],
                          z0=z0, z1=z0 + part['h'][0] * height + part['h'][1]))
    return parts


# Material slot per part key for build_door_mesh, matching the
# (stile, rail, panel) triple it accepts.
_PART_MAT_SLOT = {
    'slab': 0, 'left_stile': 0, 'right_stile': 0, 'mid_stile': 0,
    'top_rail': 1, 'bottom_rail': 1, 'mid_rail': 1, 'panel': 2,
}


def build_door_mesh(mesh, info, width, height, thickness, materials=None):
    """Replace ``mesh``'s geometry with the door built as static boxes
    in front-cutpart local space: the door height runs along +X from
    the bottom edge at x=0, the width along -Y (a front cutpart with
    Mirror Y set) with the door's LEFT edge at y=0 -- for a face-frame
    front that is the viewer's left, unlike the CPM_5PIECEDOOR node,
    which rendered its Left / Right stile inputs on the opposite
    sides from their names. The front face is at z=thickness; panels
    sit back from it by their y_inset and use their own thickness.

    ``materials`` is an optional (stile, rail, panel) triple assigned
    as the mesh's material slots; face material indices are set either
    way (mid stiles index as stiles, mid rails as rails). Zero-size
    members (e.g. a per-side stile width of 0.0) are skipped.
    """
    verts = []
    faces = []
    face_slots = []
    for part in evaluate_layout(info, width, height):
        if part['x1'] - part['x0'] <= 0.0 or part['z1'] - part['z0'] <= 0.0:
            continue
        th = thickness if part['thickness'] is None else part['thickness']
        zf = thickness - part['y_inset']
        x0, x1 = part['z0'], part['z1']
        y0, y1 = -part['x1'], -part['x0']
        z0, z1 = zf - th, zf
        b = len(verts)
        verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        faces.extend([(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7),
                      (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5),
                      (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)])
        face_slots.extend([_PART_MAT_SLOT[part['key']]] * 6)
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    # Slots first: clearing materials drops the material_index layer.
    if materials is not None:
        mesh.materials.clear()
        for mat in materials:
            mesh.materials.append(mat)
    attr = (mesh.attributes.get('material_index')
            or mesh.attributes.new('material_index', 'INT', 'FACE'))
    attr.data.foreach_set('value', face_slots)
    mesh.update()
