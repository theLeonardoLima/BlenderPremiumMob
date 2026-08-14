import bpy  # type: ignore
from .wall_builder import BTM_OT_WallBuilder
from .floor_builder import BTM_OT_FloorBuilder, BTM_OT_AdjustFloor
from .cabinet_builder import BTM_OT_CabinetBuilder
from .opening_builder import BTM_OT_InsertOpening, BTM_OT_RemoveOpening
from .ops_cutting import BTM_OT_CalculateNesting, BTM_OT_ExportCutPlanJSON
from .ops_dimensions import BTM_OT_DimensionSettingsDialog, BTM_OT_ApplyDimensionPreset

classes = (
    BTM_OT_WallBuilder,
    BTM_OT_FloorBuilder,
    BTM_OT_AdjustFloor,
    BTM_OT_CabinetBuilder,
    BTM_OT_InsertOpening,
    BTM_OT_RemoveOpening,
    BTM_OT_CalculateNesting,
    BTM_OT_ExportCutPlanJSON,
    BTM_OT_DimensionSettingsDialog,
    BTM_OT_ApplyDimensionPreset,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
