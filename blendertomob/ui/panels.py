"""
BlenderToMob UI Panels — Interface de Marcenaria e CAD Paramétrico
Organizada em abas (CONSTRUTOR, GALERIA, CONFIGURAÇÕES e PLANO DE CORTE)
com suporte integral a Português do Brasil (pt_BR) e unidades dinâmicas (mm, cm, m).
"""

import bpy  # type: ignore
from ..data import units


# ==========================================================================
# Helpers de cena
# ==========================================================================

def _scene_has_walls(context):
    for obj in context.scene.objects:
        if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'WALL':
            return True
    return False


# ==========================================================================
# PAINEL PRINCIPAL: Criador de Ambientes (Blender to Mob)
# ==========================================================================

class BTM_PT_EnvironmentBuilder(bpy.types.Panel):
    bl_label = "Blender to Mob"
    bl_idname = "BTM_PT_environment_builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.btm_settings
        hb_scene = getattr(scene, 'home_builder', None)

        # Seletor de Abas (Segmented Buttons)
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop(settings, "btm_active_tab", expand=True)

        layout.separator(factor=0.8)

        tab = settings.btm_active_tab

        # ------------------------------------------------------------------
        # ABA: CONSTRUTOR
        # ------------------------------------------------------------------
        if tab == 'CONSTRUTOR':
            # Seção: Paredes e Piso
            box = layout.box()
            box.label(text="Paredes & Piso", icon='GREASEPENCIL')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("home_builder_walls.draw_walls", text="Desenhar Paredes", icon='GREASEPENCIL')
            grid.operator("btm.adjust_floor", text="Ajustar Piso", icon='MESH_GRID')
            grid.operator("btm.floor_builder", text="Piso Manual", icon='MESH_PLANE')
            grid.operator("home_builder_walls.add_ceiling", text="Criar Teto", icon='MESH_CUBE')

            # Seção: Aberturas
            box = layout.box()
            box.label(text="Aberturas & Vãos", icon='MOD_BOOLEAN')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("home_builder_doors_windows.place_door", text="Porta Simples", icon='IMPORT')
            grid.operator("home_builder_doors_windows.place_double_door", text="Porta Dupla", icon='EXPORT')
            grid.operator("home_builder_doors_windows.place_window", text="Janela", icon='MESH_GRID')
            grid.operator("home_builder_doors_windows.place_open_door", text="Vão Livre", icon='WORLD')

            # Seção: Módulos & Iluminação
            box = layout.box()
            box.label(text="Mobiliário & Iluminação", icon='LIGHT')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("btm.cabinet_builder", text="Módulo Rápido", icon='OUTLINER_OB_MESH')
            grid.operator("btm.dimension_settings_dialog", text="Config. Dimensões", icon='PREFERENCES')
            grid.operator("home_builder_walls.add_room_lights", text="Luzes do Quarto", icon='LIGHT')
            grid.operator("home_builder_obstacles.place_obstacle", text="Inserir Obstáculo", icon='ERROR')

        # ------------------------------------------------------------------
        # ABA: GALERIA DE MÓDULOS
        # ------------------------------------------------------------------
        elif tab == 'GALERIA':
            if hb_scene is None:
                layout.label(text="Biblioteca de módulos indisponível", icon='ERROR')
                return

            layout.prop(hb_scene, "product_tab", text="Biblioteca")
            layout.separator(factor=0.5)

            box = layout.box()
            if hb_scene.product_tab == 'FRAMELESS' and hasattr(scene, 'hb_frameless'):
                scene.hb_frameless.draw_library_ui(box, context)
            elif hb_scene.product_tab == 'FACE FRAME' and hasattr(scene, 'hb_face_frame'):
                scene.hb_face_frame.draw_library_ui(box, context)
            elif hasattr(scene, 'hb_closets'):
                scene.hb_closets.draw_library_ui(box, context)

        # ------------------------------------------------------------------
        # ABA: CONFIGURAÇÕES (Unidades, Dimensões e Limites MDF)
        # ------------------------------------------------------------------
        elif tab == 'CONFIGURACOES':
            # 1. Unidades e Snap
            box_unit = layout.box()
            box_unit.label(text="Unidade & Precisão", icon='SCENE_DATA')
            col = box_unit.column(align=True)
            col.prop(settings, "btm_unit", text="Unidade do Projeto")
            col.prop(settings, "snap_grid", text="Atrair ao Grid (Snap)")
            if settings.snap_grid:
                col.prop(settings, "snap_increment", text="Incremento do Snap")
            col.prop(settings, "collision_global", text="Evitar Colisões Físicas")

            # 2. Configurador de Dimensões (Promob-Style)
            box_dim = layout.box()
            box_dim.label(text="Padrões de Marcenaria (Dimensões)", icon='CON_SIZELIMIT')
            dim = settings.dimension_settings

            col_d = box_dim.column(align=True)
            col_d.prop(dim, "preset", text="Preset")

            row_btn = box_dim.row(align=True)
            row_btn.operator("btm.dimension_settings_dialog", text="Abrir Editor de Dimensões", icon='WINDOW')

            # Resumo rápido de espessuras
            box_th_summary = box_dim.box()
            box_th_summary.label(text="Espessuras de Chapa Ativas", icon='MOD_SOLIDIFY')
            grid_th = box_th_summary.grid_flow(columns=2, align=True)
            grid_th.prop(dim, "carcass_thickness", text="Estrutura/Caixa")
            grid_th.prop(dim, "back_thickness", text="Fundo")
            grid_th.prop(dim, "door_thickness", text="Portas")
            grid_th.prop(dim, "shelf_thickness", text="Prateleiras")

            # 3. Limites e Especificações de Chapas MDF
            box_mdf = layout.box()
            box_mdf.label(text="Limites & Configurações de Chapas MDF", icon='STICKY_UVS_DISABLE')
            mdf = settings.mdf_config

            col_mdf = box_mdf.column(align=True)
            col_mdf.prop(mdf, "sheet_format", text="Formato")
            col_mdf.prop(mdf, "sheet_width", text="Largura")
            col_mdf.prop(mdf, "sheet_height", text="Comprimento/Altura")

            box_refilo = box_mdf.box()
            box_refilo.label(text="Refilos (Descarte de Bordas)", icon='ARROW_LEFTRIGHT')
            grid_ref = box_refilo.grid_flow(columns=2, align=True)
            grid_ref.prop(mdf, "refilo_top", text="Superior")
            grid_ref.prop(mdf, "refilo_bottom", text="Inferior")
            grid_ref.prop(mdf, "refilo_left", text="Esquerdo")
            grid_ref.prop(mdf, "refilo_right", text="Direito")

            col_mdf.prop(mdf, "kerf", text="Lâmina de Serra (Kerf)")
            col_mdf.prop(mdf, "allow_rotation", text="Permitir Rotação de Peças")
            col_mdf.prop(mdf, "respect_grain", text="Respeitar Veio da Madeira")

            # 4. Gerenciador de Ambientes e Elevações
            if hb_scene is not None:
                from .. import hb_project
                room_scenes = hb_project.get_room_scenes()
                room_scenes.sort(key=lambda s: s.home_builder.sort_order if hasattr(s, 'home_builder') else 0)

                box_rooms = layout.box()
                box_rooms.label(text="Gerenciador de Ambientes", icon='HOME')

                col_rooms = box_rooms.column(align=True)
                for r_scene in room_scenes:
                    row = col_rooms.row(align=True)
                    is_selected = r_scene == context.scene
                    icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'

                    op = row.operator("home_builder.switch_room", text=r_scene.name, icon=icon)
                    op.scene_name = r_scene.name

                    if len(room_scenes) > 1:
                        del_op = row.operator("home_builder.delete_room", text="", icon='X')
                        del_op.scene_name = r_scene.name

                row_actions = box_rooms.row(align=True)
                row_actions.operator("home_builder.create_room", text="Novo Ambiente", icon='ADD')
                row_actions.operator("home_builder.rename_room", text="Renomear", icon='GREASEPENCIL')

        # ------------------------------------------------------------------
        # ABA: PLANO DE CORTE (Nesting & Exportação JSON)
        # ------------------------------------------------------------------
        elif tab == 'PLANO_CORTE':
            box_actions = layout.box()
            box_actions.label(text="Otimizador de Corte (Nesting)", icon='ALIGN_JUSTIFY')

            row_calc = box_actions.row(align=True)
            row_calc.scale_y = 1.3
            row_calc.operator("btm.calculate_nesting", text="Calcular Plano de Corte", icon='PLAY')

            row_exp = box_actions.row(align=True)
            row_exp.scale_y = 1.2
            row_exp.operator("btm.export_cut_plan_json", text="Exportar JSON (CorteCloud / CutList)", icon='EXPORT')

            # Resumo do Plano Calculado
            nesting_res = scene.get("btm_nesting_result", "Nenhuma otimização calculada.")
            box_info = layout.box()
            box_info.label(text="Status da Otimização", icon='INFO')
            box_info.label(text=nesting_res)

            if "btm_nesting_sheets_count" in scene:
                box_metrics = layout.box()
                box_metrics.label(text="Métricas do Projeto", icon='LINENUMBERS_ON')
                col_m = box_metrics.column(align=True)
                col_m.label(text=f"Total de Peças: {scene.get('btm_nesting_parts_count', 0)}")
                col_m.label(text=f"Chapas Necessárias: {scene.get('btm_nesting_sheets_count', 0)}")
                col_m.label(text=f"Aproveitamento: {scene.get('btm_nesting_utilization', 0.0)}%")


# ==========================================================================
# PAINEL: Propriedades Paramétricas Dinâmicas (Context-Sensitive)
# ==========================================================================

class BTM_PT_ContextProperties(bpy.types.Panel):
    bl_label = "Propriedades do Objeto Selecionado"
    bl_idname = "BTM_PT_context_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and hasattr(obj, 'btm_plane')
            and obj.btm_plane.object_kind in ('WALL', 'MODULE', 'OPENING', 'FLOOR')
        )

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        kind = obj.btm_plane.object_kind

        if kind == 'WALL':
            self._draw_wall_props(layout, obj)
        elif kind == 'MODULE':
            self._draw_module_props(layout, obj)
        elif kind == 'OPENING':
            self._draw_opening_props(layout, obj)
        elif kind == 'FLOOR':
            self._draw_floor_props(context, layout, obj)

    def _draw_wall_props(self, layout, obj):
        layout.label(text="Parâmetros da Parede", icon='MESH_PLANE')
        wall = obj.btm_wall

        box = layout.box()
        col = box.column(align=True)
        col.prop(wall, "length", text="Comprimento")
        col.prop(wall, "thickness", text="Espessura")

        col.separator(factor=0.5)
        col.prop(wall, "height_start", text="Pé-Direito Inicial")
        col.prop(wall, "height_end", text="Pé-Direito Final")
        col.prop(wall, "offset", text="Afastamento Base")

        col.separator(factor=0.5)
        col.prop(wall, "absolute_angle", text="Ângulo Absoluto")
        col.prop(wall, "relative_angle", text="Ângulo Relativo")
        col.prop(wall, "sagitta", text="Flecha do Arco")
        col.prop(wall, "wall_type", text="Tipo de Parede")

    def _draw_module_props(self, layout, obj):
        layout.label(text="Parâmetros do Módulo", icon='OUTLINER_OB_MESH')
        cabinet = obj.btm_cabinet

        box = layout.box()
        col = box.column(align=True)
        col.prop(cabinet, "cabinet_type", text="Tipo")
        col.separator(factor=0.5)
        col.prop(cabinet, "width", text="Largura")
        col.prop(cabinet, "height", text="Altura")
        col.prop(cabinet, "depth", text="Profundidade")
        col.prop(cabinet, "thickness", text="Espessura Chapas")

        # Portas e Controle de Abertura interativo
        box_door = layout.box()
        box_door.label(text="Portas & Abertura", icon='OUTLINER_OB_LIGHTPATH')
        col_door = box_door.column(align=True)
        col_door.prop(cabinet, "door_swing", text="Sentido")
        if cabinet.door_swing != 'NONE':
            col_door.prop(cabinet, "door_open", slider=True, text="Grau de Abertura")

    def _draw_opening_props(self, layout, obj):
        layout.label(text="Parâmetros da Abertura", icon='MOD_BOOLEAN')
        opening = obj.btm_opening

        box = layout.box()
        col = box.column(align=True)
        col.prop(opening, "opening_type", text="Tipo")
        col.separator(factor=0.5)
        col.prop(opening, "width", text="Largura")
        col.prop(opening, "height", text="Altura")
        col.prop(opening, "sill_height", text="Peitoril")

        if opening.parent_wall:
            col.separator(factor=0.5)
            col.label(text=f"Parede: {opening.parent_wall.name}", icon='LINKED')

        layout.separator(factor=0.5)
        row = layout.row()
        row.alert = True
        row.operator("btm.remove_opening", text="Remover Abertura", icon='TRASH')

    def _draw_floor_props(self, context, layout, obj):
        layout.label(text="Parâmetros do Piso", icon='MESH_GRID')
        box = layout.box()
        box.label(text=f"Elemento: {obj.name}")
        if obj.type == 'MESH':
            dims = obj.dimensions
            w_str = units.format_value(dims.x, context.scene)
            h_str = units.format_value(dims.y, context.scene)
            box.label(text=f"Dimensões: {w_str} x {h_str}")


# ==========================================================================
# PAINEL: Plano de Corte (Nesting)
# ==========================================================================

class BTM_PT_NestingPanel(bpy.types.Panel):
    bl_label = "Plano de Corte (Nesting)"
    bl_idname = "BTM_PT_nesting_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Otimizador de Chapas MDF", icon='ALIGN_JUSTIFY')
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("btm.calculate_nesting", text="Calcular Plano de Corte", icon='PLAY')

        row_exp = layout.row(align=True)
        row_exp.operator("btm.export_cut_plan_json", text="Exportar JSON Universal", icon='EXPORT')

        nesting_res = scene.get("btm_nesting_result", "Nenhuma otimização calculada")
        box = layout.box()
        box.label(text=nesting_res, icon='INFO')


# ==========================================================================
# Registro
# ==========================================================================

classes = (
    BTM_PT_EnvironmentBuilder,
    BTM_PT_ContextProperties,
    BTM_PT_NestingPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
