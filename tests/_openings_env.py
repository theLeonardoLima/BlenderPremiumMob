"""Caixa de porta ou janela montada como o modal de colocação monta (`doors_windows._PlaceWallObjectBase`), sem a
interação: caixa `GeoNodeCage` com a bandeira, o símbolo 2D (portas) e o texto. Usado pelas fumaças da feature 010."""

import math

import bpy

from caffmob_draw import hb_types
from caffmob_draw.hb_details import GeoNodeText
from caffmob_draw.operators import doors_windows as dw


def make_cage(kind='DOOR', leaf_w=0.80, leaf_h=2.10, wall=0.15, inside=True, left=False, location=(0, 0, 0),
              window_w=1.2, window_h=1.0):
    cage = hb_types.GeoNodeCage()
    window = kind == 'WINDOW'
    cage.create("Window" if window else "Door")
    cage.obj['IS_WINDOW_BP' if window else 'IS_ENTRY_DOOR_BP'] = True
    cage.set_input('Dim X', window_w if window else dw._leaf_to_hole(kind, 'X', leaf_w * (2 if kind == 'DOUBLE_DOOR' else 1)))
    cage.set_input('Dim Y', wall)
    cage.set_input('Dim Z', window_h if window else dw._leaf_to_hole(kind, 'Z', leaf_h))
    cage.obj.btm_opening_real.kind = kind
    cage.obj.location = location
    if kind in ('DOOR', 'DOUBLE_DOOR'):
        swing = hb_types.GeoNodeDoorSwing()
        swing.create('Door Swing Annotation')
        swing.obj.parent = cage.obj
        swing.set_input('Dim X', cage.get_input('Dim X'))
        swing.set_input('Dim Y', wall)
        swing.set_input('Swing Inside', inside)
        swing.set_input('Is Left', left)
        swing.set_input('Is Double', kind == 'DOUBLE_DOOR')
    text = GeoNodeText()
    text.create("Window Text" if window else "Door Text", "WINDOW" if window else "DOOR", 0.1)
    text.obj.parent = cage.obj
    text.obj.rotation_euler.x = math.radians(90)
    bpy.context.view_layer.update()
    return cage.obj
