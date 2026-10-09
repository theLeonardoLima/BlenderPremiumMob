"""Gera uma porta de madeira em escala métrica, OBJ/MTL e cena de apresentação."""
from pathlib import Path
import math
import json
import bpy
import numpy as np
from mathutils import Vector, Matrix

OUT = Path(__file__).resolve().parent
# Execução dedicada em background; não altera a sessão interativa.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
asset = bpy.data.collections.new('PORTA_080x210')
scene.collection.children.link(asset)
leaf = []

def material(name, color, metal=0, rough=.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    m.diffuse_color = (*color, 1)
    return m

# Texturas raster transportáveis pelo OBJ: veios alongados e poros discretos.
rng = np.random.default_rng(42)
w, h = 1024, 2048
u, v = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
warp = u + .018*np.sin(v*13+u*8) + .010*np.sin(v*29+u*14)
grain = .5+.5*np.sin(warp*790 + 2*np.sin(warp*70))
broad = np.interp(warp.ravel(), np.linspace(-.1,1.1,280), rng.random(280)).reshape(h,w)
fine = rng.random((h,w))
shade = .79 + .08*broad + .018*grain + .018*fine
pores = (grain>.975)*(.4+.6*fine)*.055
rgb = np.stack([.43*shade-pores, .265*shade-pores*.7, .137*shade-pores*.4], axis=-1)

def image_file(name, pixels):
    im = bpy.data.images.new(name, width=w, height=h)
    rgba = np.ones((h,w,4), dtype=np.float32)
    rgba[:,:,:3] = pixels if pixels.ndim==3 else pixels[:,:,None]
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = str(OUT/name)
    im.file_format = 'PNG'
    im.save()
    return im

color = image_file('nogueira_cor.png', rgb)
rough = image_file('nogueira_rugosidade.png', .33+.12*(1-grain)+.025*fine)
rough.colorspace_settings.name='Non-Color'
wood = material('Nogueira_verniz_acetinado', (.32,.18,.075))
nt=wood.node_tree
p=nt.nodes.get('Principled BSDF')
p.inputs['Coat Weight'].default_value=.18
p.inputs['Coat Roughness'].default_value=.3
for im, socket in [(color,'Base Color'),(rough,'Roughness')]:
    tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=im
    nt.links.new(tex.outputs['Color'],p.inputs[socket])
bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.025; bump.inputs['Distance'].default_value=.00022
nt.links.new(tex.outputs['Color'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
metal=material('Aco_inox_escovado',(.46,.49,.51),1,.27)
dark=material('Borracha_EPDM',(.012,.016,.014),0,.68)
slot=material('Cavidades_ferragens',(.019,.022,.025),.6,.42)
brass=material('Lingueta_latao',(.48,.30,.10),.85,.3)


def finish(o, name, mat, bevel, moving=False, horizontal=False):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    asset.objects.link(o)
    o.data.materials.append(mat)
    if mat==wood:
        uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
        offset=(sum(ord(c) for c in name)%97)/97
        for poly in o.data.polygons:
            for li in poly.loop_indices:
                co=o.data.vertices[o.data.loops[li].vertex_index].co
                if abs(poly.normal.y)>.5:
                    a,b=(co.z,co.x) if horizontal else (co.x,co.z)
                elif abs(poly.normal.x)>.5: a,b=co.y,co.z
                else: a,b=co.x,co.y
                uv.data[li].uv=(a/.45+offset,b/2.3+offset*.3)
    if bevel:
        m=o.modifiers.new('Microchanfro_real','BEVEL'); m.width=bevel; m.segments=4
        m=o.modifiers.new('Normais_ponderadas','WEIGHTED_NORMAL'); m.keep_sharp=True
    if moving: leaf.append(o)
    return o


def box(name, loc, size, mat=wood, bevel=.001, moving=False, horizontal=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    for vert in o.data.vertices:
        vert.co.x*=size[0]; vert.co.y*=size[1]; vert.co.z*=size[2]
    o.data.update()
    return finish(o,name,mat,bevel,moving,horizontal)


def cylinder(name, loc, radius, depth, mat=metal, axis='Z', moving=False):
    rotation={'Z':(0,0,0),'Y':(math.pi/2,0,0),'X':(0,math.pi/2,0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=bpy.context.object
    for poly in o.data.polygons: poly.use_smooth=len(poly.vertices)==4
    return finish(o,name,mat,.00035,moving)


def screw_y(name,x,y,z,moving=False):
    cylinder(name,(x,y,z),.0034,.0015,axis='Y',moving=moving)
    side=-1 if y<0 else 1
    for size in [(.0045,.0003,.0008),(.0008,.0003,.0045)]:
        box(name+'_fenda',(x,y+side*.00085,z),size,slot,.0001,moving)

# Folha de 800 x 2100 x 40 mm, elevada 8 mm do piso.
box('Folha_montante_dobradicas',(.055,0,1.058),(.11,.040,2.10),moving=True)
box('Folha_montante_fechadura',(.745,0,1.058),(.11,.040,2.10),moving=True)
for name,z,height in [('inferior',.078,.14),('central',.938,.14),('superior',2.043,.13)]:
    box('Folha_travessa_'+name,(.4,0,z),(.58,.040,height),moving=True,horizontal=True)
for index,(bottom,top) in enumerate([(.148,.868),(1.008,1.978)]):
    box('Almofada_'+str(index),(.4,0,(bottom+top)/2),(.582,.021,top-bottom+.002),moving=True)
    for side in [-1,1]:
        y=side*.014
        for x in [.117,.683]:
            box('Friso_vertical', (x,y,(bottom+top)/2),(.014,.010,top-bottom),moving=True,bevel=.0025)
        for z in [bottom+.007,top-.007]:
            box('Friso_horizontal',(.4,y,z),(.552,.010,.014),moving=True,bevel=.0025,horizontal=True)
# Marco, batentes e vedação; vão com 3 mm de folga lateral.
for x,label in [(-.026,'esquerdo'),(.826,'direito')]:
    box('Marco_'+label,(x,0,1.058),(.046,.145,2.116))
    box('Batente_'+label,(x+(.020 if x<0 else -.020),.034,1.058),(.019,.024,2.116),bevel=.0015)
    box('Vedacao_'+label,(x+(.023 if x<0 else -.023),.021,1.056),(.010,.004,2.10),dark,.001)
box('Marco_superior',(.4,0,2.136),(.898,.145,.046),horizontal=True)
box('Batente_superior',(.4,.034,2.114),(.806,.024,.018),horizontal=True)
box('Vedacao_superior',(.4,.021,2.111),(.800,.004,.004),dark,.001)
# Guarnições dos dois lados, com moldura escalonada.
for side in [-1,1]:
    for x in [-.043,.843]:
        box('Guarnicao_vertical',(x,side*.081,1.072),(.072,.017,2.144),bevel=.002)
        box('Filete_guarnicao',(x,side*.092,1.07),(.043,.006,2.14),bevel=.0015)
    box('Guarnicao_superior',(.4,side*.081,2.18),(.958,.017,.072),bevel=.002,horizontal=True)
    box('Filete_superior',(.4,side*.092,2.18),(.954,.006,.043),bevel=.0015,horizontal=True)
# Três dobradiças com cinco nós, arruelas e parafusos.
for idx,z in enumerate([.25,1.05,1.86]):
    box('Dobradiça_folha',(.015,-.0215,z),(.032,.003,.09),metal,.001,True)
    box('Dobradiça_marco',(-.019,-.023,z),(.032,.003,.09),metal,.001)
    for k in range(5):
        cylinder('No_dobradica',(-.003,-.025,z-.036+k*.018),.006,.0175,moving=k%2==0)
    for dz in [-.047,.047]:
        cylinder('Pino_dobradica',(-.003,-.025,z+dz),.0064,.003)
    for dz in [-.030,0,.030]:
        screw_y('Parafuso_dobradica',.017,-.024,z+dz,True)
        screw_y('Parafuso_marco',-.021,-.026,z+dz)
# Maçanetas, rosetas, cilindros, espelho de testa e contra-testa.
for side in [-1,1]:
    y=side*.024
    cylinder('Roseta_macaneta',(.736,y,1.02),.026,.008,axis='Y',moving=True)
    cylinder('Anel_macaneta',(.736,side*.029,1.02),.0215,.002,axis='Y',moving=True)
    cylinder('Eixo_macaneta',(.736,side*.048,1.02),.009,.038,axis='Y',moving=True)
    box('Alavanca_macaneta',(.683,side*.069,1.02),(.125,.020,.017),metal,.007,True)
    cylinder('Roseta_chave',(.736,y,.932),.024,.008,axis='Y',moving=True)
    cylinder('Cilindro_chave',(.736,side*.029,.936),.009,.003,brass,'Y',True)
    box('Rasgo_chave',(.736,side*.031,.933),(.002,.001,.014),slot,.0003,True)
    for z in [.997,1.043]: screw_y('Parafuso_roseta',.736,side*.029,z,True)
box('Testa_fechadura',(.801,0,.978),(.002,.026,.18),metal,.001,True)
box('Lingueta',(.805,0,1.02),(.010,.014,.014),brass,.002,True)
box('Contratesta',(.802,0,1.02),(.002,.034,.088),metal,.001)
for z in [.905,1.051]:
    cylinder('Parafuso_testa',(.803,0,z),.003,.002,axis='X',moving=True)
box('Vedacao_inferior',(.4,0,.010),(.78,.021,.004),dark,.001,True)
# Exporta só o produto fechado, em metros, com eixos padrão do importador OBJ.
for o in bpy.context.selected_objects: o.select_set(False)
for o in asset.objects: o.select_set(True)
bpy.context.view_layer.objects.active=leaf[0]
objpath=OUT/'porta_realista_080x210.obj'
bpy.ops.wm.obj_export(filepath=str(objpath),export_selected_objects=True,export_materials=True,export_pbr_extensions=True,path_mode='RELATIVE',export_uv=True,export_normals=True)
stats={'objetos':len(asset.objects),'folha_m': [.8,.04,2.1], 'unidade':'metro','obj':objpath.name}
(OUT/'dimensoes.json').write_text(json.dumps(stats,indent=2))
# Cena de apresentação com folha entreaberta para revelar a espessura.
pivot=Vector((-.003,-.025,0))
rotation=Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(-22),4,'Z') @ Matrix.Translation(-pivot)
for o in leaf: o.matrix_world=rotation @ o.matrix_world
floor=box('Chao_estudio',(.4,0,-.026),(200,200,.04),material('Estudio',(.22,.24,.25),0,.7),.001)
asset.objects.unlink(floor); scene.collection.objects.link(floor)
world=bpy.data.worlds.new('Estudio_world'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.62,.72,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35

def point(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Luz_principal',(-2,-3,4),450,3),('Preenchimento',(3,-1,2.8),300,2),('Recorte',(0,2,3.8),500,2)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    o=bpy.data.objects.new(name,data); scene.collection.objects.link(o); o.location=loc; point(o,(.4,0,1))
cam=bpy.data.cameras.new('Camera'); o=bpy.data.objects.new('Camera',cam); scene.collection.objects.link(o)
o.location=(3,-5,2.7); point(o,(.4,0,1.08)); cam.type='ORTHO'; cam.ortho_scale=2.85; scene.camera=o
scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
scene.render.resolution_x=880; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT/'previa.png')
for im in [color,rough]: im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'porta_realista_estudio.blend'))
bpy.ops.render.render(write_still=True)
print('PORTA_CONCLUIDA',stats,flush=True)
