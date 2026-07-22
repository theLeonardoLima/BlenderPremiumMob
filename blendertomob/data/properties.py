import bpy  # type: ignore
import math


# ---------------------------------------------------------------------------
# Update callbacks — regenerate geometry/drivers when property changes
# ---------------------------------------------------------------------------

def update_wall_geom(self, context):
    obj = self.id_data
    if obj and obj.type == 'MESH':
        import json
        segments_str = obj.get("btm_wall_segments", "")
        if segments_str:
            try:
                segments_data = json.loads(segments_str)
                for seg in segments_data:
                    seg['thickness'] = self.thickness
                    seg['height'] = self.height_start
                obj["btm_wall_segments"] = json.dumps(segments_data)
                from ..geometry.mesh_gen import generate_wall_from_segments
                generate_wall_from_segments(obj, segments_data)
                return
            except Exception:
                pass
        
        # Fallback for single-segment walls
        from ..geometry.mesh_gen import generate_wall_mesh
        generate_wall_mesh(obj, self.length, self.thickness, self.height_start)


def update_cabinet_geom(self, context):
    obj = self.id_data
    if obj and obj.type == 'MESH':
        from ..geometry.mesh_gen import generate_cabinet_mesh
        generate_cabinet_mesh(obj, self.width, self.height, self.depth, self.thickness)
        
        # Atualiza a geometria da porta e o controlador vazio
        from ..geometry import door_controller
        door_controller.update_door_geometry_and_controller(obj)


def update_door_properties(self, context):
    obj = self.id_data
    if obj and obj.type == 'MESH':
        from ..geometry import door_controller
        door_controller.update_door_rotation_from_property(obj)


def update_scene_unit(self, context):
    unit_settings = context.scene.unit_settings
    unit_settings.system = 'METRIC'
    if self.btm_unit == 'METERS':
        unit_settings.length_unit = 'METERS'
    elif self.btm_unit == 'CENTIMETERS':
        unit_settings.length_unit = 'CENTIMETERS'
    elif self.btm_unit == 'MILLIMETERS':
        unit_settings.length_unit = 'MILLIMETERS'


# ---------------------------------------------------------------------------
# Wall Segment PropertyGroup
# ---------------------------------------------------------------------------

class BTM_PG_WallSegment(bpy.types.PropertyGroup):
    length: float = bpy.props.FloatProperty(
        name="Comprimento",
        description="Comprimento do segmento de parede",
        default=2.0,
        min=0.01,
        max=100.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )
    absolute_angle: float = bpy.props.FloatProperty(
        name="Ângulo Absoluto (°)",
        description="Ângulo do segmento em relação ao sistema global",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype='ANGLE'
    )
    relative_angle: float = bpy.props.FloatProperty(
        name="Ângulo Relativo (°)",
        description="Ângulo em relação ao segmento anterior",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype='ANGLE'
    )
    thickness: float = bpy.props.FloatProperty(
        name="Espessura",
        description="Espessura da parede",
        default=0.15,
        min=0.01,
        max=2.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )
    height_start: float = bpy.props.FloatProperty(
        name="Pé-Direito Inicial",
        description="Altura da parede no ponto inicial",
        default=2.7,
        min=0.1,
        max=10.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )
    height_end: float = bpy.props.FloatProperty(
        name="Pé-Direito Final",
        description="Altura da parede no ponto final",
        default=2.7,
        min=0.1,
        max=10.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )
    offset: float = bpy.props.FloatProperty(
        name="Afastamento",
        description="Afastamento da base da parede em relação ao piso",
        default=0.0,
        subtype='DISTANCE'
    )
    sagitta: float = bpy.props.FloatProperty(
        name="Flecha",
        description="Flecha do arco para paredes curvas (0 para retas)",
        default=0.0,
        subtype='DISTANCE'
    )
    linear_increment: float = bpy.props.FloatProperty(
        name="Incr. Linear",
        description="Passo do salto do cursor referente ao comprimento",
        default=0.05,
        min=0.001,
        max=1.0,
        subtype='DISTANCE'
    )
    angular_increment: float = bpy.props.FloatProperty(
        name="Incr. Angular (°)",
        description="Passo do ângulo quando ajustado pelo mouse",
        default=5.0,
        min=0.5,
        max=90.0,
        subtype='ANGLE'
    )
    orientation: bpy.props.EnumProperty(
        name="Construção",
        description="Lado da parede que recebe o valor de comprimento",
        items=[
            ('RIGHT', "Direita", "Construção no sentido horário"),
            ('LEFT', "Esquerda", "Construção no sentido anti-horário")
        ],
        default='RIGHT'
    )
    wall_type: bpy.props.EnumProperty(
        name="Tipo de Parede",
        description="Preset de material/espessura/acabamento",
        items=[
            ('NORMAL', "Normal", "Parede de alvenaria padrão"),
            ('DRYWALL', "Drywall", "Parede de gesso acartonado"),
            ('GLASS', "Vidro", "Parede de vidro tempoerado"),
        ],
        default='NORMAL'
    )
    use_as_default: bpy.props.BoolProperty(
        name="Utilizar valores como padrão",
        description="Salvar estes valores como padrão para novas paredes",
        default=False
    )


# ---------------------------------------------------------------------------
# Insertion Plane PropertyGroup
# ---------------------------------------------------------------------------

class BTM_PG_InsertionPlane(bpy.types.PropertyGroup):
    object_kind: bpy.props.EnumProperty(
        name="Tipo de Objeto",
        items=[
            ('WALL', "Parede", "Parede de alvenaria"),
            ('FLOOR', "Piso", "Piso de referência"),
            ('MODULE', "Módulo", "Módulo de marcenaria/armário"),
            ('GEOMETRY', "Geometria", "Geometria livre paramétrica"),
            ('OPENING', "Abertura", "Porta ou janela de ambiente"),
        ],
        default='WALL'
    )
    parent_plane: bpy.props.PointerProperty(
        name="Plano Pai",
        type=bpy.types.Object
    )
    layer_id: bpy.props.StringProperty(
        name="ID da Camada",
        default="Default"
    )
    collision_override: bpy.props.EnumProperty(
        name="Colisão",
        items=[
            ('INHERIT', "Herdar", "Herdar configuração global"),
            ('ON', "Ativa", "Colisão ativa"),
            ('OFF', "Desativada", "Ignorar colisão")
        ],
        default='INHERIT'
    )


# ---------------------------------------------------------------------------
# Opening Properties (Portas e Janelas)
# ---------------------------------------------------------------------------

class BTM_PG_OpeningProperties(bpy.types.PropertyGroup):
    opening_type: bpy.props.EnumProperty(
        name="Tipo de Abertura",
        description="Tipo de abertura de parede",
        items=[
            ('DOOR', "Porta", "Porta de ambiente"),
            ('WINDOW', "Janela", "Janela de ambiente"),
        ],
        default='DOOR'
    )
    width: float = bpy.props.FloatProperty(
        name="Largura",
        description="Largura do vão da abertura",
        default=0.8,
        min=0.1,
        max=5.0,
        subtype='DISTANCE'
    )
    height: float = bpy.props.FloatProperty(
        name="Altura",
        description="Altura do vão da abertura",
        default=2.1,
        min=0.1,
        max=5.0,
        subtype='DISTANCE'
    )
    sill_height: float = bpy.props.FloatProperty(
        name="Peitoril",
        description="Afastamento do piso até a base da abertura (0 para portas)",
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='DISTANCE'
    )
    parent_wall: bpy.props.PointerProperty(
        name="Parede",
        description="Parede que contém esta abertura",
        type=bpy.types.Object
    )


# ---------------------------------------------------------------------------
# Cabinet Properties
# ---------------------------------------------------------------------------

class BTM_PG_CabinetProperties(bpy.types.PropertyGroup):
    width: float = bpy.props.FloatProperty(
        name="Largura",
        default=0.8,
        min=0.1,
        max=3.0,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )
    height: float = bpy.props.FloatProperty(
        name="Altura",
        default=0.7,
        min=0.1,
        max=3.0,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )
    depth: float = bpy.props.FloatProperty(
        name="Profundidade",
        default=0.55,
        min=0.1,
        max=2.0,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )
    thickness: float = bpy.props.FloatProperty(
        name="Espessura Chapas",
        default=0.018,
        min=0.006,
        max=0.05,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )
    cabinet_type: bpy.props.EnumProperty(
        name="Tipo de Armário",
        items=[
            ('BASE', "Balcão Inferior", ""),
            ('WALL', "Aéreo", ""),
            ('TALL', "Paneleiro/Despensa", "")
        ],
        default='BASE'
    )
    
    # Propriedades de abertura e swing da porta
    door_open: float = bpy.props.FloatProperty(
        name="Abertura Porta",
        description="Porcentagem de abertura da porta (0.0 = Fechada, 1.0 = Totalmente Aberta)",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=update_door_properties
    )
    door_swing: bpy.props.EnumProperty(
        name="Sentido Abertura",
        description="Tipo e sentido de abertura das portas",
        items=[
            ('NONE', "Sem Porta", ""),
            ('LEFT', "Esquerda", "Porta simples abrindo para a esquerda"),
            ('RIGHT', "Direita", "Porta simples abrindo para a direita"),
            ('DOUBLE', "Dupla", "Portas duplas abrindo para os lados"),
            ('FLIP', "Basculante", "Porta abrindo para cima"),
        ],
        default='LEFT',
        update=update_cabinet_geom
    )


# ---------------------------------------------------------------------------
# Component Configuration PropertyGroup (Dimension Configurator)
# ---------------------------------------------------------------------------

class BTM_PG_ComponentConfig(bpy.types.PropertyGroup):
    material: bpy.props.EnumProperty(
        name="Material",
        items=[
            ('MDF', "MDF", ""),
            ('MDP', "MDP", ""),
            ('WOOD', "Madeira Maciça", ""),
        ],
        default='MDF'
    )
    max_width: float = bpy.props.FloatProperty(
        name="Largura Máxima da Chapa",
        default=2.73,
        min=0.1,
        max=10.0,
        subtype='DISTANCE'
    )
    max_length: float = bpy.props.FloatProperty(
        name="Comprimento Máximo da Chapa",
        default=1.81,
        min=0.1,
        max=10.0,
        subtype='DISTANCE'
    )
    thickness: float = bpy.props.FloatProperty(
        name="Espessura da Chapa",
        default=0.015,
        min=0.003,
        max=0.1,
        subtype='DISTANCE'
    )
    # Edge bands (fitas de borda)
    edge_1: float = bpy.props.FloatProperty(
        name="Fita Borda 1 (Superior)",
        default=0.0,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )
    edge_2: float = bpy.props.FloatProperty(
        name="Fita Borda 2 (Inferior)",
        default=0.0,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )
    edge_3: float = bpy.props.FloatProperty(
        name="Fita Borda 3 (Direita/Traseira)",
        default=0.0,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )
    edge_4: float = bpy.props.FloatProperty(
        name="Fita Borda 4 (Esquerda/Frontal)",
        default=0.0004,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )


# ---------------------------------------------------------------------------
# Scene Settings (Global)
# ---------------------------------------------------------------------------

class BTM_PG_SceneSettings(bpy.types.PropertyGroup):
    btm_active_tab: bpy.props.EnumProperty(
        name="Aba Ativa",
        items=[
            ('CONSTRUTOR', "CONSTRUTOR", "Ferramentas de desenho e construção", 'GREASEPENCIL', 0),
            ('GALERIA', "GALERIA", "Galeria de móveis e componentes", 'ASSET_MANAGER', 1),
            ('CONFIGURACOES', "CONFIGURAÇÕES", "Configurações do projeto e dimensões", 'PREFERENCES', 2),
        ],
        default='CONSTRUTOR'
    )

    # Dropdown de Unidade do add-on
    btm_unit: bpy.props.EnumProperty(
        name="Unidade",
        description="Escolha a unidade de medida do projeto",
        items=[
            ('METERS', "Metros (m)", "Entrada e exibição em metros"),
            ('CENTIMETERS', "Centímetros (cm)", "Entrada e exibição em centímetros"),
            ('MILLIMETERS', "Milímetros (mm)", "Entrada e exibição em milímetros"),
        ],
        default='MILLIMETERS',
        update=update_scene_unit
    )

    # Snap settings
    snap_grid: bpy.props.BoolProperty(
        name="Snap ao Grid",
        description="Ativa o snap posicional em incrementos fixos",
        default=True
    )
    snap_increment: float = bpy.props.FloatProperty(
        name="Incremento de Snap",
        description="Passo do snap para posicionamento",
        default=0.05,
        min=0.001,
        max=1.0,
        subtype='DISTANCE'
    )
    collision_global: bpy.props.BoolProperty(
        name="Colisões Globais",
        description="Evitar interseção física entre módulos",
        default=True
    )

    # Grid overlay settings
    show_grid: bpy.props.BoolProperty(
        name="Exibir Grid no Piso",
        description="Mostra grid pontilhado sobre o piso para guia de posicionamento",
        default=True
    )
    grid_spacing_x: float = bpy.props.FloatProperty(
        name="Intervalo Horizontal",
        description="Espaçamento horizontal das linhas da grade",
        default=0.5,
        min=0.05,
        max=5.0,
        subtype='DISTANCE'
    )
    grid_spacing_y: float = bpy.props.FloatProperty(
        name="Intervalo Vertical",
        description="Espaçamento vertical das linhas da grade",
        default=0.5,
        min=0.05,
        max=5.0,
        subtype='DISTANCE'
    )
    grid_snap_enabled: bpy.props.BoolProperty(
        name="Atrair ao Grid",
        description="Módulos são atraídos para a grade mais próxima",
        default=True
    )
    grid_snap_gap: float = bpy.props.FloatProperty(
        name="Gap de Atração",
        description="Distância máxima na qual a atração da grade passa a agir",
        default=0.05,
        min=0.005,
        max=0.5,
        subtype='DISTANCE'
    )

    # Insertion plane overlay
    show_insertion_plane: bpy.props.BoolProperty(
        name="Mostrar Planos de Inserção",
        description="Exibe sombreamento amarelo no plano de inserção sob o cursor",
        default=True
    )

    # Dimension labels
    show_dimensions: bpy.props.BoolProperty(
        name="Exibir Cotas",
        description="Mostra dimensões dinâmicas sobre os objetos",
        default=True
    )

    # Configurador de componentes ativos
    config_active_component: bpy.props.EnumProperty(
        name="Componente",
        description="Escolha o componente a configurar",
        items=[
            ('LATERAL', "Lateral", "Lateral do móvel"),
            ('DIVISORIA', "Divisória", "Divisória interna"),
            ('BASE', "Base", "Base ou tampo estrutural"),
            ('FUNDO', "Fundo", "Fundo do armário"),
            ('PRATELEIRA', "Prateleira", "Prateleira interna"),
            ('PORTA', "Porta / Frente", "Portas e frentes de gaveta"),
        ],
        default='LATERAL'
    )

    # Ponteiros para configurações individuais
    config_lateral: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)
    config_divisoria: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)
    config_base: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)
    config_fundo: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)
    config_prateleira: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)
    config_porta: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    BTM_PG_WallSegment,
    BTM_PG_InsertionPlane,
    BTM_PG_OpeningProperties,
    BTM_PG_CabinetProperties,
    BTM_PG_ComponentConfig,
    BTM_PG_SceneSettings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register property pointers on Blender data types
    bpy.types.Object.btm_wall = bpy.props.PointerProperty(type=BTM_PG_WallSegment)
    bpy.types.Object.btm_plane = bpy.props.PointerProperty(type=BTM_PG_InsertionPlane)
    bpy.types.Object.btm_opening = bpy.props.PointerProperty(type=BTM_PG_OpeningProperties)
    bpy.types.Object.btm_cabinet = bpy.props.PointerProperty(type=BTM_PG_CabinetProperties)
    bpy.types.Scene.btm_settings = bpy.props.PointerProperty(type=BTM_PG_SceneSettings)


def unregister():
    # Remove properties from data types
    del bpy.types.Object.btm_wall
    del bpy.types.Object.btm_plane
    del bpy.types.Object.btm_opening
    del bpy.types.Object.btm_cabinet
    del bpy.types.Scene.btm_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
