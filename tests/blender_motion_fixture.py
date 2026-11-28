"""Synthetic motion fixtures for the Blender analyzer; not iClone transfer evidence."""
import bpy,sys,json,math
from pathlib import Path
p=Path(sys.argv[sys.argv.index("--")+1]);p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
a=bpy.data.armatures.new("Skeleton");o=bpy.data.objects.new("Rig",a);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
names=["root","hips","spine","neck","head","left_hand","right_hand","left_foot","right_foot"]
for i,n in enumerate(names):
 b=a.edit_bones.new(n);b.head=(0,0,i*.2);b.tail=(0,0,i*.2+.18)
 if i:b.parent=a.edit_bones[names[i-1] if i<5 else "spine"]
bpy.ops.object.mode_set(mode="POSE")
n=o.pose.bones["neck"];n.rotation_mode="XYZ"
for fr,deg in [(1,0),(5,0),(6,75),(10,0)]:
 n.rotation_euler.x=math.radians(deg);n.keyframe_insert("rotation_euler",frame=fr)
bpy.ops.object.mode_set(mode="OBJECT")
sc=bpy.context.scene;sc.render.fps=30;sc.frame_start=1;sc.frame_end=10
bpy.ops.wm.save_as_mainfile(filepath=str(p/"motion.blend"))
(p/"config.json").write_text(json.dumps({"rig":"Rig","frames":[1,10],"bones":{n:n for n in names},"limits":{"neck.rest_angle_deg":45,"neck.angular_speed_deg_s":400,"root.horizontal_drift_m":.02}}),encoding="utf-8")
