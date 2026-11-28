"""Runs inside Blender: import one motion FBX (iClone Data Link 'Send Motion' / Export FBX, or a library .fbx),
map the main bones automatically (CC_Base_*, RL_*, mixamorig:*, plain names), then run blender_motion_analyze.py.
args after --: <motion.fbx> <out.json> [limits.json]"""
import bpy,sys,json,runpy
from pathlib import Path
fbx,out=sys.argv[sys.argv.index("--")+1:][:2]
extra=sys.argv[sys.argv.index("--")+3:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)
rigs=[o for o in bpy.data.objects if o.type=="ARMATURE" and o.animation_data and o.animation_data.action]
if not rigs:raise SystemExit("no animated armature in "+fbx)
rig=max(rigs,key=lambda o:len(o.data.bones))
names={b.name.lower():b.name for b in rig.data.bones}
WANT={"root":["cc_base_boneroot","rl_boneroot","root"],"hips":["cc_base_hip","hips","hip","pelvis"],
      "spine":["cc_base_spine01","spine1","spine01","spine"],"neck":["cc_base_necktwist01","neck","neck_01"],"head":["cc_base_head","head"],
      "left_hand":["cc_base_l_hand","lefthand","hand_l","l_hand"],"right_hand":["cc_base_r_hand","righthand","hand_r","r_hand"],
      "left_foot":["cc_base_l_foot","leftfoot","foot_l","l_foot"],"right_foot":["cc_base_r_foot","rightfoot","foot_r","r_foot"]}
def find(keys):
    for k in keys:
        for low,real in names.items():
            if low==k or low.split(":")[-1]==k:return real
bones={k:find(v) for k,v in WANT.items()}
if not bones["root"]:bones["root"]=bones["hips"]          # many FBX motions have no separate root bone
miss=[k for k,v in bones.items() if not v]
if miss:raise SystemExit("cannot map bones %s; rig bones: %s"%(miss,list(names.values())[:30]))
a=rig.animation_data.action;f0,f1=int(round(a.frame_range[0])),int(round(a.frame_range[1]))
sc=bpy.context.scene;sc.frame_start,sc.frame_end=f0,f1
limits=json.loads(Path(extra[0]).read_text(encoding="utf-8")) if extra else {}
cfg={"rig":rig.name,"frames":[f0,f1],"bones":bones,"limits":limits}
cp=Path(out).with_suffix(".cfg.json");cp.parent.mkdir(parents=True,exist_ok=True)
cp.write_text(json.dumps(cfg,ensure_ascii=False),encoding="utf-8")
sys.argv=[sys.argv[0],"--",str(cp),out]
runpy.run_path(str(Path(__file__).with_name("blender_motion_analyze.py")),run_name="__main__")
