"""
Blender to Mob UI Panels — Interface baseada no Promob com suporte a Scene Units e unidades flexíveis
"""

import bpy  # type: ignore
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


def _scene_has_floor(context):
    for obj in context.scene.objects:
        if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'FLOOR':
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
                # Conversão interna de metros para milímetros para o algoritmo de nesting
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

        # Dimensões da chapa em milímetros
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
# PAINEL PRINCIPAL: Criador de Ambientes
# ==========================================================================

class BTM_PT_EnvironmentBuilder(bpy.types.Panel):
    bl_label = "Criador de Ambientes"
    bl_idname = "BTM_PT_environment_builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        layout.label(text="Ferramentas de Construção", icon='SCENE_DATA')


# ==========================================================================
# SUB-PAINEL: Construção de Parede
# ==========================================================================

class BTM_PT_WallConstruction(bpy.types.Panel):
    bl_label = "Construção de Parede"
    bl_idname = "BTM_PT_wall_construction"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_parent_id = "BTM_PT_environment_builder"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("btm.wall_builder", text="Construir Parede", icon='GREASEPENCIL')

        layout.separator(factor=0.5)

        box = layout.box()
        box.label(text="Propriedades do Construtor", icon='PROPERTIES')

        # Tenta obter propriedades da parede ativa, ou fallback para padrão
        active_obj = context.active_object
        wall = None
        if active_obj and hasattr(active_obj, 'btm_wall') and active_obj.btm_plane.object_kind == 'WALL':
            wall = active_obj.btm_wall

        col = box.column(align=True)
        col.label(text="Dimensões:", icon='ARROW_LEFTRIGHT')
        
        row = col.row(align=True)
        row.label(text="Espessura:")
        val = wall.thickness if wall else 0.15
        row.label(text=units.format_value(val, context.scene))

        row = col.row(align=True)
        row.label(text="Altura:")
        val = wall.height_start if wall else 2.7
        row.label(text=units.format_value(val, context.scene))

        row = col.row(align=True)
        row.label(text="Afastamento:")
        val = wall.offset if wall else 0.0
        row.label(text=units.format_value(val, context.scene))

        col.separator(factor=0.5)

        col.label(text="Ângulos:", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        row = col.row(align=True)
        row.label(text="Âng. Absoluto:")
        val = wall.absolute_angle if wall else 0.0
        row.label(text=f"{val:.1f}°")

        row = col.row(align=True)
        row.label(text="Âng. Relativo:")
        val = wall.relative_angle if wall else 0.0
        row.label(text=f"{val:.1f}°")

        col.separator(factor=0.5)

        col.label(text="Incrementos:", icon='SNAP_INCREMENT')
        row = col.row(align=True)
        row.label(text="Incr. Linear:")
        val = wall.linear_increment if wall else 0.05
        row.label(text=units.format_value(val, context.scene))

        row = col.row(align=True)
        row.label(text="Incr. Angular:")
        val = wall.angular_increment if wall else 5.0
        row.label(text=f"{val:.1f}°")

        col.separator(factor=0.5)

        # Construção
        row = box.row()
        row.label(text="Construção:", icon='ORIENTATION_NORMAL')
        val = wall.orientation if wall else 'RIGHT'
        row.label(text="Direita" if val == 'RIGHT' else "Esquerda")

        # Tipo
        row = box.row()
        row.label(text="Tipo:", icon='OBJECT_DATA')
        val = wall.wall_type if wall else 'NORMAL'
        types_map = {'NORMAL': 'Normal', 'DRYWALL': 'Drywall', 'GLASS': 'Vidro'}
        row.label(text=types_map.get(val, 'Normal'))

        wall_count = sum(
            1 for obj in context.scene.objects
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'WALL'
        )
        if wall_count > 0:
            info_box = layout.box()
            info_box.label(text=f"Paredes na cena: {wall_count}", icon='INFO')


# ==========================================================================
# SUB-PAINEL: Piso
# ==========================================================================

class BTM_PT_FloorSection(bpy.types.Panel):
    bl_label = "Piso"
    bl_idname = "BTM_PT_floor_section"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_parent_id = "BTM_PT_environment_builder"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return _scene_has_walls(context)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("btm.adjust_floor", text="Ajustar Limites do Piso", icon='MESH_GRID')

        if _scene_has_floor(context):
            box = layout.box()
            box.label(text="Piso presente na cena", icon='CHECKMARK')

            settings = context.scene.btm_settings
            col = box.column(align=True)
            col.prop(settings, "show_grid", text="Exibir Grid")
            if settings.show_grid:
                row = col.row(align=True)
                row.prop(settings, "grid_spacing_x", text="Intervalo H")
                row.prop(settings, "grid_spacing_y", text="Intervalo V")
                col.prop(settings, "grid_snap_enabled", text="Atrair ao Grid")
                if settings.grid_snap_enabled:
                    col.prop(settings, "grid_snap_gap", text="Gap de Atração")
        else:
            layout.label(text="Nenhum piso na cena", icon='ERROR')
            layout.operator("btm.floor_builder", text="Criar Piso Manual", icon='MESH_PLANE')


# ==========================================================================
# SUB-PAINEL: Aberturas
# ==========================================================================

class BTM_PT_OpeningsSection(bpy.types.Panel):
    bl_label = "Aberturas"
    bl_idname = "BTM_PT_openings_section"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_parent_id = "BTM_PT_environment_builder"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return _scene_has_walls(context)

    def draw(self, context):
        layout = self.layout

        obj = context.active_object
        wall_selected = (
            obj is not None
            and hasattr(obj, 'btm_plane')
            and obj.btm_plane.object_kind == 'WALL'
        )

        if wall_selected:
            box = layout.box()
            box.label(text=f"Parede activa: {obj.name}", icon='MESH_PLANE')

            col = box.column(align=True)
            col.scale_y = 1.3
            col.operator("btm.insert_opening", text="Inserir Porta", icon='MOD_BOOLEAN').opening_type = 'DOOR'
            col.operator("btm.insert_opening", text="Inserir Janela", icon='MOD_BOOLEAN').opening_type = 'WINDOW'
        else:
            layout.label(text="Selecione uma parede", icon='INFO')
            layout.label(text="para inserir aberturas")

        # Lista aberturas existentes
        openings = [
            o for o in context.scene.objects
            if hasattr(o, 'btm_plane') and o.btm_plane.object_kind == 'OPENING'
        ]
        if openings:
            layout.separator(factor=0.5)
            box = layout.box()
            box.label(text=f"Aberturas ({len(openings)})", icon='OUTLINER_DATA_MESH')
            for opening_obj in openings:
                row = box.row(align=True)
                op_props = opening_obj.btm_opening
                type_icon = 'IMPORT' if op_props.opening_type == 'DOOR' else 'EXPORT'
                type_name = "Porta" if op_props.opening_type == 'DOOR' else "Janela"
                
                w_str = units.format_value(op_props.width, context.scene)
                h_str = units.format_value(op_props.height, context.scene)
                row.label(text=f"{type_name}: {w_str} x {h_str}", icon=type_icon)


# ==========================================================================
# SUB-PAINEL: Plano de Inserção
# ==========================================================================

class BTM_PT_InsertionPlane(bpy.types.Panel):
    bl_label = "Plano de Inserção"
    bl_idname = "BTM_PT_insertion_plane"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_parent_id = "BTM_PT_environment_builder"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        settings = context.scene.btm_settings

        layout.prop(settings, "show_insertion_plane", text="Sombreamento de Planos", icon='SHADING_RENDERED')

        obj = context.active_object
        if obj and hasattr(obj, 'btm_plane'):
            kind = obj.btm_plane.object_kind
            kind_labels = {
                'WALL': "Parede",
                'FLOOR': "Piso",
                'MODULE': "Módulo",
                'GEOMETRY': "Geometria",
                'OPENING': "Abertura",
            }
            box = layout.box()
            box.label(text=f"Plano ativo: {kind_labels.get(kind, kind)}", icon='LIGHT_AREA')
            if obj.btm_plane.parent_plane:
                box.label(text=f"Pai: {obj.btm_plane.parent_plane.name}")


# ==========================================================================
# PAINEL: Propriedades Paramétricas Dinâmicas (Context-Sensitive)
# ==========================================================================

class BTM_PT_ContextProperties(bpy.types.Panel):
    bl_label = "Propriedades"
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

        col.separator(factor=0.5)
        col.prop(wall, "sagitta")
        col.prop(wall, "wall_type")

        col.separator(factor=0.5)
        col.prop(wall, "linear_increment")
        col.prop(wall, "angular_increment")
        col.prop(wall, "orientation")
        col.prop(wall, "use_as_default")

        box2 = layout.box()
        box2.prop(obj.btm_plane, "layer_id")
        box2.prop(obj.btm_plane, "collision_override")

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

        box2 = layout.box()
        box2.prop(obj.btm_plane, "layer_id")
        box2.prop(obj.btm_plane, "collision_override")

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
# PAINEL: Módulos de Mobiliário
# ==========================================================================

class BTM_PT_FurniturePanel(bpy.types.Panel):
    bl_label = "Módulos"
    bl_idname = "BTM_PT_furniture_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        layout.operator("btm.cabinet_builder", text="Inserir Armário/Módulo", icon='OUTLINER_OB_MESH')

        module_count = sum(
            1 for obj in context.scene.objects
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'MODULE'
        )
        if module_count > 0:
            box = layout.box()
            box.label(text=f"Módulos na cena: {module_count}", icon='INFO')


# ==========================================================================
# PAINEL: Configurador de Dimensões (Estilo Promob)
# ==========================================================================

class BTM_PT_DimensionConfigurator(bpy.types.Panel):
    """Configurador de Dimensões e Fitas de Borda Promob-style"""
    bl_label = "Configurador de Dimensões"
    bl_idname = "BTM_PT_dimension_configurator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        settings = context.scene.btm_settings

        # Seletor de Componentes
        layout.prop(settings, "config_active_component", text="Componente")

        comp_type = settings.config_active_component
        if comp_type == 'LATERAL':
            comp = settings.config_lateral
            title = "Lateral"
        elif comp_type == 'DIVISORIA':
            comp = settings.config_divisoria
            title = "Divisória"
        elif comp_type == 'BASE':
            comp = settings.config_base
            title = "Base / Tampo"
        elif comp_type == 'FUNDO':
            comp = settings.config_fundo
            title = "Fundo"
        elif comp_type == 'PRATELEIRA':
            comp = settings.config_prateleira
            title = "Prateleira"
        elif comp_type == 'PORTA':
            comp = settings.config_porta
            title = "Porta / Frente"
        else:
            return

        layout.separator(factor=0.5)

        # Esquema visual de fitas de borda baseado no anexo do Promob
        box_schema = layout.box()
        box_schema.label(text="Esquema das Bordas", icon='SELECT_SET')
        
        col_schema = box_schema.column(align=True)
        col_schema.scale_y = 0.95
        col_schema.label(text="              (1) Superior")
        
        row_mid = col_schema.row(align=True)
        row_mid.label(text="(4) Esquerda / Frontal")
        row_mid.label(text="[ Painel ]")
        row_mid.label(text=" (3) Direita / Traseira")
        
        col_schema.label(text="              (2) Inferior")

        layout.separator(factor=0.5)

        # Tabela de propriedades paramétricas da chapa
        box_prop = layout.box()
        box_prop.label(text=f"Propriedades - {title}", icon='PROPERTIES')
        
        col = box_prop.column(align=True)
        col.prop(comp, "material", text="A - Material")
        col.prop(comp, "max_width", text="B - Largura Máxima")
        col.prop(comp, "max_length", text="C - Comprimento Máximo")
        col.prop(comp, "thickness", text="D - Espessura")

        layout.separator(factor=0.5)

        # Tabela de fitas de borda
        box_edge = layout.box()
        box_edge.label(text="Integração c/ Plano de Corte", icon='ALIGN_JUSTIFY')
        
        col_edge = box_edge.column(align=True)
        col_edge.prop(comp, "edge_1", text="E - Fita Borda 1")
        col_edge.prop(comp, "edge_2", text="F - Fita Borda 2")
        col_edge.prop(comp, "edge_3", text="G - Fita Borda 3")
        col_edge.prop(comp, "edge_4", text="H - Fita Borda 4")


# ==========================================================================
# PAINEL: Plano de Corte (Nesting)
# ==========================================================================

class BTM_PT_NestingPanel(bpy.types.Panel):
    bl_label = "Plano de Corte (Nesting)"
    bl_idname = "BTM_PT_nesting_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 4

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Otimizador de Chapas", icon='ALIGN_JUSTIFY')
        layout.operator("btm.calculate_nesting", text="Otimizar Plano de Corte", icon='PLAY')

        nesting_res = scene.get("btm_nesting_result", "Nenhuma otimização calculada")

        box = layout.box()
        box.label(text=nesting_res, icon='INFO')


# ==========================================================================
# PAINEL: Configurações Globais
# ==========================================================================

class BTM_PT_GlobalSettings(bpy.types.Panel):
    bl_label = "Configurações"
    bl_idname = "BTM_PT_global_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Blender to Mob"
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.btm_settings

        # Sistema de Unidade ativo do add-on
        box_unit = layout.box()
        box_unit.label(text="Unidades do Projeto", icon='SCENE_DATA')
        box_unit.prop(settings, "btm_unit", text="Unidade")

        # Snap settings
        box = layout.box()
        box.label(text="Snap & Posicionamento", icon='SNAP_ON')
        col = box.column(align=True)
        col.prop(settings, "snap_grid")
        if settings.snap_grid:
            col.prop(settings, "snap_increment")

        # Collision
        box2 = layout.box()
        box2.label(text="Colisão", icon='MOD_PHYSICS')
        box2.prop(settings, "collision_global")

        # Visual overlays
        box3 = layout.box()
        box3.label(text="Visualização", icon='OVERLAY')
        col = box3.column(align=True)
        col.prop(settings, "show_grid", text="Grid do Piso")
        col.prop(settings, "show_insertion_plane", text="Planos de Inserção")
        col.prop(settings, "show_dimensions", text="Cotas / Dimensões")


# ==========================================================================
# Registro
# ==========================================================================

classes = (
    BTM_OT_CalculateNesting,
    BTM_PT_EnvironmentBuilder,
    BTM_PT_WallConstruction,
    BTM_PT_FloorSection,
    BTM_PT_OpeningsSection,
    BTM_PT_InsertionPlane,
    BTM_PT_ContextProperties,
    BTM_PT_FurniturePanel,
    BTM_PT_DimensionConfigurator,
    BTM_PT_NestingPanel,
    BTM_PT_GlobalSettings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
