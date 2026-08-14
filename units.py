"""
BlenderToMob Units System — Conversão e Formatação de Medidas Métricas e Imperiais
Suporta Milímetros (mm), Centímetros (cm), Metros (m), Polegadas (in) e Pés (ft).
"""

import bpy  # type: ignore

# Fatores de conversão para metros (unidade base do Blender)
UNIT_CONVERSION_TO_METERS = {
    'MM': 0.001,
    'MILLIMETERS': 0.001,
    'CM': 0.01,
    'CENTIMETERS': 0.01,
    'M': 1.0,
    'METERS': 1.0,
    'IN': 0.0254,
    'INCHES': 0.0254,
    'FT': 0.3048,
    'FEET': 0.3048,
}

UNIT_LABELS = {
    'MM': 'mm',
    'MILLIMETERS': 'mm',
    'CM': 'cm',
    'CENTIMETERS': 'cm',
    'M': 'm',
    'METERS': 'm',
    'IN': 'in',
    'INCHES': '"',
    'FT': 'ft',
    'FEET': "'",
}


def to_meters(value, unit='MM'):
    """Converte um valor da unidade fornecida para metros (unidade interna do Blender)."""
    scale = UNIT_CONVERSION_TO_METERS.get(unit.upper(), 0.001)
    return value * scale


def from_meters(value_in_meters, unit='MM'):
    """Converte um valor em metros (unidade interna do Blender) para a unidade fornecida."""
    scale = UNIT_CONVERSION_TO_METERS.get(unit.upper(), 0.001)
    if scale == 0:
        return value_in_meters
    return value_in_meters / scale


def get_scene_length_unit(scene=None):
    """Detecta a unidade de comprimento ativa nas configurações de cena do Blender."""
    if scene is None:
        scene = bpy.context.scene if hasattr(bpy, 'context') and hasattr(bpy.context, 'scene') else None
    if not scene:
        return 'MM'

    # Verifica se a cena tem propriedade customizada do add-on
    if hasattr(scene, 'btm_settings') and hasattr(scene.btm_settings, 'btm_unit'):
        u = scene.btm_settings.btm_unit
        if u == 'MILLIMETERS':
            return 'MM'
        elif u == 'CENTIMETERS':
            return 'CM'
        elif u == 'METERS':
            return 'M'

    unit_settings = scene.unit_settings
    if unit_settings.system == 'METRIC':
        length_unit = unit_settings.length_unit
        if length_unit == 'MILLIMETERS':
            return 'MM'
        elif length_unit == 'CENTIMETERS':
            return 'CM'
        elif length_unit == 'METERS':
            return 'M'
    return 'MM'


def format_number(value):
    """Formata um número removendo zeros redundantes."""
    rounded = round(value, 3)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip('0').rstrip('.')


def format_value(value_in_meters, scene=None, unit=None):
    """Formata um valor em metros para exibição na UI com o sufixo correto."""
    if unit is None:
        unit = get_scene_length_unit(scene)
    val = from_meters(value_in_meters, unit)
    label = UNIT_LABELS.get(unit.upper(), 'mm')
    return f"{format_number(val)} {label}"


# Aliases legados para compatibilidade reversa
def inch(value):
    return value * 0.0254

def feet(value):
    return value * 0.3048

def millimeter(value):
    return value * 0.001

def centimeter(value):
    return value * 0.01

def meter_to_inch(value):
    return round(value * 39.3701, 6)

def meter_to_millimeter(meter):
    return meter * 1000.0

def meter_to_feet(meter):
    return round(meter * 3.28084, 6)

def convert_to_meters(value, unit_code='MM'):
    return to_meters(value, unit_code)

def convert_from_meters(meters_val, unit_code='MM'):
    return from_meters(meters_val, unit_code)

def format_length_unit(meters_val, unit_code='MM'):
    return format_value(meters_val, unit=unit_code)
