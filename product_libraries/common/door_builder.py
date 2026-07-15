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
    min_h = 2.0 * rw
    if info.get('add_mid_rail'):
        min_h += max(info['mid_rail_width'], inch(0.5))
    return 2.0 * sw + inch(0.5), min_h + inch(0.5)


def door_layout(info):
    """Part rects for one door in door-local space: x across from the
    left edge, z up from the bottom edge. Returns a list of dicts:

      key       -- 'slab' / 'left_stile' / 'right_stile' / 'top_rail' /
                   'bottom_rail' / 'mid_rail' / 'panel' ('panel_bottom' /
                   'panel_top' around a mid rail)
      name      -- display name ("Left Stile", ...)
      x, w      -- (coef, offset) against the door width
      z, h      -- (coef, offset) against the door height
      thickness -- None = the caller's door thickness (frame members /
                   slab); a float for the thinner panel
      y_inset   -- setback of the part's front face from the door's
                   front face (panels; 0 for frame members)
    """
    if info.get('door_type') == 'SLAB':
        return [dict(key='slab', name="Slab", x=(0.0, 0.0), w=(1.0, 0.0),
                     z=(0.0, 0.0), h=(1.0, 0.0), thickness=None,
                     y_inset=0.0)]
    sw = max(info['stile_width'], inch(0.5))
    rw = max(info['rail_width'], inch(0.5))
    p_th = max(info['panel_thickness'], inch(0.125))
    p_in = max(info['panel_inset'], 0.0)
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
    if info.get('add_mid_rail'):
        mrw = max(info['mid_rail_width'], inch(0.5))
        if info.get('center_mid_rail', True):
            mz = (0.5, -mrw / 2.0)
        else:
            mz = (0.0, max(info['mid_rail_location'], rw))
        parts.append(dict(key='mid_rail', name="Mid Rail", x=(0.0, sw),
                          w=(1.0, -2.0 * sw), z=mz, h=(0.0, mrw),
                          thickness=None, y_inset=0.0))
        parts.append(dict(key='panel_bottom', name="Bottom Panel",
                          x=(0.0, sw), w=(1.0, -2.0 * sw),
                          z=(0.0, rw), h=(mz[0], mz[1] - rw),
                          thickness=p_th, y_inset=p_in))
        parts.append(dict(key='panel_top', name="Top Panel",
                          x=(0.0, sw), w=(1.0, -2.0 * sw),
                          z=(mz[0], mz[1] + mrw),
                          h=(1.0 - mz[0], -rw - mz[1] - mrw),
                          thickness=p_th, y_inset=p_in))
    else:
        parts.append(dict(key='panel', name="Panel", x=(0.0, sw),
                          w=(1.0, -2.0 * sw), z=(0.0, rw),
                          h=(1.0, -2.0 * rw), thickness=p_th, y_inset=p_in))
    return parts
