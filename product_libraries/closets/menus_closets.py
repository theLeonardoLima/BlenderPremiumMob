"""Right-click context menus for closet starters, bays, and openings.

The right-click handler in ui/menu_apend.py reads obj['MENU_ID'] from the
active object and shows the named Menu class. Phase 1 keeps these minimal
(properties + delete); part-add flows land in Phase 3.
"""
import bpy


class HOME_BUILDER_MT_closet_starter_commands(bpy.types.Menu):
    """Right-click menu for a closet starter root."""
    bl_label = "Closet Starter Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_closets.starter_prompts",
                        text="Starter Properties...", icon='WINDOW')
        layout.separator()
        layout.operator("hb_closets.delete_starter",
                        text="Delete Starter", icon='X')


class HOME_BUILDER_MT_closet_bay_commands(bpy.types.Menu):
    """Right-click menu for a closet bay cage."""
    bl_label = "Closet Bay Commands"

    def draw(self, context):
        layout = self.layout
        _draw_add_part_entries(layout)
        layout.separator()
        layout.operator("hb_closets.bay_prompts",
                        text="Bay Properties...", icon='WINDOW')
        layout.separator()
        op = layout.operator("hb_closets.insert_bay",
                             text="Insert Bay Left", icon='TRIA_LEFT')
        op.direction = 'BEFORE'
        op = layout.operator("hb_closets.insert_bay",
                             text="Insert Bay Right", icon='TRIA_RIGHT')
        op.direction = 'AFTER'
        layout.separator()
        layout.operator("hb_closets.delete_bay",
                        text="Delete Bay", icon='X')


def _draw_add_part_entries(layout):
    """Shared add-part section for the bay and opening menus."""
    op = layout.operator("hb_closets.add_part",
                         text="Add Fixed Shelf", icon='FIXED_SIZE')
    op.part_type = 'FIXED_SHELF'
    op = layout.operator("hb_closets.add_part",
                         text="Add Hang Rod", icon='LINKED')
    op.part_type = 'ROD'
    layout.operator("hb_closets.add_adj_shelves",
                    text="Adjustable Shelves...", icon='ALIGN_JUSTIFY')
    layout.separator()
    layout.operator("hb_closets.add_drawers",
                    text="Drawers...", icon='SNAP_FACE')
    layout.operator("hb_closets.add_doors",
                    text="Doors / Hamper...", icon='SNAP_VOLUME')
    layout.operator("hb_closets.add_cubbies",
                    text="Cubbies...", icon='MESH_GRID')


class HOME_BUILDER_MT_closet_opening_commands(bpy.types.Menu):
    """Right-click menu for a closet opening cage."""
    bl_label = "Closet Opening Commands"

    def draw(self, context):
        layout = self.layout
        _draw_add_part_entries(layout)
        layout.separator()
        layout.operator("hb_closets.bay_prompts",
                        text="Bay Properties...", icon='WINDOW')


class HOME_BUILDER_MT_closet_part_commands(bpy.types.Menu):
    """Right-click menu for a user-added interior part."""
    bl_label = "Closet Part Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_closets.delete_part",
                        text="Delete Part", icon='X')


classes = (
    HOME_BUILDER_MT_closet_starter_commands,
    HOME_BUILDER_MT_closet_bay_commands,
    HOME_BUILDER_MT_closet_opening_commands,
    HOME_BUILDER_MT_closet_part_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
