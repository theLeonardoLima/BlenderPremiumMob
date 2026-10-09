"""Interface da biblioteca de objetos (feature 009, T030; D-14, /impeccable).

Mesmo padrão visual do catálogo da 008: categorias numa fileira de ícones com o nome da ativa, busca, grade de duas
colunas com a miniatura e o nome, e um estado vazio escrito. O tooltip de cada item diz se ele vem com o plugin ou é
seu. Embaixo: Acrescentar à biblioteca. Na seção Selecionado: Retexturizar.
"""

from ..data.i18n import tr
from . import catalog, item_io, previews, store


def draw_insert(layout, context):
    ui = context.window_manager.btm_object_library
    row = layout.row(align=True)
    row.prop_tabs_enum(ui, "category", icon_only=True)
    labels = {key: label for key, label, _icon in catalog.CATEGORIES}
    layout.label(text=tr(labels[ui.category]))
    layout.prop(ui, "search", text="", icon='VIEWZOOM')
    items, warnings = item_io.all_items()
    shown = [i for i in store.by_category(items, ui.category) if i.entry in catalog.search([i.entry], ui.search)]
    if not shown:
        hint = layout.row()
        hint.active = False
        hint.label(text=tr("Nenhum objeto nesta categoria") if not ui.search else tr("Nenhum objeto com esse nome"))
    grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, align=False)
    for item in shown:
        cell = grid.column(align=True)
        icon = previews.icon_id(item.thumb)
        if icon:
            cell.template_icon(icon_value=icon, scale=4.0)
        else:
            cell.label(text="", icon='MESH_CUBE')
        row = cell.row(align=True)
        op = row.operator("caffmob.object_insert", text=item.entry.name)
        op.key = _key(item)
        if item.user:
            row.operator("caffmob.object_library_remove", text="", icon='X').key = _key(item)
    if warnings:
        hint = layout.row()
        hint.active = False
        hint.label(text=tr("{} arquivo(s) da biblioteca ignorado(s)").format(len(warnings)), icon='ERROR')
    row = layout.row()
    row.scale_y = 1.2
    row.operator("caffmob.object_library_add", text=tr("Acrescentar à biblioteca"), icon='ADD')


def _key(item):
    from .ops import item_key
    return item_key(item)


def draw_retexture(layout, context):
    col = layout.column(align=True)
    for scope, text in (('PART', tr("Parte selecionada")), ('ITEM', tr("Item inteiro"))):
        row = col.row(align=True)
        row.label(text=text)
        row.operator("caffmob.object_retexture_finish", text=tr("Acabamento"), icon='MATERIAL').scope = scope
        row.operator("caffmob.object_retexture_image", text=tr("Imagem"), icon='IMAGE_DATA').scope = scope
