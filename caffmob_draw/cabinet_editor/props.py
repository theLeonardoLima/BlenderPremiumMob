"""Estado do Editor de Armário (feature 004, T014; data-delta §1.5, D-21, D-22).

- `Session` (em memória, uma por vez): raiz do módulo, rascunho (`state.Draft`), peças da vista frontal, componente
  selecionado, mensagens, ajustes automáticos, vista 2D, janela/área e os pedidos que o modal executa.
- `WindowManager.btm_cabinet_editor`: campos do painel. As medidas são virtuais (`get`/`set`): o `set` só registra um
  pedido na sessão; quem edita o módulo é o modal (D-22), para o Blender criar um passo de desfazer só no Confirmar.
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


classes = (BTM_PG_CabinetEditorComponent, BTM_PG_CabinetEditorMessage, BTM_PG_CabinetEditorAdjustment,
           BTM_PG_CabinetEditorState)


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
