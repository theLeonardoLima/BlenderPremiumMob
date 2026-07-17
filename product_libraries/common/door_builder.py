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

import math

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


def _panel_grid(info, width, height):
    """Opening (panel-cell) rects from the layout, grouped into rows:
    [[(x0, z0, x1, z1), ...], ...] bottom row first, left to right."""
    rows = {}
    for p in evaluate_layout(info, width, height):
        if p['key'] != 'panel':
            continue
        rows.setdefault(round(p['z0'], 6), []).append(
            (p['x0'], p['z0'], p['x1'], p['z1']))
    return [sorted(rows[k]) for k in sorted(rows)]


def build_mitered_frame(info, width, height, thickness, member_section):
    """A MITERED door's frame as (verts, faces, slots) in front-cutpart
    local space (same space as build_door_mesh; slots index the stile /
    rail / panel materials). Panels are the caller's job.

    The whole member cross-section is one molding profile: a single
    sweep around the door, mitred at the corners, covers the outer
    edge, the shaped face, and the opening walls (the section carries
    all three -- door_profiles.member_section: u across the member from
    the OUTER edge, v from the front face, both ends closed to the door
    back). Only the flat BACK face is filled separately: four quads
    from the door rect to the openings' hull plus strips across any
    mid members.
    """
    W, H, T = width, height, thickness
    rows = _panel_grid(info, W, H)
    if not rows:
        return [], [], []

    verts, faces, slots = [], [], []
    side_slots = (1, 0, 1, 0)   # bottom, right, top, left

    def emit(x, z, v):
        # Door-local (x across from left, z up, v deep from the front
        # face) into cutpart-local, matching build_door_mesh's mapping.
        verts.append((z, -x, T - v))
        return len(verts) - 1

    corners = ((0.0, 0.0), (W, 0.0), (W, H), (0.0, H))
    dirs = ((1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
    n = len(member_section)
    base = len(verts)
    for (cx, cz), (dx, dz) in zip(corners, dirs):
        for (u, v) in member_section:
            emit(cx + dx * u, cz + dz * u, v)
    for c in range(4):
        a = base + c * n
        b = base + ((c + 1) % 4) * n
        for k in range(n - 1):
            faces.append((a + k, a + k + 1, b + k + 1, b + k))
            slots.append(side_slots[c])

    # Flat back face: door rect down to the openings' hull, strips
    # across the mid members.
    def back_quad(x0, z0, x1, z1, slot):
        if x1 - x0 <= 1e-9 or z1 - z0 <= 1e-9:
            return
        a = emit(x0, z0, T)
        b = emit(x1, z0, T)
        c = emit(x1, z1, T)
        d = emit(x0, z1, T)
        faces.append((d, c, b, a))
        slots.append(slot)

    fx0 = min(c[0] for r in rows for c in r)
    fx1 = max(c[2] for r in rows for c in r)
    fz0 = rows[0][0][1]
    fz1 = rows[-1][0][3]
    Bc = ((fx0, fz0), (fx1, fz0), (fx1, fz1), (fx0, fz1))
    for c in range(4):
        a0 = emit(*corners[c], T)
        a1 = emit(*corners[(c + 1) % 4], T)
        b1 = emit(*Bc[(c + 1) % 4], T)
        b0 = emit(*Bc[c], T)
        faces.append((b0, b1, a1, a0))
        slots.append(side_slots[c])
    for r in range(len(rows) - 1):
        back_quad(fx0, rows[r][0][3], fx1, rows[r + 1][0][1], 1)
    for row in rows:
        for c in range(len(row) - 1):
            back_quad(row[c][2], row[c][1], row[c + 1][0], row[c][3], 0)
    return verts, faces, slots


def _resample_loop(loop, n):
    """Resample a CLOSED loop to n points by cumulative length."""
    if len(loop) == n:
        return list(loop)
    m = len(loop)
    d = [0.0]
    for i in range(m):
        a = loop[i]
        b = loop[(i + 1) % m]
        d.append(d[-1] + ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)
    total = d[-1] or 1.0
    out = []
    j = 0
    for k in range(n):
        t = total * k / n
        while j < m - 1 and d[j + 1] < t:
            j += 1
        a = loop[j]
        b = loop[(j + 1) % m]
        seg = (d[j + 1] - d[j]) or 1.0
        f = (t - d[j]) / seg
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return out


def _emit_strip_rings(verts, faces, slots, part, thickness,
                      loop_rail, loop_stile, scope='ALL',
                      top_pts=None, bottom_pts=None):
    """Applied sticking strip around one opening cell: a closed
    cross-section swept along the opening perimeter, mitred at the
    corners like a real applied molding, seated against the
    rectangular members. u runs from the member edge INTO the opening,
    v from the front face. With different rail / stile loops the
    corner mitre planes are closed with transition strips. top_pts /
    bottom_pts sweep the strip along a shaped (arched) edge instead of
    the straight one (ignored for scope RAILS -- no shaped series uses
    it). Skipped (returns False) when the cell is too small for the
    strips."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    wr = max(u for u, v in loop_rail)
    ws = max(u for u, v in loop_stile)
    if x1 - x0 <= 2.0 * ws + 1e-6 or z1 - z0 <= 2.0 * wr + 1e-6:
        return False

    def emit(x, z, v):
        verts.append((z, -x, thickness - v))
        return len(verts) - 1

    if scope == 'RAILS':
        # Straight strips along the opening's top and bottom edges
        # only, flat ends at the vertical opening edges closed with
        # the loop cross-section as an ngon cap.
        n = len(loop_rail)
        for edge_z, dz, flip in ((z1, -1.0, False), (z0, 1.0, True)):
            b0 = len(verts)
            for (u, v) in loop_rail:
                emit(x0, edge_z + dz * u, v)
            b1 = len(verts)
            for (u, v) in loop_rail:
                emit(x1, edge_z + dz * u, v)
            for k in range(n):
                k2 = (k + 1) % n
                q = (b0 + k, b0 + k2, b1 + k2, b1 + k)
                if flip:
                    q = q[::-1]
                faces.append(q)
                slots.append(_PART_MAT_SLOT['mid_rail'])
            caps = ((b0, not flip), (b1, flip))
            for base, rev in caps:
                idx = list(range(base, base + n))
                if rev:
                    idx.reverse()
                faces.append(tuple(idx))
                slots.append(_PART_MAT_SLOT['mid_rail'])
        return True

    mixed = loop_rail is not loop_stile
    if mixed:
        n = max(len(loop_rail), len(loop_stile))
        lr = _resample_loop(loop_rail, n)
        ls = _resample_loop(loop_stile, n)
    else:
        lr = ls = loop_rail
        n = len(lr)
    secs = (lr, ls, lr, ls)   # bottom, right, top, left
    # Perimeter stations (shaped cells add curve stations along the
    # top / bottom edge); each side closes on the next side's corner,
    # so the flat rect reduces to the classic 4-corner ring pairs.
    by_side = [[], [], [], []]
    for st in _cell_perimeter(part, top_pts, bottom_pts):
        by_side[st[2]].append(st)
    ring_first = []
    ring_last = []
    for s in range(4):
        sec = secs[s]
        seq = by_side[s] + [by_side[(s + 1) % 4][0]]
        bases = []
        for (pos, dv, _s) in seq:
            base = len(verts)
            for (u, v) in sec:
                emit(pos[0] + dv[0] * u, pos[1] + dv[1] * u, v)
            bases.append(base)
        for i in range(len(bases) - 1):
            a, b = bases[i], bases[i + 1]
            for k in range(n):
                k2 = (k + 1) % n
                faces.append((a + k, a + k2, b + k2, b + k))
                slots.append(_PART_MAT_SLOT['mid_rail' if s % 2 == 0
                                            else 'mid_stile'])
        ring_first.append(bases[0])
        ring_last.append(bases[-1])
    if mixed:
        for s in range(4):
            a = ring_last[s]
            b = ring_first[(s + 1) % 4]
            for k in range(n):
                k2 = (k + 1) % n
                faces.append((a + k, a + k2, b + k2, b + k))
                slots.append(_PART_MAT_SLOT['mid_rail'])
    return True


def _emit_raised_panel(verts, faces, slots, part, thickness, panel_section,
                       top_pts=None, bottom_pts=None):
    """Raised panel for one opening cell, appended to the caller's
    lists in cutpart-local space: a mitred sweep of the panel section
    around the cell (field end first, u inward from the cell edge, v
    behind the field plane), a flat field plate, and a back plate
    flush with the door back like a flat panel. The field plane sits
    at the part's y_inset. top_pts / bottom_pts run the raise along a
    shaped (arched) edge -- the cathedral raised panel -- via the
    shared perimeter-station sweep. Returns False -- caller keeps the
    flat box -- when the cell is too small for the raise."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    fu = panel_section['field_u']
    if min(x1 - x0, z1 - z0) <= 2.0 * fu + 1e-6:
        return False
    pf = part['y_inset']
    back_v = thickness - pf
    if back_v <= 1e-9:
        return False
    sec = [(u, min(v, back_v)) for (u, v) in panel_section['points']]
    if sec[-1][1] < back_v - 1e-9:
        sec.append((sec[-1][0], back_v))

    def emit(x, z, v):
        verts.append((z, -x, thickness - (pf + v)))
        return len(verts) - 1

    stations = _cell_perimeter(part, top_pts, bottom_pts)
    n = len(sec)
    m = len(stations)
    base = len(verts)
    for (pos, dv, _s) in stations:
        for (u, v) in sec:
            emit(pos[0] + dv[0] * u, pos[1] + dv[1] * u, v)
    for c in range(m):
        a = base + c * n
        b = base + ((c + 1) % m) * n
        for k in range(n - 1):
            faces.append((a + k, a + k + 1, b + k + 1, b + k))
            slots.append(2)
    # Field plate between the rings' field points.
    faces.append(tuple(base + c * n for c in range(m)))
    slots.append(2)
    # Back plate between the rings' back points.
    faces.append(tuple(base + (m - 1 - c) * n + n - 1 for c in range(m)))
    slots.append(2)
    return True


def _groove_section(style):
    """Cross-section of one panel groove: [(du, dv), ...] walked left
    to right across the groove (du in [-half, +half] off the groove
    centerline, dv depth into the panel face, 0 at the face). KERF is
    a plain square kerf slot; BEAD is the classic quirk-bead-quirk
    beadboard cut with the bead crest just below the face."""
    if style == 'KERF':
        hw = inch(0.0625)                 # 1/8 wide slot
        d = inch(0.09375)                 # 3/32 deep
        return [(-hw, 0.0), (-hw, d), (hw, d), (hw, 0.0)]
    q = inch(0.0625)                      # quirk width each side
    r = inch(0.09)                        # bead radius
    d = inch(0.11)                        # quirk depth (crest d - r below face)
    pts = [(-(r + q), 0.0), (-(r + q), d)]
    for i in range(13):
        a = math.pi * i / 12.0
        pts.append((-r * math.cos(a), d - r * math.sin(a)))
    pts += [(r + q, d), (r + q, 0.0)]
    return pts


def _emit_grooved_panel(verts, faces, slots, part, thickness, grooves):
    """Flat recessed panel as a full-height prism with groove
    cross-sections cut into its front face (beadboard / kerf-grooved
    panel choices). Grooves run vertically at ``grooves['spacing']``,
    the pattern centered so the middle plank straddles the panel
    centerline; grooves that would land within a margin of the panel
    edge are dropped. Returns False -- the caller keeps the plain
    box -- when no groove fits."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    th = thickness if part['thickness'] is None else part['thickness']
    zf = thickness - part['y_inset']
    zb = zf - th
    width = x1 - x0
    spacing = grooves.get('spacing', 0.0)
    if spacing <= 0.0 or zb < 0.0:
        return False
    sec = _groove_section(grooves.get('style', 'BEAD'))
    hw = max(du for du, dv in sec)
    if max(dv for du, dv in sec) >= th:
        return False
    margin = max(2.0 * hw, 0.004)
    k = 1 + int(width / spacing)
    centers = []
    for i in range(-k, k + 1):
        c = width / 2.0 + (i + 0.5) * spacing
        if c - hw >= margin and c + hw <= width - margin:
            centers.append(c)
    if not centers:
        return False
    centers.sort()
    # Closed cross-section loop in (layout x, depth): back face, up the
    # right edge, then the front face right to left with the grooves
    # dropped in, closing down the left edge.
    loop = [(x0, zb), (x1, zb), (x1, zf)]
    for c in reversed(centers):
        for du, dv in reversed(sec):
            loop.append((x0 + c + du, zf - dv))
    loop.append((x0, zf))
    n = len(loop)
    base = len(verts)
    for xm in (z0, z1):
        for (lx, dz) in loop:
            verts.append((xm, -lx, dz))
    for i in range(n):
        j = (i + 1) % n
        faces.append((base + i, base + n + i, base + n + j, base + j))
        slots.append(2)
    # End caps (planar concave ngons; buried against the rails).
    faces.append(tuple(base + i for i in range(n)))
    slots.append(2)
    faces.append(tuple(base + 2 * n - 1 - i for i in range(n)))
    slots.append(2)
    return True


# ---- Shaped (arched) opening edges ---------------------------------

def shape_rise(curve, w):
    """Peak rise of a shaped opening edge across a cell of width w.
    Proportions read off the catalog series drawings; capped so wide
    doors keep believable arches."""
    if curve == 'CROWN':
        return min(0.16 * w, inch(1.75))
    return min(0.20 * w, inch(2.25))    # ARCH


def _shape_curve_pts(curve, w, rise, segs=16):
    """Shaped opening-edge polyline across a cell of width w:
    [(x, rise), ...] left to right, x in [0, w], rise >= 0, both
    endpoints at 0. ARCH is the circular eyebrow arc through the peak;
    CROWN the cathedral ogee (reverse curves rising to a flat-topped
    center hump). Returns None for a degenerate span."""
    if rise <= 1e-6 or w <= 1e-6:
        return None
    if curve == 'CROWN':
        p0, p1, p2, p3 = ((0.0, 0.0), (0.22 * w, 0.0),
                          (0.30 * w, rise), (0.5 * w, rise))
        m = max(segs // 2, 4)
        half = []
        for i in range(m + 1):
            t = i / m
            mt = 1.0 - t
            half.append((mt ** 3 * p0[0] + 3.0 * mt * mt * t * p1[0]
                         + 3.0 * mt * t * t * p2[0] + t ** 3 * p3[0],
                         mt ** 3 * p0[1] + 3.0 * mt * mt * t * p1[1]
                         + 3.0 * mt * t * t * p2[1] + t ** 3 * p3[1]))
        pts = half + [(w - x, z) for (x, z) in reversed(half[:-1])]
    else:
        radius = (rise * rise + (w * 0.5) ** 2) / (2.0 * rise)
        cx, cz = w * 0.5, rise - radius
        a0 = math.atan2(-cz, -cx)
        a1 = math.atan2(-cz, w - cx)
        pts = []
        for i in range(segs + 1):
            a = a0 + (a1 - a0) * i / segs
            pts.append((cx + radius * math.cos(a),
                        max(cz + radius * math.sin(a), 0.0)))
    pts[0] = (0.0, 0.0)
    pts[-1] = (w, 0.0)
    return pts


def _cell_perimeter(part, top_pts=None, bottom_pts=None):
    """Sweep stations around a cell perimeter, counter-clockwise from
    the bottom-left corner: [(pos, dir, side)] where a swept section
    point at inward distance u sits at ``pos + dir * u`` (dir is the
    angle-bisector mitre direction, stretched 1/(1 + n1.n2) so offset
    edges meet -- the flat-rect corners reduce to the classic (1, 1)
    diagonals) and side is 0..3 (bottom / right / top / left).
    top_pts / bottom_pts replace the straight top / bottom edge with
    shaped polylines in absolute coords, left to right."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    bot = list(bottom_pts) if bottom_pts else [(x0, z0), (x1, z0)]
    top = (list(reversed(top_pts)) if top_pts
           else [(x1, z1), (x0, z1)])
    sides = (bot, [bot[-1], top[0]], top, [top[-1], bot[0]])

    def seg_normal(a, b):
        tx, tz = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, tz) or 1.0
        return (-tz / length, tx / length)

    def mitre(na, nb):
        d = max(1.0 + na[0] * nb[0] + na[1] * nb[1], 0.2)
        return ((na[0] + nb[0]) / d, (na[1] + nb[1]) / d)

    stations = []
    for s in range(4):
        poly = sides[s]
        prev = sides[(s - 1) % 4]
        stations.append((poly[0],
                         mitre(seg_normal(prev[-2], prev[-1]),
                               seg_normal(poly[0], poly[1])), s))
        for i in range(1, len(poly) - 1):
            stations.append((poly[i],
                             mitre(seg_normal(poly[i - 1], poly[i]),
                                   seg_normal(poly[i], poly[i + 1])), s))
    return stations


def _clip_half(poly, a, b, c):
    """Sutherland-Hodgman clip of a convex polygon [(x, z), ...] to the
    half-plane a*x + b*z <= c."""
    out = []
    n = len(poly)
    for i in range(n):
        p = poly[i]
        q = poly[(i + 1) % n]
        fp = a * p[0] + b * p[1] - c
        fq = a * q[0] + b * q[1] - c
        if fp <= 1e-12:
            out.append(p)
        if (fp < -1e-12 and fq > 1e-12) or (fp > 1e-12 and fq < -1e-12):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def _mullion_layout(pattern, w, h, bw):
    """Bar footprints for a straight-bar mullion pattern over a w x h
    opening: a list of convex polygons [(x, z), ...] in opening-local
    coords. Muntin construction: verticals run through, horizontals
    butt between them; the X pattern half-laps its falling diagonal
    around the rising one. Patterns follow the CWP Enhanced Panel
    Options specs (catalog pdf 143-144):

    GRID    -- Wood Mullion: 2 lites across, rows by the height chart
               (24/36/48 -> 2/3/4 lites high, else 5).
    MISSION -- (3) equal-width lites at the top, 1/3 of the opening
               height; plain glass below.
    PRAIRIE -- border bars leaving a 2 x 2 lite in each corner.
    X       -- corner-to-corner diagonals.

    Returns [] when the opening is too small for the pattern."""
    hb = bw / 2.0
    polys = []
    if pattern == 'GRID':
        rows = (2 if h <= inch(24.0) else 3 if h <= inch(36.0)
                else 4 if h <= inch(48.0) else 5)
        cx = w / 2.0
        if w > bw + inch(2.0):
            polys.append([(cx - hb, 0.0), (cx + hb, 0.0),
                          (cx + hb, h), (cx - hb, h)])
            spans = [(0.0, cx - hb), (cx + hb, w)]
        else:
            spans = [(0.0, w)]
        for j in range(1, rows):
            zc = h * j / rows
            if zc - hb <= inch(1.0) or zc + hb >= h - inch(1.0):
                continue
            for (xa, xb) in spans:
                polys.append([(xa, zc - hb), (xb, zc - hb),
                              (xb, zc + hb), (xa, zc + hb)])
    elif pattern == 'MISSION':
        zb0 = h - h / 3.0 - bw
        if zb0 <= inch(1.0) or w <= 3.0 * bw + inch(3.0):
            return []
        polys.append([(0.0, zb0), (w, zb0), (w, zb0 + bw), (0.0, zb0 + bw)])
        lw = (w - 2.0 * bw) / 3.0
        for i in (1, 2):
            xa = i * lw + (i - 1) * bw
            polys.append([(xa, zb0 + bw), (xa + bw, zb0 + bw),
                          (xa + bw, h), (xa, h)])
    elif pattern == 'PRAIRIE':
        m = inch(2.0)
        if w <= 2.0 * (m + bw) + inch(1.0) or h <= 2.0 * (m + bw) + inch(1.0):
            return []
        for xa in (m, w - m - bw):
            polys.append([(xa, 0.0), (xa + bw, 0.0),
                          (xa + bw, h), (xa, h)])
        spans = [(0.0, m), (m + bw, w - m - bw), (w - m, w)]
        for za in (m, h - m - bw):
            for (xa, xb) in spans:
                polys.append([(xa, za), (xb, za), (xb, za + bw), (xa, za + bw)])
    elif pattern == 'X':
        rect = ((1.0, 0.0, w), (-1.0, 0.0, 0.0), (0.0, 1.0, h),
                (0.0, -1.0, 0.0))

        def strip_quad(p0, p1):
            dx, dz = p1[0] - p0[0], p1[1] - p0[1]
            length = math.hypot(dx, dz)
            if length <= 1e-9:
                return None
            nx, nz = -dz / length, dx / length
            poly = [(p0[0] + nx * hb, p0[1] + nz * hb),
                    (p1[0] + nx * hb, p1[1] + nz * hb),
                    (p1[0] - nx * hb, p1[1] - nz * hb),
                    (p0[0] - nx * hb, p0[1] - nz * hb)]
            for (a, b, c) in rect:
                poly = _clip_half(poly, a, b, c)
                if len(poly) < 3:
                    return None
            return poly

        rising = strip_quad((0.0, 0.0), (w, h))
        falling = strip_quad((0.0, h), (w, 0.0))
        if rising:
            polys.append(rising)
        if falling and rising:
            length = math.hypot(w, h)
            nx, nz = -h / length, w / length      # rising centerline normal
            for pc in (_clip_half(falling, nx, nz, -hb),
                       _clip_half(falling, -nx, -nz, -hb)):
                if len(pc) >= 3:
                    polys.append(pc)
        elif falling:
            polys.append(falling)
    return polys


def _emit_prism(verts, faces, slots, poly, x_off, z_off, z_front, z_back,
                slot):
    """Planar polygon in cell-local (x, z) coords as a prism between
    two depth planes (mesh space, front cap toward +z). Winding is
    normalized from the polygon's signed area, so callers can pass
    loops in either order. Skips degenerate polygons."""
    pts = [(z_off + pz, -(x_off + px)) for (px, pz) in poly]
    n = len(pts)
    if n < 3:
        return
    area = sum(pts[i][0] * pts[(i + 1) % n][1]
               - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    if abs(area) < 1e-10:
        return
    if area < 0.0:
        pts.reverse()
    base = len(verts)
    for (mx, my) in pts:
        verts.append((mx, my, z_front))
    for (mx, my) in pts:
        verts.append((mx, my, z_back))
    faces.append(tuple(base + i for i in range(n)))
    slots.append(slot)
    faces.append(tuple(base + n + (n - 1 - i) for i in range(n)))
    slots.append(slot)
    for i in range(n):
        j = (i + 1) % n
        faces.append((base + i, base + n + i, base + n + j, base + j))
        slots.append(slot)


def _curve_clip_planes(pts, x_off, z_off, below):
    """Half-plane (a, b, c) triples for _clip_half keeping the region
    below (or above) a shaped-edge polyline, cell-local coords. Chord
    half-planes under-fill slightly where the curve is convex -- bars
    end a hair short instead of poking through the rail."""
    planes = []
    for i in range(len(pts) - 1):
        px, pz = pts[i][0] - x_off, pts[i][1] - z_off
        qx, qz = pts[i + 1][0] - x_off, pts[i + 1][1] - z_off
        a = -(qz - pz)
        b = qx - px
        c = a * px + b * pz
        if not below:
            a, b, c = -a, -b, -c
        planes.append((a, b, c))
    return planes


def _emit_shaped_panel(verts, faces, slots, part, thickness, top_pts,
                       bottom_pts):
    """Flat panel for a shaped cell: the front-face outline with its
    top / bottom edge following the shaped curve, extruded through the
    panel thickness at the part's y_inset."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    th = thickness if part['thickness'] is None else part['thickness']
    zf = thickness - part['y_inset']
    zb = zf - th
    if zb < -1e-9:
        zb = 0.0
    loop = list(bottom_pts) if bottom_pts else [(x0, z0), (x1, z0)]
    loop += list(reversed(top_pts)) if top_pts else [(x1, z1), (x0, z1)]
    out = []
    for p in loop:
        if not out or abs(p[0] - out[-1][0]) > 1e-9 \
                or abs(p[1] - out[-1][1]) > 1e-9:
            out.append(p)
    _emit_prism(verts, faces, slots, out, 0.0, 0.0, zf, zb, 2)
    return True


def _emit_mullion_bars(verts, faces, slots, part, thickness, spec,
                       top_pts=None, bottom_pts=None):
    """Mullion bars over a glass opening cell: each _mullion_layout
    polygon becomes a prism from the door's front face back to the
    glass plane (spec['depth'] behind the face). Bars index the stile
    material slot; on shaped cells they are clipped under / above the
    curve. Returns False when the pattern doesn't fit or the depth is
    degenerate."""
    x_off, z_off = part['x0'], part['z0']
    w = part['x1'] - x_off
    h = part['z1'] - z_off
    depth = spec.get('depth', 0.0)
    if depth <= 1e-6 or w <= 0.0 or h <= 0.0:
        return False
    bw = spec.get('bar_width', inch(0.875))
    polys = _mullion_layout(spec.get('pattern', 'GRID'), w, h, bw)
    if not polys:
        return False
    planes = []
    if top_pts:
        planes += _curve_clip_planes(top_pts, x_off, z_off, True)
    if bottom_pts:
        planes += _curve_clip_planes(bottom_pts, x_off, z_off, False)
    z_front = thickness
    z_back = thickness - depth
    for poly in polys:
        for (a, b, c) in planes:
            poly = _clip_half(poly, a, b, c)
            if len(poly) < 3:
                break
        if len(poly) < 3:
            continue
        _emit_prism(verts, faces, slots, poly, x_off, z_off,
                    z_front, z_back, 0)
    return True


# Part keys whose boxes may carry the door's outer edge profile. Panels
# and mid members never do: a zero-width outer member exposing them to
# the outline is the butted-mirror-pair case, where the shared edge is
# not an outer edge and correctly stays square.
_OUTLINE_EDGE_KEYS = {'slab', 'left_stile', 'right_stile',
                      'top_rail', 'bottom_rail'}


def _emit_edge_profiled_box(verts, faces, slots, part, thickness, section,
                            width, height):
    """Frame member / slab box with the door's outer edge profile cut
    along the sides that lie on the door outline. One section ring per
    box corner, raised-panel style: a side on the outline offsets its
    rings inward by the section's u (a door corner where two outline
    sides meet mitres on the diagonal); an interior side keeps u = 0,
    so the cut ends in a flat silhouette that butts the neighbouring
    member's identical cut at part joints. Returns False -- the caller
    keeps the plain box -- when no side is on the outline, the section
    is too wide for the part, or the part is not a full-thickness
    front-face member."""
    if part['thickness'] is not None or part['y_inset']:
        return False
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    tol = 1e-6
    on_l = x0 <= tol
    on_r = x1 >= width - tol
    on_b = z0 <= tol
    on_t = z1 >= height - tol
    if not (on_l or on_r or on_b or on_t):
        return False
    sec = [(u, min(v, thickness)) for (u, v) in section]
    if sec[-1][1] < thickness - 1e-9:
        sec.append((sec[-1][0], thickness))
    u_max = max(u for u, v in sec)
    if u_max <= 0.0:
        return False
    if ((int(on_l) + int(on_r)) * u_max >= (x1 - x0) - tol
            or (int(on_b) + int(on_t)) * u_max >= (z1 - z0) - tol):
        return False
    corners = ((x0, z0), (x1, z0), (x1, z1), (x0, z1))
    dirs = ((1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
    gate_x = (on_l, on_r, on_r, on_l)
    gate_z = (on_b, on_b, on_t, on_t)
    n = len(sec)
    base = len(verts)
    slot = _PART_MAT_SLOT[part['key']]
    for (cx, cz), (dx, dz), sx, sz in zip(corners, dirs, gate_x, gate_z):
        for (u, v) in sec:
            verts.append((cz + (dz * u if sz else 0.0),
                          -(cx + (dx * u if sx else 0.0)),
                          thickness - v))
    for c in range(4):
        a = base + c * n
        b = base + ((c + 1) % 4) * n
        for k in range(n - 1):
            faces.append((a + k, a + k + 1, b + k + 1, b + k))
            slots.append(slot)
    # Front plate between the rings' face points, back plate between
    # their back corners.
    faces.append((base + 0 * n, base + 1 * n, base + 2 * n, base + 3 * n))
    slots.append(slot)
    faces.append((base + 3 * n + n - 1, base + 2 * n + n - 1,
                  base + 1 * n + n - 1, base + 0 * n + n - 1))
    slots.append(slot)
    return True


def _emit_shaped_rail(verts, faces, slots, part, thickness, curve_segs,
                      side, outer_section, width, height):
    """Top / bottom rail whose opening edge follows the shaped
    curve(s): a ring loop around the part perimeter -- edge-profile
    section rings at the four corners (outline gates as in
    _emit_edge_profiled_box), plain through-thickness rings at each
    curve station -- latticed ring to ring with ngon front / back
    caps. curve_segs are per-cell absolute polylines along the shaped
    edge (the edge stays flat between them, over mid stiles); side is
    'TOP' for a top rail (curve on its bottom edge) or 'BOTTOM'."""
    x0, x1 = part['x0'], part['x1']
    z0, z1 = part['z0'], part['z1']
    tol = 1e-6
    on_l = x0 <= tol
    on_r = x1 >= width - tol
    on_b = z0 <= tol
    on_t = z1 >= height - tol
    stations = []
    for seg in curve_segs:
        for (sx, sz) in seg:
            if sx <= x0 + tol or sx >= x1 - tol:
                continue
            stations.append((sx, sz))
    if not stations:
        return False
    edge_z = z0 if side == 'TOP' else z1
    peak = max(abs(sz - edge_z) for (sx, sz) in stations)
    sec = None
    if outer_section is not None:
        sec = [(u, min(v, thickness)) for (u, v) in outer_section]
        if sec[-1][1] < thickness - 1e-9:
            sec.append((sec[-1][0], thickness))
        u_max = max(u for u, v in sec)
        # The curve eats into the rail: the profile must fit the
        # material left above (below) the peak.
        if (u_max >= (z1 - z0) - peak - tol
                or (int(on_l) + int(on_r)) * u_max >= (x1 - x0) - tol):
            sec = None
    if sec is None:
        sec = [(0.0, 0.0), (0.0, thickness)]
    n = len(sec)
    slot = _PART_MAT_SLOT[part['key']]

    rings = []

    def ring_at(px, pz, ox, oz):
        base = len(verts)
        for (u, v) in sec:
            verts.append((pz + oz * u, -(px + ox * u), thickness - v))
        rings.append(base)

    corners = ((x0, z0), (x1, z0), (x1, z1), (x0, z1))
    dirs = ((1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))
    gate_x = (on_l, on_r, on_r, on_l)
    gate_z = (on_b, on_b, on_t, on_t)
    for c in range(4):
        (cx, cz), (dx, dz) = corners[c], dirs[c]
        ring_at(cx, cz,
                dx if gate_x[c] else 0.0,
                dz if gate_z[c] else 0.0)
        if c == 0 and side == 'TOP':
            for (sx, sz) in stations:
                ring_at(sx, sz, 0.0, 0.0)
        elif c == 2 and side == 'BOTTOM':
            for (sx, sz) in reversed(stations):
                ring_at(sx, sz, 0.0, 0.0)
    m = len(rings)
    for i in range(m):
        a = rings[i]
        b = rings[(i + 1) % m]
        for k in range(n - 1):
            faces.append((a + k, a + k + 1, b + k + 1, b + k))
            slots.append(slot)
    faces.append(tuple(rings))
    slots.append(slot)
    faces.append(tuple(r + n - 1 for r in reversed(rings)))
    slots.append(slot)
    return True


def build_door_mesh(mesh, info, width, height, thickness, materials=None,
                    outer_section=None, inner_section=None,
                    panel_section=None, inner_rail_section=None,
                    inner_stile_section=None, member_section=None,
                    applied_section=None, applied_scope='ALL',
                    panel_grooves=None, mullion=None, shape=None):
    """Replace ``mesh``'s geometry with the door built as static boxes
    in front-cutpart local space: the door height runs along +X from
    the bottom edge at x=0, the width along -Y (a front cutpart with
    Mirror Y set) with the door's LEFT edge at y=0 -- for a face-frame
    front that is the viewer's left, unlike the CPM_5PIECEDOOR node,
    which rendered its Left / Right stile inputs on the opposite
    sides from their names. The front face is at z=thickness; panels
    sit back from it by their y_inset and use their own thickness.

    FRAMED doors keep every member a rectangular box part (stiles full
    height, rails between) and render the inside profile as an APPLIED
    STICKING STRIP: a closed cross-section (door_profiles.
    sticking_strip) swept around each opening perimeter, mitred at the
    corners like a real applied molding, via inner_section (or
    inner_rail_section / inner_stile_section for series that run
    different strips on rails and stiles). MITERED doors pass
    member_section instead and build through build_frame_geometry.
    With ``panel_section`` (door_profiles.panel_profile_section) panels
    build as raised panels instead, falling back to the flat box per
    cell when the cell is too small for the raise; ``panel_grooves``
    (dict(style='BEAD'|'KERF', spacing=<m>), ignored when a raise is
    active) cuts vertical beadboard / kerf grooves into flat panels
    via _emit_grooved_panel. outer_section (an
    edge_profile_section / named_edge_section sweep section) cuts the
    door's outer edge profile into the members and slabs whose sides
    lie on the door outline (_emit_edge_profiled_box), falling back to
    square edges per part when the section doesn't fit.

    ``shape`` (dict(curve='ARCH'|'CROWN', double=bool, rise=<m cap>))
    arches the top opening edge -- and the bottom for the Double
    shapes -- per top/bottom-row cell: the rails' opening edges follow
    the curve (_emit_shaped_rail), flat panels become shaped prisms,
    raised panels and sticking strips sweep the curved perimeter, and
    mullion bars clip under it. The caller widens the shaped rails by
    the peak rise so the catalog rail width survives at the crest.

    ``materials`` is an optional (stile, rail, panel) triple assigned
    as the mesh's material slots; face material indices are set either
    way (mid stiles index as stiles, mid rails as rails). Zero-size
    members (e.g. a per-side stile width of 0.0) are skipped.
    """
    mitered = (member_section is not None
               and info.get('door_type') != 'SLAB')
    if mitered:
        verts, faces, face_slots = build_mitered_frame(
            info, width, height, thickness, member_section)
    else:
        verts = []
        faces = []
        face_slots = []
    parts = evaluate_layout(info, width, height)
    # Shaped (arched) top / bottom opening edges: one curve per cell in
    # the top row (and bottom row for the Double shapes), the rails'
    # opening edges following the same polylines. shape['rise'] caps
    # the rise at the band the caller widened the rail by.
    shaped_top = {}
    shaped_bottom = {}
    top_rail_segs = []
    bottom_rail_segs = []
    if (shape is not None and not mitered
            and info.get('door_type') != 'SLAB'):
        curve = shape.get('curve', 'ARCH')
        cap = shape.get('rise')
        panels = [p for p in parts if p['key'] == 'panel'
                  and p['x1'] > p['x0'] and p['z1'] > p['z0']]
        rows = []
        if panels:
            z_top = max(p['z1'] for p in panels)
            rows.append(('top', [p for p in panels
                                 if abs(p['z1'] - z_top) < 1e-6]))
            if shape.get('double'):
                z_bot = min(p['z0'] for p in panels)
                rows.append(('bottom', [p for p in panels
                                        if abs(p['z0'] - z_bot) < 1e-6]))
        for where, row in rows:
            for p in sorted(row, key=lambda q: q['x0']):
                w = p['x1'] - p['x0']
                rise = shape_rise(curve, w)
                if cap is not None:
                    rise = min(rise, cap)
                c = _shape_curve_pts(curve, w, rise)
                if not c:
                    continue
                if where == 'top':
                    pts = [(p['x0'] + x, p['z1'] + r) for (x, r) in c]
                    shaped_top[id(p)] = pts
                    top_rail_segs.append(pts)
                else:
                    pts = [(p['x0'] + x, p['z0'] - r) for (x, r) in c]
                    shaped_bottom[id(p)] = pts
                    bottom_rail_segs.append(pts)
    cells = []
    for part in parts:
        if mitered and part['key'] != 'panel':
            continue
        if part['x1'] - part['x0'] <= 0.0 or part['z1'] - part['z0'] <= 0.0:
            continue
        if part['key'] == 'panel':
            cells.append(part)
        t_pts = shaped_top.get(id(part))
        b_pts = shaped_bottom.get(id(part))
        if (part['key'] == 'panel' and panel_section is not None
                and _emit_raised_panel(verts, faces, face_slots, part,
                                       thickness, panel_section,
                                       t_pts, b_pts)):
            continue
        if (part['key'] == 'panel' and panel_section is None
                and panel_grooves is not None
                and not t_pts and not b_pts
                and _emit_grooved_panel(verts, faces, face_slots, part,
                                        thickness, panel_grooves)):
            continue
        # Shaped flat cell (grooved kinds fall back here too -- the
        # groove prism can't take a curved top yet).
        if (part['key'] == 'panel' and (t_pts or b_pts)
                and _emit_shaped_panel(verts, faces, face_slots, part,
                                       thickness, t_pts, b_pts)):
            continue
        if (part['key'] == 'top_rail' and top_rail_segs
                and _emit_shaped_rail(verts, faces, face_slots, part,
                                      thickness, top_rail_segs, 'TOP',
                                      outer_section, width, height)):
            continue
        if (part['key'] == 'bottom_rail' and bottom_rail_segs
                and _emit_shaped_rail(verts, faces, face_slots, part,
                                      thickness, bottom_rail_segs, 'BOTTOM',
                                      outer_section, width, height)):
            continue
        if (outer_section is not None and not mitered
                and part['key'] in _OUTLINE_EDGE_KEYS
                and _emit_edge_profiled_box(verts, faces, face_slots, part,
                                            thickness, outer_section,
                                            width, height)):
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
    # Applied sticking strips: members stay rectangular parts; the
    # inside profile sweeps each opening perimeter as its own molding
    # loop seated against them.
    if (not mitered and info.get('door_type') != 'SLAB'
            and (inner_section is not None
                 or inner_rail_section is not None
                 or inner_stile_section is not None)):
        lr = inner_rail_section or inner_section or inner_stile_section
        ls = inner_stile_section or inner_section or inner_rail_section
        for part in cells:
            _emit_strip_rings(verts, faces, face_slots, part, thickness,
                              lr, ls,
                              top_pts=shaped_top.get(id(part)),
                              bottom_pts=shaped_bottom.get(id(part)))
    # Applied decorative molding: another loop around each opening,
    # seated proud on the door face (door_profiles.applied_strip).
    if (not mitered and info.get('door_type') != 'SLAB'
            and applied_section is not None):
        for part in cells:
            _emit_strip_rings(verts, faces, face_slots, part, thickness,
                              applied_section, applied_section,
                              scope=applied_scope)
    # Mullion bars over glass openings (dict(pattern=..., bar_width=,
    # depth=) -- see _mullion_layout / _emit_mullion_bars). Independent
    # of the frame construction, so mitered doors get them too.
    if info.get('door_type') != 'SLAB' and mullion is not None:
        for part in cells:
            _emit_mullion_bars(verts, faces, face_slots, part, thickness,
                               mullion,
                               top_pts=shaped_top.get(id(part)),
                               bottom_pts=shaped_bottom.get(id(part)))
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
