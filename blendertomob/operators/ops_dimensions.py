"""
BlenderToMob Dimensions Operators — Diálogo Modal e Operadores do Configurador de Dimensões
"""

import bpy  # type: ignore
from ..data.dimensions_preset import DIMENSION_PRESETS


class BTM_OT_DimensionSettingsDialog(bpy.types.Operator):
    """Abre a janela de Configuração Avançada de Dimensões e Padrões de Marcenaria"""
    bl_idname = "btm.dimension_settings_dialog"
    bl_label = "Configurações de Dimensões"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        dim = scene.btm_settings.dimension_settings

        # 1. Seletor de Presets
        box_preset = layout.box()
        box_preset.label(text="Padrões e Presets de Marcenaria", icon='ASSET_MANAGER')
        box_preset.prop(dim, "preset", text="Modelo")

        # 2. Dimensões Gerais
        box_gen = layout.box()
        box_gen.label(text="Dimensões Gerais do Módulo", icon='CON_SIZELIMIT')
        col = box_gen.column(align=True)

        row_w = col.row(align=True)
        row_w.prop(dim, "width_default", text="Largura")
        row_w.prop(dim, "width_min", text="Mín.")
        row_w.prop(dim, "width_max", text="Máx.")

        row_h = col.row(align=True)
        row_h.prop(dim, "height_default", text="Altura")
        row_h.prop(dim, "height_min", text="Mín.")
        row_h.prop(dim, "height_max", text="Máx.")

        row_d = col.row(align=True)
        row_d.prop(dim, "depth_default", text="Profundidade")
        row_d.prop(dim, "depth_min", text="Mín.")
        row_d.prop(dim, "depth_max", text="Máx.")

        col.separator(factor=0.5)
        col.prop(dim, "step_increment")
        col.prop(dim, "base_height")
        col.prop(dim, "wall_clearance")

        # 3. Espessuras de Chapas MDF
        box_th = layout.box()
        box_th.label(text="Espessuras de Chapas MDF", icon='MOD_SOLIDIFY')
        grid_th = box_th.grid_flow(columns=2, align=True)
        grid_th.prop(dim, "carcass_thickness", text="Caixa / Laterais")
        grid_th.prop(dim, "back_thickness", text="Fundo")
        grid_th.prop(dim, "door_thickness", text="Portas / Frentes")
        grid_th.prop(dim, "shelf_thickness", text="Prateleiras")

        # 4. Folgas, Recuos e Encaixes
        box_gaps = layout.box()
        box_gaps.label(text="Folgas e Recuos Estruturais", icon='SNAP_GRID')
        grid_gaps = box_gaps.grid_flow(columns=3, align=True)
        grid_gaps.prop(dim, "door_gap", text="Folga Portas")
        grid_gaps.prop(dim, "back_inset", text="Recuo Fundo")
        grid_gaps.prop(dim, "groove_depth", text="Canal Rebaixo")

        # 5. Fitas de Borda
        box_edge = layout.box()
        box_edge.label(text="Fitas de Borda (Espessuras)", icon='LINE_DATA')
        grid_edge = box_edge.grid_flow(columns=2, align=True)
        grid_edge.prop(dim, "edge_front", text="Frontal")
        grid_edge.prop(dim, "edge_back", text="Traseira")
        grid_edge.prop(dim, "edge_top", text="Superior")
        grid_edge.prop(dim, "edge_bottom", text="Inferior")

    def execute(self, context):
        self.report({'INFO'}, "Configurações de dimensões atualizadas.")
        return {'FINISHED'}


class BTM_OT_ApplyDimensionPreset(bpy.types.Operator):
    """Aplica rapidamente um preset dimensional específico ao projeto"""
    bl_idname = "btm.apply_dimension_preset"
    bl_label = "Aplicar Preset de Dimensão"
    bl_options = {'REGISTER', 'UNDO'}

    preset_key: bpy.props.StringProperty(name="Chave do Preset", default="COZINHA_INFERIOR")  # type: ignore

    def execute(self, context):
        scene = context.scene
        dim = scene.btm_settings.dimension_settings
        if self.preset_key in DIMENSION_PRESETS:
            dim.preset = self.preset_key
            self.report({'INFO'}, f"Preset '{DIMENSION_PRESETS[self.preset_key]['name']}' aplicado com sucesso.")
        return {'FINISHED'}


classes = (
    BTM_OT_DimensionSettingsDialog,
    BTM_OT_ApplyDimensionPreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
