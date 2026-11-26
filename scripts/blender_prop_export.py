"""Executed in Blender with the authored asset file loaded."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
a=sys.argv[sys.argv.index("--")+1:];folder=Path(a[0]);sys.path.insert(0,a[1])
import qa_check
objects=[o for o in bpy.context.scene.objects if o.type=="MESH"]
if not objects:raise RuntimeError("no mesh")
# Only authored visible meshes, no preview light/camera or unrelated scene.
bpy.ops.object.select_all(action="DESELECT")
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
q=qa_check.run(objects=[o.name for o in objects],profile="render")
(folder/"asset_qa.json").write_text(json.dumps(q,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
if q.get("pass") is not True:raise RuntimeError("geometry QA failed")
# Use existing file textures; write generated/packed images as portable PNG next to FBX.
for im in bpy.data.images:
    if im.size[0]==0 or im.type=="RENDER_RESULT":continue
    if im.packed_file or im.source=="GENERATED":
        im.filepath_raw=str(folder/(bpy.path.clean_name(im.name)+".png"));im.file_format="PNG";im.save()
bpy.ops.object.select_all(action="DESELECT")
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(folder/"model.fbx"),use_selection=True,global_scale=1,apply_unit_scale=True,axis_forward="-Z",axis_up="Y",object_types={"MESH"},bake_anim=False,path_mode="COPY",embed_textures=False)
print("EXPORTED",len(objects),"objects")
