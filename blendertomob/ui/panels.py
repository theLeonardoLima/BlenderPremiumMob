"""
Blender to Mob UI Panels — Interface organizada em abas de grade (Grid Dashboard)
CONSTRUTOR, GALERIA DE MÓDULOS e CONFIGURAÇÕES (com Configurador de Dimensões e Projetos).
"""

import bpy  # type: ignore
import os
from ..cutting.nesting import NestingPart, optimize_nesting
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
# Operador de Nesting
# ==========================================================================

class BTM_OT_CalculateNesting(bpy.types.Operator):
    """Calcula a otimização de corte (nesting) dos módulos na cena"""
    bl_idname = "btm.calculate_nesting"
    bl_label = "Calcular Plano de Corte"
    bl_options = {'REGISTER'}

    def execute(self, context):
        modules = []
        for obj in context.scene.objects:
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'MODULE':
                cabinet = obj.btm_cabinet
                part = NestingPart(
                    id=obj.name,
                    name=obj.name,
                    width=cabinet.width * 1000.0,
                    height=cabinet.depth * 1000.0,
                    quantity=1,
                    grain_direction='NONE',
                    module_ref=obj.name
                )
                modules.append(part)

        if not modules:
            self.report({'WARNING'}, "Nenhum módulo encontrado na cena para otimização.")
            return {'CANCELLED'}

        result = optimize_nesting(
            parts=modules,
            sheet_width=2750.0,
            sheet_height=1830.0,
            refilo=10.0,
            kerf=4.0
        )

        stats = result["stats"]
        msg = (f"Nesting Concluído: {stats['sheets_count']} chapas usadas. "
               f"Aproveitamento: {stats['utilization_percentage']}%")
        self.report({'INFO'}, msg)
        context.scene["btm_nesting_result"] = msg
        return {'FINISHED'}


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

        # Tab selector (Segmented buttons row)
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop(settings, "btm_active_tab", expand=True)

        layout.separator(factor=0.8)

        tab = settings.btm_active_tab

        # ------------------------------------------------------------------
        # ABA: CONSTRUTOR
        # ------------------------------------------------------------------
        if tab == 'CONSTRUTOR':
            # Seção: Desenho de Paredes e Contorno
            box = layout.box()
            box.label(text="Paredes & Piso", icon='GREASEPENCIL')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("home_builder_walls.draw_walls", text="Desenhar Paredes", icon='GREASEPENCIL')
            grid.operator("btm.adjust_floor", text="Ajustar Piso", icon='MESH_GRID')
            grid.operator("btm.floor_builder", text="Piso Manual", icon='MESH_PLANE')
            grid.operator("home_builder_walls.add_ceiling", text="Criar Teto", icon='MESH_CUBE')

            # Seção: Aberturas e Perfuração
            box = layout.box()
            box.label(text="Aberturas & Esqueleto", icon='MOD_BOOLEAN')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("home_builder_doors_windows.place_door", text="Porta Simples", icon='IMPORT')
            grid.operator("home_builder_doors_windows.place_double_door", text="Porta Dupla", icon='EXPORT')
            grid.operator("home_builder_doors_windows.place_window", text="Janela", icon='MESH_GRID')
            grid.operator("home_builder_doors_windows.place_open_door", text="Vão Aberto", icon='WORLD')

            # Seção: Agregados & Iluminação
            box = layout.box()
            box.label(text="Mobiliário & Luz", icon='LIGHT')
            grid = box.grid_flow(columns=2, even_columns=True, even_rows=True, align=True)
            grid.operator("btm.cabinet_builder", text="Módulo Rápido", icon='OUTLINER_OB_MESH')
            grid.operator("home_builder_walls.add_room_lights", text="Iluminação", icon='LIGHT')
            grid.operator("home_builder_walls.setup_world_lighting", text="Luz do Ambiente", icon='WORLD')
            grid.operator("home_builder_obstacles.place_obstacle", text="Obstáculo", icon='ERROR')

        # ------------------------------------------------------------------
        # ABA: GALERIA DE MÓDULOS
        # ------------------------------------------------------------------
        elif tab == 'GALERIA':
            if hb_scene is None:
                layout.label(text="Biblioteca indisponível", icon='ERROR')
                return

            # Selector de biblioteca
            layout.prop(hb_scene, "product_tab", text="Biblioteca")

            layout.separator(factor=0.5)

            # Renderiza a UI da biblioteca original
            box = layout.box()
            if hb_scene.product_tab == 'FRAMELESS' and hasattr(scene, 'hb_frameless'):
                scene.hb_frameless.draw_library_ui(box, context)
            elif hb_scene.product_tab == 'FACE FRAME' and hasattr(scene, 'hb_face_frame'):
                scene.hb_face_frame.draw_library_ui(box, context)
            elif hasattr(scene, 'hb_closets'):
                scene.hb_closets.draw_library_ui(box, context)

        # ------------------------------------------------------------------
        # ABA: CONFIGURAÇÕES
        # ------------------------------------------------------------------
        elif tab == 'CONFIGURACOES':
            # 1. Unidades e Medidas
            box_unit = layout.box()
            box_unit.label(text="Configurações Gerais & Snap", icon='SCENE_DATA')
            col = box_unit.column(align=True)
            col.prop(settings, "btm_unit", text="Unidade")
            col.prop(settings, "snap_grid", text="Atrair ao Grid")
            if settings.snap_grid:
                col.prop(settings, "snap_increment", text="Passo do Snap")
            col.prop(settings, "collision_global", text="Colisões Globais")

            # 2. Configurador de Dimensões (Promob-Style)
            box_config = layout.box()
            box_config.label(text="Configurador de Móveis", icon='PROPERTIES')
            box_config.prop(settings, "config_active_component", text="Peça")
            
            comp_type = settings.config_active_component
            comp = None
            if comp_type == 'LATERAL':
                comp = settings.config_lateral
            elif comp_type == 'DIVISORIA':
                comp = settings.config_divisoria
            elif comp_type == 'BASE':
                comp = settings.config_base
            elif comp_type == 'FUNDO':
                comp = settings.config_fundo
            elif comp_type == 'PRATELEIRA':
                comp = settings.config_prateleira
            elif comp_type == 'PORTA':
                comp = settings.config_porta

            if comp:
                col = box_config.column(align=True)
                col.prop(comp, "material", text="Material")
                col.prop(comp, "max_width", text="Largura Máx.")
                col.prop(comp, "max_length", text="Comprimento Máx.")
                col.prop(comp, "thickness", text="Espessura")
                
                # Fitas de Borda
                box_border = box_config.box()
                box_border.label(text="Fitas de Borda (Espessura)", icon='ALIGN_JUSTIFY')
                col_b = box_border.column(align=True)
                col_b.prop(comp, "edge_1", text="1 - Superior")
                col_b.prop(comp, "edge_2", text="2 - Inferior")
                col_b.prop(comp, "edge_3", text="3 - Direita/Traseira")
                col_b.prop(comp, "edge_4", text="4 - Esquerda/Frontal")

            # 3. Gerenciador de Quartos e Ambientes
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
                row_actions.operator("home_builder.create_room", text="Novo Quarto", icon='ADD')
                row_actions.operator("home_builder.rename_room", text="Renomear", icon='GREASEPENCIL')

            # 4. Pranchas e Layouts 2D
            from .. import hb_layouts
            layout_views = hb_layouts.LayoutView.get_all_layout_views()
            layout_views.sort(key=lambda s: s.home_builder.sort_order if hasattr(s, 'home_builder') else 0)

            box_layouts = layout.box()
            box_layouts.label(text="Layouts & Elevações 2D", icon='VIEW_ORTHO')
            
            if layout_views:
                col_layouts = box_layouts.column(align=True)
                for view in layout_views:
                    row = col_layouts.row(align=True)
                    is_selected = view == context.scene
                    icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'
                    
                    op = row.operator("home_builder_layouts.go_to_layout_view", text=view.name, icon=icon)
                    op.scene_name = view.name
                    
                    del_op = row.operator("home_builder_layouts.delete_layout_view", text="", icon='X')
                    del_op.scene_name = view.name

            row_create = box_layouts.row(align=True)
            row_create.operator("home_builder_layouts.create_all_elevations", text="Gerar Elevações", icon='DOCUMENTS')
            row_create.operator("home_builder_layouts.create_plan_view", text="Planta Baixa", icon='MESH_GRID')


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
        col.prop(wall, "length")
        col.prop(wall, "thickness")

        col.separator(factor=0.5)
        col.prop(wall, "height_start")
        col.prop(wall, "height_end")
        col.prop(wall, "offset")

        col.separator(factor=0.5)
        col.prop(wall, "absolute_angle")
        col.prop(wall, "relative_angle")
        col.prop(wall, "sagitta")
        col.prop(wall, "wall_type")

    def _draw_module_props(self, layout, obj):
        layout.label(text="Parâmetros do Módulo", icon='OUTLINER_OB_MESH')
        cabinet = obj.btm_cabinet

        box = layout.box()
        col = box.column(align=True)
        col.prop(cabinet, "cabinet_type")
        col.separator(factor=0.5)
        col.prop(cabinet, "width")
        col.prop(cabinet, "height")
        col.prop(cabinet, "depth")
        col.prop(cabinet, "thickness")

        # Portas e Controle de Abertura interativo
        box_door = layout.box()
        box_door.label(text="Portas & Rotação", icon='OUTLINER_OB_LIGHTPATH')
        col_door = box_door.column(align=True)
        col_door.prop(cabinet, "door_swing")
        if cabinet.door_swing != 'NONE':
            col_door.prop(cabinet, "door_open", slider=True, text="Abertura")

    def _draw_opening_props(self, layout, obj):
        layout.label(text="Parâmetros da Abertura", icon='MOD_BOOLEAN')
        opening = obj.btm_opening

        box = layout.box()
        col = box.column(align=True)
        col.prop(opening, "opening_type")
        col.separator(factor=0.5)
        col.prop(opening, "width")
        col.prop(opening, "height")
        col.prop(opening, "sill_height")

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
        box.label(text=f"Objeto: {obj.name}")
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

        layout.label(text="Otimizador de Chapas", icon='ALIGN_JUSTIFY')
        layout.operator("btm.calculate_nesting", text="Otimizar Plano de Corte", icon='PLAY')

        nesting_res = scene.get("btm_nesting_result", "Nenhuma otimização calculada")

        box = layout.box()
        box.label(text=nesting_res, icon='INFO')


# ==========================================================================
# Registro
# ==========================================================================

classes = (
    BTM_OT_CalculateNesting,
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
