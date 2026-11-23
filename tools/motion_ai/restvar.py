import bpy, sys
v = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(os.path.expanduser("~"), "Documents", "Reallusion", "DataLink", "CC4 - CC3_Base_Plus_2", "exports", "CC3_Base_Plus", "CC3_Base_Plus.fbx"))
T=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
T.animation_data_create(); T.animation_data.action=bpy.data.actions.new("rest")
for f in (0,90):
    for pb in T.pose.bones:
        pb.matrix_basis.identity(); pb.keyframe_insert("location",frame=f); pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode=="QUATERNION" else "rotation_euler",frame=f)
sc=bpy.context.scene; sc.frame_start,sc.frame_end=0,90
bpy.ops.object.select_all(action="DESELECT"); T.select_set(True)
if v != "v1":
    for o in sc.objects:
        if o.type=="MESH" and o.parent==T: o.select_set(True)
kw = dict(use_selection=True, bake_anim=True, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, add_leaf_bones=False)
if v == "v2": kw.update(primary_bone_axis="X", secondary_bone_axis="-Y")
if v == "v3": kw.update(apply_scale_options="FBX_SCALE_ALL")
bpy.ops.export_scene.fbx(filepath=r"C:\MotionAI\out\rest_%s.fbx" % v, **kw)
print("OK", v)
