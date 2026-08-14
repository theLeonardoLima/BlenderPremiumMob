#!/usr/bin/env python3
"""
Test suite for BlenderToMob Nesting, Part Extraction, JSON Export and Units
"""

import sys
import os
import json
from unittest.mock import MagicMock

# Mock bpy if running outside Blender
if 'bpy' not in sys.modules:
    class MockOperator:
        pass
    class MockPropertyGroup:
        pass
    class MockPanel:
        pass
    class MockPreferences:
        pass
    class MockExportHelper:
        pass

    mock_bpy = MagicMock()
    mock_bpy.app.version = (5, 2, 0)
    mock_bpy.types.Operator = MockOperator
    mock_bpy.types.PropertyGroup = MockPropertyGroup
    mock_bpy.types.Panel = MockPanel
    mock_bpy.types.AddonPreferences = MockPreferences
    sys.modules['bpy'] = mock_bpy
    sys.modules['bpy.types'] = mock_bpy.types
    sys.modules['bpy.props'] = MagicMock()
    sys.modules['bpy.app.handlers'] = MagicMock()
    sys.modules['bpy.utils'] = MagicMock()
    sys.modules['bpy.utils.previews'] = MagicMock()
    sys.modules['bpy_extras'] = MagicMock()
    mock_io = MagicMock()
    mock_io.ExportHelper = MockExportHelper
    sys.modules['bpy_extras.io_utils'] = mock_io
    sys.modules['bpy_extras.view3d_utils'] = MagicMock()
    sys.modules['bmesh'] = MagicMock()
    mock_math = MagicMock()
    sys.modules['mathutils'] = mock_math
    sys.modules['mathutils.geometry'] = MagicMock()
    sys.modules['gpu'] = MagicMock()
    sys.modules['gpu_extras'] = MagicMock()
    sys.modules['gpu_extras.batch'] = MagicMock()
    sys.modules['blf'] = MagicMock()

from blendertomob.cutting.nesting import NestingPart, optimize_nesting
from blendertomob.cutting.json_exporter import export_cut_plan_to_json
from blendertomob.data.dimensions_preset import DIMENSION_PRESETS
from blendertomob.data import units

def test_units():
    print("Testing Units...")
    assert units.to_meters(1000.0, 'MM') == 1.0
    assert units.to_meters(100.0, 'CM') == 1.0
    assert units.to_meters(1.0, 'M') == 1.0
    assert units.from_meters(1.0, 'MM') == 1000.0
    assert units.from_meters(1.0, 'CM') == 100.0
    assert "1000 mm" in units.format_value(1.0, unit='MM')
    assert "100 cm" in units.format_value(1.0, unit='CM')
    assert "1 m" in units.format_value(1.0, unit='M')
    print("✓ Units test passed!")

def test_dimension_presets():
    print("Testing Dimension Presets...")
    assert 'COZINHA_INFERIOR' in DIMENSION_PRESETS
    assert 'COZINHA_AEREO' in DIMENSION_PRESETS
    assert 'DORMITORIO_ROUPEIRO' in DIMENSION_PRESETS
    assert 'BANHEIRO_GABINETE' in DIMENSION_PRESETS
    assert 'PROMOB_STANDARD' in DIMENSION_PRESETS
    p = DIMENSION_PRESETS['PROMOB_STANDARD']
    assert p['carcass_thickness'] == 0.015
    assert p['back_thickness'] == 0.006
    print("✓ Dimension presets test passed!")

def test_nesting_and_json_export():
    print("Testing Nesting & JSON Exporter...")
    parts = [
        NestingPart(id="MOD1_LAT_ESQ", name="Lateral Esquerda", width=550, height=720, quantity=2, thickness=15, material="MDF Branco", grain_direction='VERTICAL', module_ref="Balcao_01", edge_right=1.0),
        NestingPart(id="MOD1_BASE", name="Base", width=770, height=550, quantity=2, thickness=15, material="MDF Branco", grain_direction='HORIZONTAL', module_ref="Balcao_01", edge_right=1.0),
        NestingPart(id="MOD1_PRAT", name="Prateleira", width=768, height=530, quantity=1, thickness=15, material="MDF Branco", grain_direction='HORIZONTAL', module_ref="Balcao_01", edge_right=1.0),
        NestingPart(id="MOD1_FUNDO", name="Fundo Traseiro", width=786, height=706, quantity=1, thickness=6, material="MDF 6mm Branco", grain_direction='VERTICAL', module_ref="Balcao_01"),
        NestingPart(id="MOD1_PORTAS", name="Portas", width=396, height=716, quantity=2, thickness=18, material="MDF Louro Freijo", grain_direction='VERTICAL', module_ref="Balcao_01", edge_top=1.0, edge_bottom=1.0, edge_left=1.0, edge_right=1.0),
    ]

    result = optimize_nesting(
        parts=parts,
        sheet_width=2750.0,
        sheet_height=1830.0,
        refilo_top=10.0,
        refilo_bottom=10.0,
        refilo_left=10.0,
        refilo_right=10.0,
        kerf=4.0,
        allow_rotation=True,
        respect_grain=True
    )

    stats = result["stats"]
    print(f"  Nesting Stats: {stats['sheets_count']} sheets, {stats['total_placed_parts']} placed parts, {stats['utilization_percentage']}% utilization.")
    assert stats["sheets_count"] >= 1
    assert stats["total_placed_parts"] == 8
    assert stats["unplaced_count"] == 0

    # Test JSON export
    test_json_path = "/tmp/test_blendertomob_cut_plan.json"
    export_cut_plan_to_json(test_json_path, result, parts, project_name="Cozinha Residencial Teste")
    
    assert os.path.exists(test_json_path)
    with open(test_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data["generator"] == "BlenderToMob (Blender 5.2.0)"
    assert data["project"]["name"] == "Cozinha Residencial Teste"
    assert len(data["sheets"]) >= 1
    assert len(data["parts_catalog"]) == 5
    print("✓ Nesting & JSON export test passed!")

if __name__ == "__main__":
    test_units()
    test_dimension_presets()
    test_nesting_and_json_export()
    print("\nALL TESTS PASSED SUCCESSFULLY! 🚀")
