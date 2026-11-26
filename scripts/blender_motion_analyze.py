"""Read evaluated armature motion in Blender. No scene edits or retargeting."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:]
cfg=json.loads(Path(args[0]).read_text(encoding="utf-8"));out=Path(args[1])
scene=bpy.context.scene;rig=bpy.data.objects.get(cfg["rig"])
if rig is None or rig.type!="ARMATURE":raise ValueError("explicit armature required")
mp=cfg["bones"];required=("root","hips","spine","neck","head","left_hand","right_hand","left_foot","right_foot")
if any(k not in mp or mp[k] not in rig.pose.bones for k in required):raise ValueError("unmapped required bone")
start,end=map(int,cfg["frames"]);fps=scene.render.fps/scene.render.fps_base
if end<=start or fps<=0:raise ValueError("invalid frame range/fps")
limits=cfg.get("limits",{});unit=scene.unit_settings.scale_length
samples=[];previous={};velprev={};posprev={};metrics={}
def update(k,v,f):
    a=metrics.setdefault(k,{"max":-1,"frame":None})
    if v>a["max"]:a.update(max=v,frame=f)
def relative(pb):
    pose=pb.parent.matrix.inverted_safe()@pb.matrix if pb.parent else pb.matrix
    rest=pb.parent.bone.matrix_local.inverted_safe()@pb.bone.matrix_local if pb.parent else pb.bone.matrix_local
    return (rest.to_quaternion().inverted()@pose.to_quaternion()).normalized()
def ang(a,b):return math.degrees(2*math.acos(min(1,max(0,abs(a.dot(b))))))
root0=None
for frame in range(start,end+1):
    scene.frame_set(frame);ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());row={"frame":frame,"seconds":(frame-start)/fps,"bones":{}}
    for label,name in mp.items():
        pb=ev.pose.bones.get(name)
        if pb is None:raise ValueError("bone missing "+name)
        q=relative(pb);p=ev.matrix_world@pb.head;p=p*unit
        angle=ang(q,q.__class__((1,0,0,0)));update(label+".rest_angle_deg",angle,frame)
        if label in previous:
            w=ang(q,previous[label])*fps;update(label+".angular_speed_deg_s",w,frame)
            if label in velprev:update(label+".angular_speed_change_deg_s2",abs(w-velprev[label])*fps,frame)
            velprev[label]=w;update(label+".speed_m_s",(p-posprev[label]).length*fps,frame)
        previous[label]=q.copy();posprev[label]=p.copy()
        row["bones"][label]={"position_m":list(p),"rest_relative_quaternion":list(q),"rest_angle_deg":angle}
    rp=Vector(row["bones"]["root"]["position_m"]);root0=rp.copy() if root0 is None else root0
    update("root.horizontal_drift_m",math.hypot(rp.x-root0.x,rp.y-root0.y),frame)
    for c in cfg.get("contacts",[]):
        if not c["frames"][0]<=frame<=c["frames"][1]:continue
        target=bpy.data.objects.get(c["target"])
        if target is None or c["bone"] not in row["bones"]:raise ValueError("contact target/bone missing")
        dest=target.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation*unit
        distance=(Vector(row["bones"][c["bone"]]["position_m"])-dest).length
        update("contact."+c["bone"]+"."+c["target"]+".distance_m",distance,frame)
    samples.append(row)
flags=[{"metric":k,"max":metrics[k]["max"],"frame":metrics[k]["frame"],"limit":v} for k,v in limits.items() if k in metrics and metrics[k]["max"]>v]
missing=[k for k in limits if k not in metrics]
if missing:raise ValueError("unmeasured limit: "+str(missing))
report={"schema":1,"rig":rig.name,"frames":[start,end],"fps":fps,"metrics":metrics,"flags":flags,"pass_thresholds":not flags,"visual_review_required":True,"notes":"Rest-relative rotation magnitude, not anatomical flexion; flags need action-specific review. Contacts are configured point distances, not mesh collision detection.","samples":samples}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False),encoding="utf-8")
print("MOTION_QA",len(samples),"frames",len(flags),"flags")
