import sys, bpy
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env as env
from caffmob_draw.selection import classify
from caffmob_draw.walls2d import scene_io
ctx=bpy.context
cube=bpy.data.objects.get('Cube'); print("cube", cube is not None, cube and cube.btm_plane.object_kind, cube and cube.btm_plane.is_property_set('object_kind'))
print("classify cube", classify.classify(cube))
print("is_other_layer_wall", scene_io.is_other_layer_wall(cube))
print("insert_opening poll", bpy.types.Operator.bl_rna_get_subclass_py('CAFFMOB_OT_insert_opening').poll(ctx))
cube.btm_plane.object_kind='WALL'; print("depois de setar", cube.btm_plane.is_property_set('object_kind'))
