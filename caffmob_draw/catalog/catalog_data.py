"""Catalog data: every browseable item across the entire HB5 library.

Each entry is a plain Python dict (intentionally simple - this is data,
not Blender properties). The browser UI mirrors entries into a Scene
CollectionProperty so Blender's UIList can iterate them.

KIND values drive the action verb shown in list-view detail cards:
    'product' - placeable in the scene  -> "Place at cursor"

Door styles, finishes, end conditions, and other per-cabinet
configurations are intentionally NOT in this catalog. They are
modifications applied to an existing cabinet via its Style Section /
right-click properties popup, not items to "place" from a library.

Inserts (rollouts, trash, dividers) are likewise NOT in this catalog.
They are placed via right-click on a face-frame bay, not from this
browse-and-place library.
"""

from ..data.i18n import N_

# Contexto de tradução dos nomes e descrições dos itens: o nome também é o id do item e pode ser uma palavra genérica
# ("Range"), que não pode mudar a tradução do resto do Blender (BUG-20261007-FLZO).
TEXT_CTXT = "caffmob_catalogo"

KIND_VERBS = {
    'product': N_('Place at cursor'),
}

KIND_ICONS = {
    'product': 'MESH_CUBE',
}


def _ff(cabinet_name, bay_qty=1):
    """Helper for face-frame cabinet entries that all share the same operator."""
    return {
        'action_operator': 'caffmob_face_frame.draw_cabinet',
        'action_args': {'cabinet_name': cabinet_name, 'bay_qty': bay_qty},
    }


def _todo(label):
    """Helper for catalog entries whose real operator hasn't been built yet."""
    return {
        'action_operator': 'caffmob_catalog.not_yet_implemented',
        'action_args': {'item_name': label},
    }


def _e(category, name, description, action, tags=None):
    """Build a catalog entry from compact data.

    The id is auto-derived from category + name (sanitised). Adding a
    new entry is one line at the call site below.
    """
    sanitised = (
        name.lower()
        .replace(' ', '_')
        .replace('-', '')
        .replace('?', '')
        .replace('(', '')
        .replace(')', '')
        .replace('/', '_')
        .replace(',', '')
    )
    while '__' in sanitised:
        sanitised = sanitised.replace('__', '_')
    sanitised = sanitised.strip('_')
    item_id = category.replace('/', '_') + '_' + sanitised
    return {
        'id': item_id,
        'code': '',
        'name': name,
        'description': description,
        'kind': 'product',
        'category': category,
        'tags': list(tags or []),
        'thumbnail': '',
        **action,
    }


CATALOG = [
    # =======================================================================
    # Standard cabinets
    # =======================================================================
    _e('standard', N_('Base'),
       N_('Standard 1-door 1-drawer base cabinet.'),
       _ff('Base Door'), tags=['base', 'standard']),
    _e('standard', N_('Tall'),
       N_('Tall pantry, oven, broom, or refrigerator surround.'),
       _ff('Tall'), tags=['tall', 'pantry']),
    _e('standard', N_('Upper'),
       N_('Standard wall cabinet.'),
       _ff('Upper'), tags=['wall', 'upper']),
    _e('standard', N_('Upper Stacked'),
       N_('Wall cabinet with stacked door configuration.'),
       _ff('Upper Stacked'), tags=['wall', 'stacked']),
    _e('standard', N_('Lap Drawer'),
       N_('Lap drawer cabinet.'),
       _ff('Lap Drawer'), tags=['drawer', 'lap']),
    _e('standard', N_('Floating Base Cabinet'),
       N_('Floating base cabinet (no toe kick).'),
       _todo('Floating Base Cabinet'), tags=['base', 'floating']),

    # =======================================================================
    # Corner cabinets
    # =======================================================================
    _e('corner', N_('Pie Cut Door - Left Opens First'),
       N_('Pie cut corner; left door opens first.'),
       _todo('Pie Cut Door (Left Opens First)'), tags=['pie cut', 'corner']),
    _e('corner', N_('Pie Cut Door - Bi-fold'),
       N_('Pie cut corner with bi-fold doors.'),
       _todo('Pie Cut Door (Bi-fold)'), tags=['pie cut', 'bi-fold']),
    _e('corner', N_('Pie Cut Door - Tray Compartment'),
       N_('Pie cut corner with tray compartment.'),
       _todo('Pie Cut Door (Tray Compartment)'), tags=['pie cut', 'tray']),
    _e('corner', N_('Diagonal'),
       N_('Diagonal corner cabinet.'),
       _todo('Diagonal corner'), tags=['diagonal', 'corner']),
    _e('corner', N_('Diagonal Sink - Full Height Doors'),
       N_('Diagonal sink corner with full-height doors.'),
       _todo('Diagonal Sink (Full Height Doors)'), tags=['diagonal', 'sink']),
    _e('corner', N_('Diagonal Sink - Standard with False Front'),
       N_('Diagonal sink corner, standard configuration with false drawer front.'),
       _todo('Diagonal Sink (Standard, False Front)'), tags=['diagonal', 'sink', 'false front']),
    _e('corner', N_('Pie Cut Drawer - 2'),
       N_('Pie cut corner with 2 drawers.'),
       _todo('Pie Cut Drawer (2)'), tags=['pie cut', 'drawer']),
    _e('corner', N_('Pie Cut Drawer - 3'),
       N_('Pie cut corner with 3 drawers.'),
       _todo('Pie Cut Drawer (3)'), tags=['pie cut', 'drawer']),
    _e('corner', N_('Pie Cut Drawer - 4'),
       N_('Pie cut corner with 4 drawers.'),
       _todo('Pie Cut Drawer (4)'), tags=['pie cut', 'drawer']),

    # =======================================================================
    # Appliance products
    # =======================================================================
    _e('appliance', N_('Elevated Dishwasher - Standard'),
       N_('Elevated dishwasher cabinet, standard.'),
       _todo('Elevated Dishwasher (Standard)'), tags=['dishwasher', 'elevated']),
    _e('appliance', N_('Elevated Dishwasher - With Drawer'),
       N_('Elevated dishwasher cabinet with drawer.'),
       _todo('Elevated Dishwasher (With Drawer)'), tags=['dishwasher', 'elevated', 'drawer']),
    _e('appliance', N_('Dishwasher'),
       N_('Dishwasher cabinet.'),
       _todo('Dishwasher cabinet'), tags=['dishwasher']),
    _e('appliance', N_('Single Oven'),
       N_('Single oven cabinet.'),
       _todo('Single Oven cabinet'), tags=['oven', 'single']),
    _e('appliance', N_('Double Oven'),
       N_('Double oven cabinet.'),
       _todo('Double Oven cabinet'), tags=['oven', 'double']),
    _e('appliance', N_('Microwave'),
       N_('Microwave cabinet.'),
       _todo('Microwave cabinet'), tags=['microwave']),
    _e('appliance', N_('Microwave and Oven'),
       N_('Combined microwave and oven cabinet.'),
       _todo('Microwave and Oven'), tags=['oven', 'microwave']),
    _e('appliance', N_('Refrigerator - Integrated Legs'),
       N_('Refrigerator surround with integrated legs.'),
       _todo('Refrigerator (Integrated Legs)'), tags=['refrigerator', 'legs']),
    _e('appliance', N_('Refrigerator - Stile (in lieu of leg)'),
       N_('Refrigerator surround with stile in lieu of leg.'),
       _todo('Refrigerator (Stile)'), tags=['refrigerator', 'stile']),
    _e('appliance', N_('Refrigerator Columns'),
       N_('Refrigerator columns.'),
       _todo('Refrigerator Columns'), tags=['refrigerator', 'columns']),
    _e('appliance', N_('Refrigerator Pilasters?'),
       N_('Refrigerator pilasters - confirm before placing.'),
       _todo('Refrigerator Pilasters'), tags=['refrigerator', 'pilasters']),
    _e('appliance', N_('Step-back Surround Set'),
       N_('Step-back refrigerator surround set.'),
       _todo('Step-back Surround Set'), tags=['refrigerator', 'surround']),
    _e('appliance', N_('Range'),
       N_('Range cabinet.'),
       _todo('Range cabinet'), tags=['range']),
    _e('appliance', N_('Standalone Refrigerator?'),
       N_('Standalone refrigerator placeholder - confirm before placing.'),
       _todo('Standalone Refrigerator'), tags=['refrigerator', 'standalone']),

    # =======================================================================
    # Vanities
    # =======================================================================
    _e('vanity', N_('Vanity Special'),
       N_('Special vanity cabinet.'),
       _todo('Vanity Special'), tags=['vanity']),
    _e('vanity', N_('Vanity Combination'),
       N_('Combination vanity cabinet.'),
       _todo('Vanity Combination'), tags=['vanity']),
    _e('vanity', N_('Vanity Deluxe'),
       N_('Deluxe vanity cabinet.'),
       _todo('Vanity Deluxe'), tags=['vanity']),

    # =======================================================================
    # Parts
    # =======================================================================
    _e('parts', N_('Leg Product'),
       N_('Face-frame leg / post / filler. Loose-stile, end-leg, and '
       'intermediate-leg behaviour are all options on its prompts '
       '(Finish Type / Only Stile).'),
       _ff('Leg Product'), tags=['leg', 'stile', 'end']),
    _e('parts', N_('Vanity End Leg Assembly'),
       N_('Vanity end leg assembly.'),
       _todo('Vanity End Leg Assembly'), tags=['vanity', 'leg']),
    _e('parts', N_('Vanity Support Leg - Square'),
       N_('Square vanity support leg.'),
       _todo('Vanity Support Leg (Square)'), tags=['vanity', 'leg', 'square']),
    _e('parts', N_('Vanity Support Leg - Curved'),
       N_('Curved vanity support leg.'),
       _todo('Vanity Support Leg (Curved)'), tags=['vanity', 'leg', 'curved']),
    _e('parts', N_('Vanity Fixed Shelf - Finished'),
       N_('Finished vanity fixed shelf.'),
       _todo('Vanity Fixed Shelf (Finished)'), tags=['vanity', 'shelf']),
    _e('parts', N_('Vanity Fixed Shelf - Slotted'),
       N_('Slotted vanity fixed shelf.'),
       _todo('Vanity Fixed Shelf (Slotted)'), tags=['vanity', 'shelf', 'slotted']),
    _e('parts', N_('Floating Shelves'),
       N_('Wall-mounted floating shelf.'),
       _ff('Floating Shelves'), tags=['shelf', 'floating']),
    _e('parts', N_('Shelf - Non-Floating'),
       N_('Non-floating shelf.'),
       _todo('Non-Floating Shelf'), tags=['shelf']),
    _e('parts', N_('Shelf - Heavy Duty'),
       N_('Heavy duty shelf.'),
       _todo('Heavy Duty Shelf'), tags=['shelf', 'heavy duty']),

    # =======================================================================
    # Specialty
    # =======================================================================
    _e('specialty', N_('Recessed Medicine Cabinet'),
       N_('Recessed medicine cabinet.'),
       _todo('Recessed Medicine Cabinet'), tags=['medicine', 'recessed']),
    _e('specialty', N_('Tri-View Medicine Cabinet'),
       N_('Tri-view medicine cabinet.'),
       _todo('Tri-View Medicine Cabinet'), tags=['medicine', 'tri-view']),
    _e('specialty', N_('Overstool - With Shelf'),
       N_('Overstool with shelf.'),
       _todo('Overstool (With Shelf)'), tags=['overstool']),
    _e('specialty', N_('Overstool - With Towel Bar'),
       N_('Overstool with towel bar.'),
       _todo('Overstool (With Towel Bar)'), tags=['overstool', 'towel bar']),
    _e('specialty', N_('Overstool - With Shelf and Towel Bar'),
       N_('Overstool with shelf and towel bar.'),
       _todo('Overstool (With Shelf and Towel Bar)'), tags=['overstool', 'shelf', 'towel bar']),
    _e('specialty', N_('Mirror Frame - Shaker'),
       N_('Shaker-style mirror frame.'),
       _todo('Mirror Frame (Shaker)'), tags=['mirror', 'shaker']),
    _e('specialty', N_('Mirror Frame - Colonial'),
       N_('Colonial-style mirror frame.'),
       _todo('Mirror Frame (Colonial)'), tags=['mirror', 'colonial']),
    _e('specialty', N_('Mirror Frame - Clover'),
       N_('Clover-style mirror frame.'),
       _todo('Mirror Frame (Clover)'), tags=['mirror', 'clover']),
    _e('specialty', N_('Mirror Frame - Gothic'),
       N_('Gothic-style mirror frame.'),
       _todo('Mirror Frame (Gothic)'), tags=['mirror', 'gothic']),
    _e('specialty', N_('Tub Skirt - Finished'),
       N_('Finished tub skirt.'),
       _todo('Tub Skirt (Finished)'), tags=['tub skirt']),
    _e('specialty', N_('Tub Skirt - Paneled'),
       N_('Paneled tub skirt.'),
       _todo('Tub Skirt (Paneled)'), tags=['tub skirt', 'paneled']),
    _e('specialty', N_('Tub Skirt - Working or Removable Door'),
       N_('Tub skirt with working or removable door.'),
       _todo('Tub Skirt (Working / Removable Door)'), tags=['tub skirt', 'door']),
    _e('specialty', N_('Tub Skirt - Removable Panels'),
       N_('Tub skirt with removable panels.'),
       _todo('Tub Skirt (Removable Panels)'), tags=['tub skirt', 'panels']),
    _e('specialty', N_('Bookcase - Standard'),
       N_('Standard bookcase.'),
       _todo('Bookcase (Standard)'), tags=['bookcase']),
    _e('specialty', N_('Bookcase - Storage Unit'),
       N_('Bookcase as a storage unit.'),
       _todo('Bookcase (Storage Unit)'), tags=['bookcase', 'storage']),
    _e('specialty', N_('Bookcase Upper - Standard'),
       N_('Standard upper bookcase.'),
       _todo('Bookcase Upper (Standard)'), tags=['bookcase', 'upper']),
    _e('specialty', N_('Bookcase Upper - Hutch'),
       N_('Hutch upper bookcase.'),
       _todo('Bookcase Upper (Hutch)'), tags=['bookcase', 'hutch']),
    _e('specialty', N_('Bookcase Corner - Hutch'),
       N_('Hutch corner bookcase.'),
       _todo('Bookcase Corner (Hutch)'), tags=['bookcase', 'corner', 'hutch']),
    _e('specialty', N_('Bookcase Corner - Storage'),
       N_('Storage corner bookcase.'),
       _todo('Bookcase Corner (Storage)'), tags=['bookcase', 'corner', 'storage']),
    _e('specialty', N_('Bookcase Corner Upper - Standard'),
       N_('Standard upper corner bookcase.'),
       _todo('Bookcase Corner Upper (Standard)'), tags=['bookcase', 'corner', 'upper']),
    _e('specialty', N_('Bookcase Corner Upper - Hutch'),
       N_('Hutch upper corner bookcase.'),
       _todo('Bookcase Corner Upper (Hutch)'), tags=['bookcase', 'corner', 'upper', 'hutch']),
    _e('specialty', N_('Window Seat - Veneer Front'),
       N_('Window seat with veneer front.'),
       _todo('Window Seat (Veneer Front)'), tags=['window seat']),
    _e('specialty', N_('Window Seat - Paneled Front'),
       N_('Window seat with paneled front.'),
       _todo('Window Seat (Paneled Front)'), tags=['window seat', 'paneled']),
    _e('specialty', N_('Window Seat - With Doors'),
       N_('Window seat with doors.'),
       _todo('Window Seat (With Doors)'), tags=['window seat', 'doors']),
    _e('specialty', N_('Window Seat - With Drawers'),
       N_('Window seat with drawers.'),
       _todo('Window Seat (With Drawers)'), tags=['window seat', 'drawers']),
    _e('specialty', N_('Window Seat - Hinged Lid?'),
       N_('Window seat with hinged lid - confirm before placing.'),
       _todo('Window Seat (Hinged Lid)'), tags=['window seat', 'lid']),
    _e('specialty', N_('Dresser - 5 Drawers'),
       N_('Dresser with 5 drawers.'),
       _todo('Dresser (5 Drawers)'), tags=['dresser', 'drawer']),
    _e('specialty', N_('Dresser - 6 Drawers'),
       N_('Dresser with 6 drawers.'),
       _todo('Dresser (6 Drawers)'), tags=['dresser', 'drawer']),
    _e('specialty', N_('Night Stand - Standard'),
       N_('Standard night stand.'),
       _todo('Night Stand (Standard)'), tags=['night stand']),
    _e('specialty', N_('Night Stand - 3 Drawer'),
       N_('3-drawer night stand.'),
       _todo('Night Stand (3 Drawer)'), tags=['night stand', 'drawer']),

    # =======================================================================
    # Angled
    # =======================================================================
    _e('angled', N_('Angled Ends with Doors'),
       N_('Angled end cabinet with doors.'),
       _todo('Angled Ends with Doors'), tags=['angled', 'ends', 'doors']),
    _e('angled', N_('Double Angled Ends'),
       N_('Double angled end cabinet.'),
       _todo('Double Angled Ends'), tags=['angled', 'ends']),
    _e('angled', N_('Angled Finished Ends'),
       N_('Angled finished end cabinet.'),
       _todo('Angled Finished Ends'), tags=['angled', 'ends', 'finished']),

    # =======================================================================
    # Misc
    # =======================================================================
    _e('misc', N_('Half Wall'),
       N_('Half wall.'),
       _todo('Half Wall'), tags=['wall']),
    _e('misc', N_('Support Frame'),
       N_('Support frame.'),
       _todo('Support Frame'), tags=['frame', 'support']),
    _e('misc', N_('Face Frame and Doors'),
       N_('Face frame and doors only (no carcass).'),
       _todo('Face Frame and Doors'), tags=['face frame', 'doors']),
    _e('misc', N_('X-Frame Ends'),
       N_('X-frame ends.'),
       _todo('X-Frame Ends'), tags=['x-frame', 'ends']),
]


def find_entry(item_id):
    """Return the catalog entry with the given id, or None."""
    for entry in CATALOG:
        if entry['id'] == item_id:
            return entry
    return None


def list_categories():
    """Unique sorted list of category paths in the catalog. Includes
    intermediate parents.
    """
    paths = set()
    for entry in CATALOG:
        cat = entry.get('category', '')
        if not cat:
            continue
        parts = cat.split('/')
        for i in range(1, len(parts) + 1):
            paths.add('/'.join(parts[:i]))
    return sorted(paths)


def category_label(path):
    if not path:
        return 'Everything'
    leaf = path.split('/')[-1]
    return leaf.replace('_', ' ').replace('-', ' ').title()


def category_indented_label(path):
    depth = path.count('/')
    indent = '    ' * depth
    return indent + category_label(path)
