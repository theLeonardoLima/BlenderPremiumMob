"""Estado do Editor de Armário (feature 004, T014; data-delta §1.5, D-21, D-22).

- `Session` (em memória, uma por vez): raiz do módulo, rascunho (`state.Draft`), peças da vista frontal, componente
  selecionado, mensagens, ajustes automáticos, vista 2D, janela/área e os pedidos que o modal executa.
- `WindowManager.btm_cabinet_editor`: campos do painel. As medidas são virtuais (`get`/`set`): o `set` só registra um
  pedido na sessão; quem edita o módulo é o modal (D-22), para o Blender criar um passo de desfazer só no Confirmar.
- Feature 006 (D-01, D-13, D-14): aba ativa, opções da próxima divisão (lembradas enquanto o editor está aberto),
  subvão escolhido e os espelhos das listas de componentes externos e de divisões.
"""

import bpy  # type: ignore

EDITOR_CATEGORY = "Editor de Armário"


class Session:
    def __init__(self, root_name, library, draft):
        self.root_name = root_name
        self.library = library
        self.draft = draft
        self.parts = []                   # elevation.Part
        self.initial_parts = []
        self.selected = None              # nome do componente
        self.messages = []                # validate.Message
        self.adjustments = []             # (nome, mudança)
        self.limits = {}
        self.view = None
        self.window_ptr = 0
        self.area_ptr = 0
        self.restore_area_type = None
        self.requests = []                # [(tipo, dados)] executados pelo modal
        self.request = None               # 'ok' | 'cancel'
        self.error = ""
        self.space = ""                   # subvão escolhido na aba Divisão (feature 006)
        self.spaces = {}                  # caminho → caixa (lo, hi) dos subvãos-folha, no referencial da vista
        self.space_labels = {}            # caminho → rótulo
        self.removed_parts = []           # elevation.Part das peças removidas (desenhadas tracejadas)

    def root(self):
        return bpy.data.objects.get(self.root_name)

    def push(self, kind, data=None):
        self.requests.append((kind, data))
        self.redraw()

    def blocking(self):
        return any(m.blocks for m in self.messages)

    def redraw(self):
        wm = bpy.context.window_manager
        for window in wm.windows:
            for area in window.screen.areas:
                if area.as_pointer() == self.area_ptr or area.type == 'VIEW_3D':
                    area.tag_redraw()


_session = [None]


def session():
    return _session[0]


def start(root_name, library, draft):
    _session[0] = Session(root_name, library, draft)
    return _session[0]


def end():
    _session[0] = None


# Campos virtuais ---------------------------------------------------------------------------------------------

_DIM_INDEX = {'width': 0, 'height': 1, 'depth': 2}


def _dim_get(name):
    def get(_self):
        s = session()
        return float(s.draft.current.dimensions[_DIM_INDEX[name]]) if s is not None else 0.0
    return get


def _dim_set(name):
    def set_(_self, value):
        s = session()
        if s is not None:
            s.push('dimension', (name, float(value)))
    return set_


def _index_update(self, context):
    s = session()
    if s is None or not (0 <= self.component_index < len(self.components)):
        return
    s.selected = self.components[self.component_index].name
    s.redraw()


class BTM_PG_CabinetEditorComponent(bpy.types.PropertyGroup):
    kind: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    flagged: bpy.props.BoolProperty()  # type: ignore   # tem mensagem


class BTM_PG_CabinetEditorMessage(bpy.types.PropertyGroup):
    code: bpy.props.StringProperty()  # type: ignore
    severity: bpy.props.StringProperty()  # type: ignore
    component: bpy.props.StringProperty()  # type: ignore
    parameter: bpy.props.StringProperty()  # type: ignore
    value: bpy.props.StringProperty()  # type: ignore
    range: bpy.props.StringProperty()  # type: ignore
    action: bpy.props.StringProperty()  # type: ignore
    blocks: bpy.props.BoolProperty()  # type: ignore


class BTM_PG_CabinetEditorAdjustment(bpy.types.PropertyGroup):
    component: bpy.props.StringProperty()  # type: ignore
    change: bpy.props.StringProperty()  # type: ignore


TAB_ITEMS = [
    ('STRUCTURE', "Estrutura", "Medidas externas e componentes externos", 'MOD_BUILD', 0),
    ('DIVISIONS', "Divisão", "Chapas de divisão vertical e horizontal", 'MOD_LATTICE', 1),
    ('FINISH', "Acabamento", "Frentes, puxadores e materiais", 'MATERIAL', 2),
]
_SPACE_CACHE = []


def _space_items(self, context):
    s = session()
    items = [(path, s.space_labels.get(path, path), "") for path in sorted(s.spaces)] if s is not None else []
    _SPACE_CACHE[:] = items or [("", "Sem vão interno", "")]
    return _SPACE_CACHE


def _space_get(self):
    s = session()
    if s is None or not s.space:
        return 0
    for index, item in enumerate(_space_items(self, None)):
        if item[0] == s.space:
            return index
    return 0


def _space_set(self, value):
    s = session()
    items = _space_items(self, None)
    if s is not None and 0 <= value < len(items):
        s.space = items[value][0]
        s.redraw()


class BTM_PG_CabinetEditorStructureRow(bpy.types.PropertyGroup):
    role: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    size: bpy.props.StringProperty()  # type: ignore          # medidas da chapa, já formatadas
    material: bpy.props.StringProperty()  # type: ignore      # material da chapa em uso
    thickness: bpy.props.StringProperty()  # type: ignore     # espessura em uso, formatada
    removed: bpy.props.BoolProperty()  # type: ignore
    mode: bpy.props.StringProperty()  # type: ignore          # modo usado na remoção
    changed: bpy.props.BoolProperty()  # type: ignore         # alterado neste armário
    reason_remove: bpy.props.StringProperty()  # type: ignore  # vazio = pode remover
    reason_edit: bpy.props.StringProperty()  # type: ignore    # vazio = pode editar espessura


class BTM_PG_CabinetEditorDivisionRow(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    detail: bpy.props.StringProperty()  # type: ignore
    flagged: bpy.props.BoolProperty()  # type: ignore


class BTM_PG_CabinetEditorState(bpy.types.PropertyGroup):
    width: bpy.props.FloatProperty(name="Largura", subtype='DISTANCE', unit='LENGTH',
                                   get=_dim_get('width'), set=_dim_set('width'))  # type: ignore
    height: bpy.props.FloatProperty(name="Altura", subtype='DISTANCE', unit='LENGTH',
                                    get=_dim_get('height'), set=_dim_set('height'))  # type: ignore
    depth: bpy.props.FloatProperty(name="Profundidade", subtype='DISTANCE', unit='LENGTH',
                                   get=_dim_get('depth'), set=_dim_set('depth'))  # type: ignore
    components: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorComponent)  # type: ignore
    component_index: bpy.props.IntProperty(default=-1, update=_index_update)  # type: ignore
    messages: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorMessage)  # type: ignore
    adjustments: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorAdjustment)  # type: ignore
    # Feature 006
    tab: bpy.props.EnumProperty(name="Aba", items=TAB_ITEMS, default='STRUCTURE')  # type: ignore
    new_orientation: bpy.props.EnumProperty(
        name="Orientação", items=[('VERTICAL', "Vertical", "Chapa em pé: separa esquerda e direita", 'SNAP_EDGE', 0),
                                  ('HORIZONTAL', "Horizontal", "Chapa deitada: separa cima e baixo", 'SNAP_FACE',
                                   1)])  # type: ignore
    new_use_front: bpy.props.BoolProperty(name="Recuo na frente", default=False)  # type: ignore
    new_front: bpy.props.FloatProperty(name="Recuo da frente", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                       min=0.0, max=1.0)  # type: ignore
    new_use_back: bpy.props.BoolProperty(name="Recuo atrás", default=False)  # type: ignore
    new_back: bpy.props.FloatProperty(name="Recuo de trás", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                      min=0.0, max=1.0)  # type: ignore
    space: bpy.props.EnumProperty(name="Vão", items=_space_items, get=_space_get, set=_space_set)  # type: ignore
    structure: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorStructureRow)  # type: ignore
    structure_index: bpy.props.IntProperty(default=-1)  # type: ignore
    divisions: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorDivisionRow)  # type: ignore
    division_index: bpy.props.IntProperty(default=-1)  # type: ignore


classes = (BTM_PG_CabinetEditorComponent, BTM_PG_CabinetEditorMessage, BTM_PG_CabinetEditorAdjustment,
           BTM_PG_CabinetEditorStructureRow, BTM_PG_CabinetEditorDivisionRow, BTM_PG_CabinetEditorState)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_cabinet_editor = bpy.props.PointerProperty(type=BTM_PG_CabinetEditorState)


def unregister():
    end()
    if hasattr(bpy.types.WindowManager, 'btm_cabinet_editor'):
        del bpy.types.WindowManager.btm_cabinet_editor
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
