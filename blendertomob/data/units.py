import bpy

def to_meters(value, unit='MM'):
    """Converte um valor da unidade fornecida para metros (unidade interna do Blender)."""
    if unit == 'M':
        return value
    elif unit == 'CM':
        return value * 0.01
    elif unit == 'MM':
        return value * 0.001
    return value


def from_meters(value, unit='MM'):
    """Converte um valor em metros (unidade interna do Blender) para a unidade fornecida."""
    if unit == 'M':
        return value
    elif unit == 'CM':
        return value * 100.0
    elif unit == 'MM':
        return value * 1000.0
    return value


def get_scene_length_unit(scene):
    """Detecta a unidade de comprimento ativa nas configurações de cena do Blender."""
    unit_settings = scene.unit_settings
    if unit_settings.system == 'METRIC':
        length_unit = unit_settings.length_unit
        if length_unit == 'MILLIMETERS':
            return 'MM'
        elif length_unit == 'CENTIMETERS':
            return 'CM'
        elif length_unit == 'METERS':
            return 'M'
    return 'MM' # Padrão fallback para marcenaria


def format_value(value_in_meters, scene=None):
    """Formata um valor em metros para exibição na interface do usuário com o sufixo correto."""
    if scene is None:
        scene = bpy.context.scene
    unit = get_scene_length_unit(scene)
    val = from_meters(value_in_meters, unit)
    
    # Remove zeros redundantes na formatação
    rounded = round(val, 3)
    if rounded == int(rounded):
        val_str = str(int(rounded))
    else:
        val_str = f"{rounded:.3f}".rstrip('0').rstrip('.')
        
    if unit == 'MM':
        return f"{val_str} mm"
    elif unit == 'CM':
        return f"{val_str} cm"
    elif unit == 'M':
        return f"{val_str} m"
    return f"{val_str}"
