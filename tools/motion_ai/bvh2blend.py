import bpy, sys
src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_anim.bvh(filepath=src, global_scale=0.01, use_fps_scale=False, update_scene_fps=True, update_scene_duration=True,
                        rotate_mode="QUATERNION")
a = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
ren = {"Spine": "Spine1", "Neck": "Neck1", "LeftUpLeg": "LeftLeg_", "RightUpLeg": "RightLeg_"}   # names retarget.py knows
for b in a.data.bones:
    if b.name in ren: b.name = ren[b.name]
for s in ("Left", "Right"):
    a.data.bones[s + "Leg"].name = s + "Shin"; a.data.bones[s + "Leg_"].name = s + "Leg"
print("BONES", [b.name for b in a.data.bones])
bpy.ops.wm.save_as_mainfile(filepath=dst)
