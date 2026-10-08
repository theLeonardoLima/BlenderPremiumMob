"""Importar modelo 3D externo (feature 003, T047; RF-11, D-16).

Chama o importador do próprio Blender pelo tipo do arquivo (OBJ, FBX, glTF/GLB). Objetos trazidos por outros addons
(por exemplo, um importador de SketchUp) também podem ser convertidos: a conversão aceita qualquer malha da cena.

Feature 007 (T014; RN-01, D-01, D-02): **Unidade** do arquivo (Automática, mm, cm, m, pol) e **Eixo vertical** (Z, Y).
O OBJ e o FBX recebem o eixo no importador; a escala é aplicada depois, sobre as raízes importadas, para a Automática
poder medir o modelo em escala 1 (mais de 50 unidades = mm). O glTF já é métrico e Y-up por especificação.
"""

import os

import bpy  # type: ignore
from bpy_extras.io_utils import ImportHelper  # type: ignore
from mathutils import Matrix  # type: ignore

from ..data.i18n import tr
from . import import_units

UNIT_ITEMS = [('AUTO', "Automática", "Mede o modelo: mais de 50 unidades numa medida = milímetros"),
              ('MM', "Milímetros", ""), ('CM', "Centímetros", ""), ('M', "Metros", ""), ('IN', "Polegadas", "")]
UP_ITEMS = [('Z', "Z", "O arquivo usa Z para cima (SketchUp, Promob, a maioria dos CAD)"),
            ('Y', "Y", "O arquivo usa Y para cima (padrão do OBJ do Blender, glTF)")]

FORMATS = {'.obj': ('wm', 'obj_import'), '.fbx': ('import_scene', 'fbx'), '.glb': ('import_scene', 'gltf'),
           '.gltf': ('import_scene', 'gltf')}


class BTM_OT_ImportModel(bpy.types.Operator, ImportHelper):
    """Importa um modelo 3D (OBJ, FBX, glTF/GLB) para converter em agregado ou folha de porta"""
    bl_idname = "caffmob.import_model"
    bl_label = "Importar modelo 3D"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.obj;*.fbx;*.glb;*.gltf", options={'HIDDEN'})  # type: ignore
    unit: bpy.props.EnumProperty(name="Unidade do arquivo", items=UNIT_ITEMS, default='AUTO')  # type: ignore
    up_axis: bpy.props.EnumProperty(name="Eixo vertical", items=UP_ITEMS, default='Z')  # type: ignore

    def _kwargs(self, ext):
        if ext == '.obj':
            return {'up_axis': self.up_axis, 'forward_axis': 'Y' if self.up_axis == 'Z' else 'NEGATIVE_Z'}
        if ext == '.fbx':
            return {'axis_up': self.up_axis, 'axis_forward': 'Y' if self.up_axis == 'Z' else '-Z'}
        return {}

    def execute(self, context):
        ext = os.path.splitext(self.filepath)[1].lower()
        target = FORMATS.get(ext)
        if target is None:
            self.report({'ERROR'}, tr("Formato não suportado: {} (use OBJ, FBX, glTF ou GLB)").format(ext or tr("sem extensão")))
            return {'CANCELLED'}
        before = set(bpy.data.objects)
        operator = getattr(getattr(bpy.ops, target[0]), target[1])
        try:
            result = operator(filepath=self.filepath, **self._kwargs(ext))
        except RuntimeError as exc:
            self.report({'ERROR'}, tr("O Blender não conseguiu importar {}: {}").format(os.path.basename(self.filepath), exc))
            return {'CANCELLED'}
        if 'FINISHED' not in result:
            self.report({'ERROR'}, tr("Importação cancelada: {}").format(os.path.basename(self.filepath)))
            return {'CANCELLED'}
        new = [obj for obj in bpy.data.objects if obj not in before]
        meshes = [obj for obj in new if obj.type == 'MESH']
        unit = self._apply_unit(context, new, ext)
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in meshes:
            obj.select_set(True)
        if meshes:
            context.view_layer.objects.active = meshes[0]
        self.report({'INFO'}, tr("{} malha(s) importada(s), unidade: {}. Selecione o pai por último e use "
                                 "\"Converter em agregado\" ou \"Montar esquadria\"").format(len(meshes), unit))
        return {'FINISHED'}


    def _apply_unit(self, context, new, ext):
        """Escala as raízes importadas para metros; devolve o nome da unidade usada."""
        if ext in ('.glb', '.gltf') and self.unit == 'AUTO':
            return "m"
        context.view_layer.update()
        from . import group
        box = group.world_box(new)
        largest = max(box[1][i] - box[0][i] for i in range(3)) if box else 0.0
        factor = import_units.scale_for(self.unit, largest)
        if abs(factor - 1.0) > 1e-12:
            pivot = Matrix.Scale(factor, 4)
            for obj in new:
                if obj.parent is None or obj.parent not in new:
                    obj.matrix_world = pivot @ obj.matrix_world
            for obj in new:                    # a escala vai para a malha: peças com escala 1 (D-01)
                if obj.type == 'MESH' and obj.data.users == 1:
                    obj.data.transform(Matrix.Diagonal((*obj.scale, 1.0)))
                    obj.scale = (1.0, 1.0, 1.0)
        unit = 'AUTO' if self.unit == 'AUTO' else self.unit
        return {'MM': "mm", 'CM': "cm", 'M': "m", 'IN': "pol"}[import_units.suggest(largest) if unit == 'AUTO'
                                                                else unit]


classes = (BTM_OT_ImportModel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
