"""glb -> fbx for iClone props (Tidmunz prop_3d output). Scales the longest side to <size_cm>, puts the
bottom at z=0 and the centre at x=y=0, writes textures as PNG next to the fbx (packed ones come in white).

  blender -b --python scripts/glb2fbx.py -- <in.glb> <out.fbx> <size_cm>
"""
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
src, out, size = a[0], a[1], float(a[2]) / 100.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in obs: o.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
if len(obs) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
from mathutils import Vector
vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
mn = Vector([min(v[i] for v in vs) for i in range(3)]); mx = Vector([max(v[i] for v in vs) for i in range(3)])
s = size / max(mx - mn)
ob.scale = (s, s, s); bpy.ops.object.transform_apply(scale=True)
vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
mn = Vector([min(v[i] for v in vs) for i in range(3)]); mx = Vector([max(v[i] for v in vs) for i in range(3)])
ob.location = (-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z); bpy.ops.object.transform_apply(location=True)
d = os.path.dirname(os.path.abspath(out)); os.makedirs(d, exist_ok=True)
for im in bpy.data.images:
    if im.size[0] == 0: continue
    p = os.path.join(d, bpy.path.clean_name(im.name) + ".png")
    im.filepath_raw = p; im.file_format = "PNG"; im.save(); im.packed_files and im.unpack(method="REMOVE")
    im.filepath = p
bpy.ops.export_scene.fbx(filepath=out, use_selection=False, global_scale=1.0, apply_unit_scale=True,
                         path_mode="RELATIVE", embed_textures=False, object_types={"MESH"})
print("OK fbx", out, "size cm", round(max(mx - mn) * 100, 1))
