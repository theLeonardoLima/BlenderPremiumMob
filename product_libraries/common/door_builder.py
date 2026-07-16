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
evaluates the pairs; a driven builder (the wood hood) composes them into
driver expressions so the parts track their cage.
"""

from ...units import inch


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
}


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
    sw = max(info['stile_width'], inch(0.5))
    rw = max(info['rail_width'], inch(0.5))
    mrw = max(info['mid_rail_width'], inch(0.5))
    k = max(int(info.get('mid_rail_count', 0) or 0), 0)
    if k == 0 and info.get('add_mid_rail'):
        k = 1
    m = max(int(info.get('mid_stile_count', 0) or 0), 0)
    return (2.0 + m) * sw + inch(0.5), 2.0 * rw + k * mrw + inch(0.5)


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
    add_mid_rail when > 0; mid stiles use the outer stile width.
    """
    if info.get('door_type') == 'SLAB':
        return [dict(key='slab', name="Slab", x=(0.0, 0.0), w=(1.0, 0.0),
                     z=(0.0, 0.0), h=(1.0, 0.0), thickness=None,
                     y_inset=0.0)]
    sw = max(info['stile_width'], inch(0.5))
    rw = max(info['rail_width'], inch(0.5))
    mrw = max(info['mid_rail_width'], inch(0.5))
    p_th = max(info['panel_thickness'], inch(0.125))
    p_in = max(info['panel_inset'], 0.0)
    k = max(int(info.get('mid_rail_count', 0) or 0), 0)
    m = max(int(info.get('mid_stile_count', 0) or 0), 0)
    parts = [
        dict(key='left_stile', name="Left Stile", x=(0.0, 0.0), w=(0.0, sw),
             z=(0.0, 0.0), h=(1.0, 0.0), thickness=None, y_inset=0.0),
        dict(key='right_stile', name="Right Stile", x=(1.0, -sw), w=(0.0, sw),
             z=(0.0, 0.0), h=(1.0, 0.0), thickness=None, y_inset=0.0),
        dict(key='bottom_rail', name="Bottom Rail", x=(0.0, sw),
             w=(1.0, -2.0 * sw), z=(0.0, 0.0), h=(0.0, rw),
             thickness=None, y_inset=0.0),
        dict(key='top_rail', name="Top Rail", x=(0.0, sw),
             w=(1.0, -2.0 * sw), z=(1.0, -rw), h=(0.0, rw),
             thickness=None, y_inset=0.0),
    ]
    # Panel rows as (z, h) linear pairs, with the mid rails between them.
    if k > 0:
        fh = (1.0, -(2.0 * rw + k * mrw))     # field height, linear in H
        rows = [((fh[0] * i / (k + 1), fh[1] * i / (k + 1) + rw + i * mrw),
                 (fh[0] / (k + 1), fh[1] / (k + 1)))
                for i in range(k + 1)]
        for i in range(1, k + 1):
            parts.append(dict(
                key='mid_rail',
                name="Mid Rail %d" % i if k > 1 else "Mid Rail",
                x=(0.0, sw), w=(1.0, -2.0 * sw),
                z=(fh[0] * i / (k + 1),
                   fh[1] * i / (k + 1) + rw + (i - 1) * mrw),
                h=(0.0, mrw), thickness=None, y_inset=0.0))
    elif info.get('add_mid_rail'):
        # Legacy single mid rail, centered or at a fixed location.
        if info.get('center_mid_rail', True):
            mz = (0.5, -mrw / 2.0)
        else:
            mz = (0.0, max(info['mid_rail_location'], rw))
        parts.append(dict(key='mid_rail', name="Mid Rail", x=(0.0, sw),
                          w=(1.0, -2.0 * sw), z=mz, h=(0.0, mrw),
                          thickness=None, y_inset=0.0))
        rows = [((0.0, rw), (mz[0], mz[1] - rw)),
                ((mz[0], mz[1] + mrw), (1.0 - mz[0], -rw - mz[1] - mrw))]
    else:
        rows = [((0.0, rw), (1.0, -2.0 * rw))]
    # Panel columns as (x, w) linear pairs; mid stiles between them,
    # one set per row (they butt the rails).
    if m > 0:
        cw = (1.0 / (m + 1), -(2.0 * sw + m * sw) / (m + 1))
        cols = [((c * cw[0], c * (cw[1] + sw) + sw), cw)
                for c in range(m + 1)]
    else:
        cols = [((0.0, sw), (1.0, -2.0 * sw))]
    grid = len(rows) > 1 or len(cols) > 1
    for r, (rz, rh) in enumerate(rows):
        for j in range(1, m + 1):
            name = ("Mid Stile %d-%d" % (r + 1, j) if len(rows) > 1
                    else ("Mid Stile %d" % j if m > 1 else "Mid Stile"))
            parts.append(dict(key='mid_stile', name=name,
                              x=(j * cw[0], j * (cw[1] + sw)),
                              w=(0.0, sw), z=rz, h=rh,
                              thickness=None, y_inset=0.0))
        for c, (cx, cwid) in enumerate(cols):
            name = "Panel %d-%d" % (r + 1, c + 1) if grid else "Panel"
            parts.append(dict(key='panel', name=name, x=cx, w=cwid,
                              z=rz, h=rh, thickness=p_th, y_inset=p_in))
    return parts
