import bpy

# Cache de identificadores de entrada resolvidos por grupo de nós de geometria.
_INPUT_IDENT_CACHE = {}

# Blender 5.2.0+ alterou o acesso aos inputs de modificadores de Geometry Nodes.
# Em 5.2.0+: mod.properties.inputs[identifier].value
# Em < 5.2.0: mod[identifier]
GN_INPUTS_AS_RNA = bpy.app.version >= (5, 2, 0)


def _get_input_identifier(node_group, input_name):
    """Retorna o identificador do socket do modificador para um determinado input_name.
    Usa um cache na memória para evitar chamar interface_update repetidamente.
    """
    group_cache = _INPUT_IDENT_CACHE.get(id(node_group))
    if group_cache is not None:
        ident = group_cache.get(input_name)
        if ident is not None:
            return ident
    else:
        group_cache = {}
        _INPUT_IDENT_CACHE[id(node_group)] = group_cache

    if input_name not in node_group.interface.items_tree:
        raise ValueError(f"Input '{input_name}' não encontrado no Geometry Nodes")

    # Garante que a interface do modificador está atualizada com o grupo de nós
    if hasattr(node_group, 'interface_update'):
        node_group.interface_update(bpy.context)
        
    ident = node_group.interface.items_tree[input_name].identifier
    group_cache[input_name] = ident
    return ident


def _invalidate_input_cache(node_group):
    """Limpa o cache de identificadores do grupo de nós."""
    _INPUT_IDENT_CACHE.pop(id(node_group), None)


def get_gn_input(mod, input_name):
    """Lê de forma compatível o valor de uma entrada (socket) de um modificador de Geometry Nodes."""
    if not mod or not mod.node_group:
        return None
    try:
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            return getattr(mod.properties.inputs, ident).value
        return mod[ident]
    except (KeyError, AttributeError):
        _invalidate_input_cache(mod.node_group)
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            return getattr(mod.properties.inputs, ident).value
        return mod[ident]


def set_gn_input(mod, input_name, value):
    """Escreve de forma compatível um valor em uma entrada (socket) de um modificador de Geometry Nodes."""
    if not mod or not mod.node_group:
        return
    try:
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            getattr(mod.properties.inputs, ident).value = value
        else:
            mod[ident] = value
    except (KeyError, AttributeError):
        _invalidate_input_cache(mod.node_group)
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            getattr(mod.properties.inputs, ident).value = value
        else:
            mod[ident] = value
    # Tag de atualização do objeto para reavaliação no depsgraph
    mod.id_data.update_tag()


def gn_input_data_path(mod, input_name):
    """Retorna o caminho de dados (data path) de animação/driver para uma entrada do Geometry Nodes."""
    if not mod or not mod.node_group:
        return ""
    ident = _get_input_identifier(mod.node_group, input_name)
    if GN_INPUTS_AS_RNA:
        return f'modifiers["{mod.name}"].properties.inputs.{ident}.value'
    return f'modifiers["{mod.name}"]["{ident}"]'
