"""Camada falsa que imita o `UILayout` para inventariar a barra lateral (feature 005, T001; D-11). Sem `bpy`.

Um painel desenhado com uma `Probe` no lugar de `self.layout` não desenha nada: cada `operator`, `menu` e `prop` vira
um registro com a seção de origem. Os testes usam isso para provar que nenhuma ação sumiu (inventário) e que nenhum
operador aparece em duas seções (não repetição). `panel`/`panel_prop` devolvem o corpo aberto, para inventariar também
o conteúdo recolhido.
"""

from contextlib import contextmanager


class OperatorProps:
    """O que `layout.operator(...)` devolve: aceita qualquer atributo (`op.kind = 'PLACA'`)."""

    def __init__(self, record):
        object.__setattr__(self, '_record', record)

    def __setattr__(self, name, value):
        self._record['args'][name] = value

    def __getattr__(self, name):
        return self._record['args'].get(name)


class Recorder:
    def __init__(self):
        self.records = []
        self._path = []

    @contextmanager
    def section(self, name):
        self._path.append(name)
        try:
            yield
        finally:
            self._path.pop()

    def add(self, kind, name, **extra):
        record = {'kind': kind, 'name': name, 'section': " › ".join(self._path), 'args': {}}
        record.update(extra)
        self.records.append(record)
        return record

    def operators(self):
        return [r for r in self.records if r['kind'] == 'operator']


class Probe:
    """Imita o `UILayout`. Atributos de estado (`enabled`, `alert`, `scale_y`…) são aceitos e guardados."""

    def __init__(self, recorder=None):
        object.__setattr__(self, 'recorder', recorder or Recorder())
        object.__setattr__(self, '_attrs', {'operator_context': 'INVOKE_DEFAULT', 'enabled': True, 'active': True})

    # Estado ----------------------------------------------------------------------------------------------
    def __setattr__(self, name, value):
        self._attrs[name] = value

    def __getattr__(self, name):
        if name in self._attrs:
            return self._attrs[name]
        # Qualquer método desconhecido (`template_*`, `context_pointer_set`, `use_property_*`…) é aceito.
        return self._noop

    def _noop(self, *args, **kwargs):
        return self._child()

    def _child(self):
        return Probe(self.recorder)

    # Estrutura -------------------------------------------------------------------------------------------
    def row(self, *args, **kwargs):
        return self._child()

    def column(self, *args, **kwargs):
        return self._child()

    def box(self, *args, **kwargs):
        return self._child()

    def split(self, *args, **kwargs):
        return self._child()

    def grid_flow(self, *args, **kwargs):
        return self._child()

    def column_flow(self, *args, **kwargs):
        return self._child()

    def panel(self, idname, *args, **kwargs):
        return self._child(), self._child()

    def panel_prop(self, data, prop, *args, **kwargs):
        return self._child(), self._child()

    def separator(self, *args, **kwargs):
        return None

    def separator_spacer(self, *args, **kwargs):
        return None

    def label(self, *args, **kwargs):
        return None

    # O que conta no inventário -----------------------------------------------------------------------------
    def operator(self, idname, *args, **kwargs):
        record = self.recorder.add('operator', idname, text=kwargs.get('text'))
        return OperatorProps(record)

    def operator_menu_enum(self, idname, prop, *args, **kwargs):
        record = self.recorder.add('operator', idname, text=kwargs.get('text'))
        return OperatorProps(record)

    def operator_enum(self, idname, prop, *args, **kwargs):
        self.recorder.add('operator', idname)
        return None

    def menu(self, menu, *args, **kwargs):
        self.recorder.add('menu', menu)
        return None

    def menu_contents(self, menu, *args, **kwargs):
        self.recorder.add('menu', menu)
        return None

    def popover(self, panel, *args, **kwargs):
        self.recorder.add('popover', panel)
        return None

    def prop(self, data, prop, *args, **kwargs):
        self.recorder.add('prop', prop, owner=type(data).__name__)
        return None

    def prop_enum(self, data, prop, value, *args, **kwargs):
        self.recorder.add('prop', prop, owner=type(data).__name__, value=value)
        return None

    def prop_search(self, data, prop, *args, **kwargs):
        self.recorder.add('prop', prop, owner=type(data).__name__)
        return None

    def props_enum(self, data, prop, *args, **kwargs):
        self.recorder.add('prop', prop, owner=type(data).__name__)
        return None


def operator_sections(recorder):
    """{bl_idname: sorted([seções])} a partir dos registros."""
    out = {}
    for record in recorder.operators():
        out.setdefault(record['name'], set()).add(record['section'])
    return {name: sorted(sections) for name, sections in out.items()}
