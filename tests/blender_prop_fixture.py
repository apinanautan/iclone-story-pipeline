"""Small procedural salon bottle fixture for headless Blender export regression."""
import bpy, math,sys
from pathlib import Path
p=Path(sys.argv[sys.argv.index("--")+1])
bpy.ops.wm.read_factory_settings(use_empty=True)
# Revolved profile, base to top: a single connected watertight mesh.
profile=[(.035,0),(.039,.004),(.039,.105),(.038,.112),(.021,.135),(.017,.140),(.017,.169),(.020,.171),(.020,.190),(.018,.193)]
N=64;v=[(r*math.cos(2*math.pi*i/N),r*math.sin(2*math.pi*i/N),z) for r,z in profile for i in range(N)]
faces=[tuple(reversed(range(N)))]
for j in range(len(profile)-1):
 for i in range(N):
  k=j*N+i;n=j*N+(i+1)%N;faces.append((k,n,n+N,k+N))
faces.append(tuple(range((len(profile)-1)*N,len(profile)*N)))
m=bpy.data.meshes.new("bottle");m.from_pydata(v,[],faces);m.update();o=bpy.data.objects.new("SalonBottle",m);bpy.context.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
for name,color,rough,metal in [("Amber",(.26,.095,.035,1),.32,0),("Dark cap",(.025,.018,.015,1),.24,.1)]:
 mat=bpy.data.materials.new(name);mat.diffuse_color=color;mat.use_nodes=True;n=mat.node_tree.nodes.get("Principled BSDF");n.inputs["Base Color"].default_value=color;n.inputs["Metallic"].default_value=metal;n.inputs["Roughness"].default_value=rough;m.materials.append(mat)
for f in m.polygons:
 f.use_smooth=len(f.vertices)==4
 f.material_index=1 if f.center.z>.169 else 0
bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.select_all(action="SELECT");bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.wm.save_as_mainfile(filepath=str(p/"model.blend"))
