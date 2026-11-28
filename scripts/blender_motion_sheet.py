"""Runs inside Blender (headless): draw iClone bone samples as stick figures, one per frame, side by side, into ONE png.
args after --: <pic.json {frames:[{bone:[x,y,z(cm),...]}], labels:[...]}> <out.png>"""
import bpy,sys,json,math
from mathutils import Vector
src,png=sys.argv[sys.argv.index("--")+1:][:2]
D=json.load(open(src,encoding="utf-8"))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
CH=[["CC_Base_Hip","CC_Base_Spine01","CC_Base_NeckTwist01","CC_Base_Head"]]
for s in "LR":
    CH+=[["CC_Base_NeckTwist01","CC_Base_%s_Upperarm"%s,"CC_Base_%s_Forearm"%s,"CC_Base_%s_Hand"%s],
         ["CC_Base_Hip","CC_Base_%s_Thigh"%s,"CC_Base_%s_Calf"%s,"CC_Base_%s_Foot"%s]]
GAP=1.3;verts=[];edges=[];heads=[]
for n,row in enumerate(D["frames"]):
    hip=row["CC_Base_Hip"];off=Vector((n*GAP-hip[0]/100,-hip[1]/100,0))
    idx={}
    for b,v in row.items():idx[b]=len(verts);verts.append(Vector((v[0]/100,v[1]/100,v[2]/100))+off)
    for c in CH:
        for a,b in zip(c,c[1:]):
            if a in idx and b in idx:edges.append((idx[a],idx[b]))
    if "CC_Base_Head" in idx:heads.append(verts[idx["CC_Base_Head"]])
    t=bpy.data.curves.new("t%d"%n,"FONT");t.body=D["labels"][n];t.size=0.12
    o=bpy.data.objects.new("t%d"%n,t);o.location=(n*GAP-0.3,-0.5,0);o.rotation_euler=(0,0,0);sc.collection.objects.link(o)
# bevelled curves (a skin modifier only grows the first figure)
cu=bpy.data.curves.new("stick","CURVE");cu.dimensions="3D";cu.bevel_depth=0.025;cu.bevel_resolution=2
for i,j in edges:
    s=cu.splines.new("POLY");s.points.add(1);s.points[0].co=(*verts[i],1);s.points[1].co=(*verts[j],1)
sc.collection.objects.link(bpy.data.objects.new("stick",cu))
for h in heads:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09,location=h+Vector((0,0,0.07)))
lo=Vector((min(v.x for v in verts),min(v.y for v in verts),min(v.z for v in verts)))
hi=Vector((max(v.x for v in verts),max(v.y for v in verts),max(v.z for v in verts)))
fl=bpy.data.objects.new("floor",bpy.data.meshes.new("f"));sc.collection.objects.link(fl)
fl.data.from_pydata([(lo.x-.6,lo.y-.6,lo.z),(hi.x+.6,lo.y-.6,lo.z),(hi.x+.6,hi.y+.6,lo.z),(lo.x-.6,hi.y+.6,lo.z)],[],[(0,1,2,3)])
cam=bpy.data.objects.new("cam",bpy.data.cameras.new("cam"));sc.collection.objects.link(cam);sc.camera=cam
c=(lo+hi)/2
d=Vector((0.35,-1,0.25)).normalized()      # front-left, slightly above: arms and legs both readable
RX=max(480,320*len(D["frames"]));RY=400
cam.data.type="ORTHO";cam.data.ortho_scale=max(hi.x-lo.x+1.0,(hi.z-lo.z+0.6)*RX/RY)
cam.location=c+d*12;cam.rotation_euler=(-d).to_track_quat("-Z","Y").to_euler()
sc.render.engine="BLENDER_WORKBENCH";sc.render.resolution_x=RX;sc.render.resolution_y=RY
sc.display.shading.light="STUDIO";sc.display.shading.color_type="OBJECT"
sc.render.filepath=png;bpy.ops.render.render(write_still=True)
print("SHEET",png)
