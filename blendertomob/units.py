def inch(value):
    """ Converts inch to meter
    """
    return value * 0.0254

def feet(value):
    """ Converts feet to meter
    """
    return value * 0.3048

def millimeter(value):
    """ Converts millimeter to meter
    """
    return value * .001

def centimeter(value):
    """ Converts centimeter to meter
    """
    return value * .01

def meter_to_inch(value):
    """ Converts meter to inch
    """
    return round(value * 39.3701,6)

def meter_to_millimeter(meter):
    """ Converts meter to millimeter
    """
    return meter * 1000

def meter_to_feet(meter):
    """ Converts meter to feet
    """
    return round(meter * 3.28084,6)

def round_to_sixteenth(value):
    """Round a value to the nearest 1/16 (0.0625)."""
    return round(value * 16) / 16

def format_number(value):
    """Format a number, removing unnecessary trailing zeros."""
    # Round to 4 decimal places to clean up floating point noise
    rounded = round(value, 4)
    # Format and strip trailing zeros
    if rounded == int(rounded):
        return str(int(rounded))
    else:
        return f"{rounded:.4f}".rstrip('0').rstrip('.')

def unit_to_string(unit_settings, value):
    if unit_settings.system == 'METRIC':
        if unit_settings.length_unit == 'METERS':
            return format_number(round(value, 3)) + "m"
        else:
            return format_number(round(meter_to_millimeter(value), 2)) + "mm"
    elif unit_settings.system == 'IMPERIAL':
        if unit_settings.length_unit == 'FEET':
            return format_number(round(meter_to_feet(value), 2)) + "'"
        else:
            # Round to nearest 1/16" for clean cabinet dimensions
            inches = meter_to_inch(value)
            rounded_inches = round_to_sixteenth(inches)
            return format_number(rounded_inches) + '"'
    else:
        return format_number(round(value, 4))


# =============================================================================
# DYNAMIC UNIT CONVERSION HELPERS (mm, cm, m, in, ft)
# =============================================================================

UNIT_CONVERSION_TO_METERS = {
    'MM': 0.001,
    'CM': 0.01,
    'M': 1.0,
    'IN': 0.0254,
    'FT': 0.3048,
}

UNIT_LABELS = {
    'MM': 'mm',
    'CM': 'cm',
    'M': 'm',
    'IN': 'in',
    'FT': 'ft',
}


def convert_to_meters(value, unit_code='MM'):
    """Convert a value in unit_code ('MM','CM','M','IN','FT') to meters."""
    scale = UNIT_CONVERSION_TO_METERS.get(unit_code.upper(), 0.001)
    return value * scale


def convert_from_meters(meters_val, unit_code='MM'):
    """Convert a value in meters to unit_code ('MM','CM','M','IN','FT')."""
    scale = UNIT_CONVERSION_TO_METERS.get(unit_code.upper(), 0.001)
    if scale == 0:
        return meters_val
    return meters_val / scale


def format_length_unit(meters_val, unit_code='MM'):
    """Format a value in meters into a string in unit_code representation."""
    code = unit_code.upper()
    val = convert_from_meters(meters_val, code)
    label = UNIT_LABELS.get(code, 'mm')
    if code in ('MM', 'CM'):
        return f"{format_number(round(val, 2))} {label}"
    elif code == 'M':
        return f"{format_number(round(val, 3))} {label}"
    elif code == 'IN':
        return f"{format_number(round(val, 3))} {label}"
    elif code == 'FT':
        return f"{format_number(round(val, 3))} {label}"
    return f"{format_number(round(val, 3))} {label}"
