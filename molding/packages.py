"""Shipped molding package presets and built-in placeholder profiles.

A package is a named STACK of moldings: each entry is
(profile_key, forward_offset, vertical_offset). Stacks let one package
build layered setups - a flat-stock spacer with a crown on top, or a
furniture cap - without any per-cabinet configuration.

Profiles here are code-generated placeholder cross-sections so the
system works end to end; they are meant to be superseded by curated
profile assets in the molding library (a stack entry can then name a
library profile instead of a built-in key).
"""

import bpy

from .. import units


def _in(v):
    return units.inch(v)


# (identifier, label, description, stack)
CROWN_PACKAGES = [
    ('SIMPLE', "Simple Crown",
     "One crown profile along the cabinet tops",
     [('crown_simple', 0.0, 0.0)]),
    ('STACKED', "Stacked w/ Spacer",
     "Flat-stock spacer with a crown profile on top",
     [('flat_stock', 0.0, 0.0),
      ('crown_simple', 0.0, _in(3.5))]),
    ('FURNITURE', "Furniture Cap",
     "A flat furniture cap overhanging the cabinet tops",
     [('furniture_cap', 0.0, 0.0)]),
]

BASE_PACKAGES = [
    ('SIMPLE', "Simple Base",
     "One base profile along the toe kicks",
     [('base_simple', 0.0, 0.0)]),
]

LIGHT_RAIL_PACKAGES = [
    ('SIMPLE', "Simple Light Rail",
     "One light-rail profile under the upper cabinet fronts",
     [('light_rail_simple', 0.0, 0.0)]),
]

PACKAGES = {
    'CROWN': CROWN_PACKAGES,
    'BASE': BASE_PACKAGES,
    'LIGHT_RAIL': LIGHT_RAIL_PACKAGES,
}


def package_stack(molding_type, identifier):
    for ident, _label, _desc, stack in PACKAGES[molding_type]:
        if ident == identifier:
            return stack
    return None


# Enum item lists are cached at module level: Blender keeps only weak
# references to dynamic enum strings, so the lists handed to the
# property callbacks must stay alive.
_ENUM_CACHE = {}
for _mtype, _pkgs in PACKAGES.items():
    _ENUM_CACHE[_mtype] = tuple(
        [('NONE', "None", "No molding")]
        + [(ident, label, desc) for ident, label, desc, _stack in _pkgs])


def enum_items(molding_type):
    return _ENUM_CACHE[molding_type]


# ---------------------------------------------------------------------------
# Built-in placeholder profiles
# ---------------------------------------------------------------------------
# Closed 2D outlines in profile-local coordinates: +Y is up along the
# cabinet face, X is the depth direction (negative back toward the
# cabinet). Authored so the outline sits against the swept path line;
# swap for curated profile assets without touching the sweep code.

_PROFILE_OUTLINES = {
    # Sprung crown look-alike: rises above the top line, leaning back.
    'crown_simple': [
        (0.0, 0.0), (0.0, _in(0.5)), (-_in(0.125), _in(0.75)),
        (-_in(0.625), _in(2.5)), (-_in(0.75), _in(2.75)),
        (-_in(0.75), _in(3.0)), (-_in(0.875), _in(3.0)),
        (-_in(0.875), 0.0),
    ],
    # 1x4 flat stock spacer.
    'flat_stock': [
        (0.0, 0.0), (0.0, _in(3.5)),
        (-_in(0.75), _in(3.5)), (-_in(0.75), 0.0),
    ],
    # Flat cap slab with a nose overhanging the face.
    'furniture_cap': [
        (_in(0.375), 0.0), (_in(0.375), _in(1.0)),
        (-_in(0.75), _in(1.0)), (-_in(0.75), 0.0),
    ],
    # Base profile: flat stock with an eased top edge.
    'base_simple': [
        (0.0, 0.0), (0.0, _in(2.5)), (-_in(0.25), _in(3.0)),
        (-_in(0.625), _in(3.0)), (-_in(0.625), 0.0),
    ],
    # Light rail hanging below the upper's bottom line.
    'light_rail_simple': [
        (0.0, 0.0), (0.0, -_in(1.25)), (-_in(0.25), -_in(1.5)),
        (-_in(0.75), -_in(1.5)), (-_in(0.75), 0.0),
    ],
}


def make_profile_object(profile_key, name, collection):
    """Create a hidden closed-poly curve object for `profile_key` to be
    used as a sweep's bevel_object. Returns None for unknown keys."""
    outline = _PROFILE_OUTLINES.get(profile_key)
    if outline is None:
        return None
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '2D'
    curve.fill_mode = 'NONE'
    spline = curve.splines.new('POLY')
    spline.points.add(len(outline) - 1)
    for pt, (x, y) in zip(spline.points, outline):
        pt.co = (x, y, 0.0, 1.0)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.hide_viewport = True
    obj.hide_render = True
    obj['IS_HB_MOLDING_PROFILE'] = True
    return obj
