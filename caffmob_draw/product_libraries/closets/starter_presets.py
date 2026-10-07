"""Declarative closet starter catalog.

One entry per library item. The class name resolves through
types_closets.CLOSET_NAME_DISPATCH; per-type geometry defaults live as
class attributes on the starter classes (face_frame pattern). This module
stays import-light (no bpy) so the solver/types can be smoke-reloaded.
"""

from ...data.i18n import N_

# Library sections: (section label, [(catalog name, button label, desc)]).
# The library UI draws one collapsible-free header row per section.
STARTER_SECTIONS = [
    (N_("Closets"), [
        ('Base', N_("Base"), N_("Floor-mounted base closet starter")),
        ('Tall', N_("Tall"), N_("Floor-mounted full-height closet starter")),
        ('Hanging', N_("Hanging"), N_("Wall-mounted hanging closet starter")),
    ]),
    (N_("L Shelves"), [
        ('L Shelf Base', N_("Base"), N_("Floor-mounted corner L-shelf unit")),
        ('L Shelf Tall', N_("Tall"), N_("Floor-mounted full-height corner L-shelf unit")),
        ('L Shelf Upper', N_("Hanging"), N_("Wall-mounted corner L-shelf unit")),
    ]),
    (N_("Islands"), [
        ('Island', N_("Single"), N_("Single-sided island with countertop and applied back")),
        ('Island Double', N_("Double"), N_("Double-sided island with center back")),
    ]),
]

# Flat list retained for anything iterating the whole catalog
# (thumbnail checks etc.).
STARTER_MENU_ENTRIES = [entry for _sec, entries in STARTER_SECTIONS
                        for entry in entries]

# Bay-level override defaults, mirrored by Closet_Bay_Props. Kept as
# data so Change Bay-style mechanisms can reset overrides the same way
# face_frame's BAY_PROPS does.
BAY_PROP_DEFAULTS = {
    'width_locked': False,
    'remove_bottom': False,
    'remove_cleat': False,
}
