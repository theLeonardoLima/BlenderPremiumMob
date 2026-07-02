"""Declarative closet starter catalog.

One entry per library item. The class name resolves through
types_closets.CLOSET_NAME_DISPATCH; per-type geometry defaults live as
class attributes on the starter classes (face_frame pattern). This module
stays import-light (no bpy) so the solver/types can be smoke-reloaded.
"""

# Order here is the order the library UI lists the starters.
STARTER_MENU_ENTRIES = [
    ('Base', "Base Starter", "Floor-mounted base closet starter"),
    ('Tall', "Tall Starter", "Floor-mounted full-height closet starter"),
    ('Hanging', "Hanging Starter", "Wall-mounted hanging closet starter"),
    ('Island', "Island Starter", "Single-sided closet island with countertop and applied back"),
    ('Island Double', "Island Double Starter", "Double-sided closet island with center back, accessible from both faces"),
]

# Bay-level override defaults, mirrored by Closet_Bay_Props. Kept as data
# so a Phase 2 "Change Bay" style mechanism can reset overrides the same
# way face_frame's BAY_PROPS does.
BAY_PROP_DEFAULTS = {
    'width_locked': False,
    'remove_bottom': False,
    'remove_cleat': False,
}
