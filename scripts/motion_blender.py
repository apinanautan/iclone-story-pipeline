"""Read a motion and print a short Thai verdict; Blender draws ONE picture of the flagged frames.

  python scripts/motion_blender.py actor <iClone actor name> [fps]   # live iClone, no FBX licence needed
  python scripts/motion_blender.py check <motion.fbx> [limits.json]  # any .fbx (library, Blender)

actor: an iClone watcher job reads the main CC_Base bone transforms frame by frame (65 s at 30 fps ~ 35 s),
because this iClone has no FBX Export License (Export FBX / Data Link Send Motion say "purchase Export Licenses").
Junk rule (user 2026-11-28): samples live in one temp folder and are deleted; progress/motion_analysis keeps
the newest KEEP reports only.
"""
import json,math,os,subprocess,sys,tempfile,time
from pathlib import Path
from blender_prop_build import blender
from cinematic_qa import digest,hashobj
ROOT=Path(__file__).resolve().parents[1]
SCR=ROOT/"scripts"
KEEP=30
TMP=Path(tempfile.gettempdir())/"ic_motion_check"
JOBS=Path(os.environ.get("LOCALAPPDATA",""))/"Tidmunz Studio"/"snapgen_data"/"ic8_jobs"
CC={"root":"CC_Base_Hip","hips":"CC_Base_Hip","spine":"CC_Base_Spine01","neck":"CC_Base_NeckTwist01","head":"CC_Base_Head",
    "left_hand":"CC_Base_L_Hand","right_hand":"CC_Base_R_Hand","left_foot":"CC_Base_L_Foot","right_foot":"CC_Base_R_Foot",
    "l_upperarm":"CC_Base_L_Upperarm","r_upperarm":"CC_Base_R_Upperarm","l_forearm":"CC_Base_L_Forearm","r_forearm":"CC_Base_R_Forearm",
    "l_thigh":"CC_Base_L_Thigh","r_thigh":"CC_Base_R_Thigh","l_calf":"CC_Base_L_Calf","r_calf":"CC_Base_R_Calf"}

def prune():
    d=ROOT/"progress"/"motion_analysis"
    for f in sorted(d.glob("*.json"),key=lambda f:f.stat().st_mtime)[:-KEEP]:
        f.unlink(missing_ok=True);f.with_suffix(".png").unlink(missing_ok=True)

JOB="""import RLPy,json
T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))
R={}
try:
    a=[x for x in RLPy.RScene.GetAvatars() if x.GetName()==@ACTOR@]
    assert a,'actor not in scene: '+@ACTOR@
    B={b.GetName():b for b in a[0].GetSkeletonComponent().GetSkinBones() if b.GetName() in @WANT@}
    n=int(RLPy.RGlobal.GetProjectLength().ToFloat()/6000*@FPS@)+1;F=[]
    for i in range(n):
        RLPy.RGlobal.SetTime(T(i/@FPS@.0));row={}
        for k,b in B.items():
            w=b.WorldTransform();p=w.T();q=w.R();row[k]=[p.x,p.y,p.z,q.w,q.x,q.y,q.z]
        F.append(row)
    R.update(fps=@FPS@,frames=F)
except Exception as e:R['err']=repr(e)
json.dump(R,open(@OUT@,'w',encoding='utf-8'),ensure_ascii=False)
"""

def sample(actor,fps=30,wait=300):
    """Watcher job in the open iClone: world position (cm) + rotation of the main bones, every 1/fps s."""
    TMP.mkdir(exist_ok=True);out=TMP/"samples.json";out.unlink(missing_ok=True)
    code=JOB.replace("@ACTOR@",repr(actor)).replace("@WANT@",repr(sorted(set(CC.values())))).replace("@FPS@",str(int(fps))).replace("@OUT@",repr(str(out)))
    run=JOBS/"run";f=run/"zz_motion_sample.py"
    for x in ("done","log","err"):(run/("zz_motion_sample."+x)).unlink(missing_ok=True)
    if f.exists():raise SystemExit("งานอ่านโมชั่นเดิมยังค้างใน iClone")
    tmp=f.with_suffix(".tmp");tmp.write_text(code,encoding="utf-8");tmp.replace(f)
    t0=time.time()
    while f.exists() and time.time()-t0<wait:time.sleep(0.5)
    if f.exists():f.unlink(missing_ok=True);raise SystemExit("iClone ไม่รับงานใน %d วินาที (ไม่ได้เปิด หรือมีหน้าต่างค้าง)"%wait)
    if not out.exists():raise SystemExit("iClone ทำงานแต่ไม่มีผล: ดู "+str(run/"zz_motion_sample.log"))
    S=json.loads(out.read_text(encoding="utf-8"));out.unlink()
    if S.get("err"):raise SystemExit("อ่านโมชั่นไม่ได้: "+S["err"])
    return S

def _ang(a,b):return math.degrees(2*math.acos(min(1.0,abs(sum(x*y for x,y in zip(a,b))))))

def measure(S,source,limits=None):
    """Same metric names and report shape as blender_motion_analyze.py (rotations are world-space here)."""
    lim=limits or LIMITS;fps=S["fps"];F=S["frames"];m={}
    def up(k,v,i):
        a=m.setdefault(k,{"max":-1,"frame":None})
        if v>a["max"]:a.update(max=v,frame=i)
    r0=F[0][CC["root"]]
    for i,row in enumerate(F):
        up("root.horizontal_drift_m",math.hypot(row[CC["root"]][0]-r0[0],row[CC["root"]][1]-r0[1])/100,i)
        if not i:continue
        for lab,b in CC.items():
            a,c=F[i-1].get(b),row.get(b)
            if a and c:up(lab+".angular_speed_deg_s",_ang(a[3:],c[3:])*fps,i);up(lab+".speed_m_s",math.dist(a[:3],c[:3])/100*fps,i)
    flags=[{"metric":k,"max":m[k]["max"],"frame":m[k]["frame"],"limit":v} for k,v in lim.items() if k in m and m[k]["max"]>v]
    return {"schema":1,"source":source,"frames":[0,len(F)-1],"fps":fps,"metrics":m,"flags":flags,"pass_thresholds":not flags,
            "notes":"iClone world-space samples; frame = index at fps"}

def picture(S,frames,png):
    """Blender draws a stick figure for each listed frame side by side: one image instead of many screenshots."""
    TMP.mkdir(exist_ok=True);src=TMP/"pic.json"
    src.write_text(json.dumps({"frames":[S["frames"][i] for i in frames],"labels":["f%d %.1fs"%(i,i/S["fps"]) for i in frames]}),encoding="utf-8")
    r=subprocess.run([blender(),"--background","--factory-startup","--python-exit-code","1","--python",str(SCR/"blender_motion_sheet.py"),"--",str(src),str(png)],
                     capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300)
    src.unlink(missing_ok=True)
    if r.returncode or not Path(png).exists():raise SystemExit("Blender วาดภาพไม่ได้: "+" | ".join((r.stdout+r.stderr).strip().splitlines()[-2:]))

def actor(name,fps=30):
    S=sample(name,int(fps));q=measure(S,name)
    d=ROOT/"progress"/"motion_analysis";d.mkdir(parents=True,exist_ok=True)
    p=d/("actor_%s.json"%hashobj([name,time.time()])[:16]);p.write_text(json.dumps(q,ensure_ascii=False),encoding="utf-8")
    fr=sorted({f["frame"] for f in q["flags"]})[:4] or [0,len(S["frames"])//2,len(S["frames"])-1]
    png=d/(p.stem+".png");picture(S,fr,png);prune()
    return q,p,png
LIMITS={"root.horizontal_drift_m":0.6,"head.angular_speed_deg_s":400,
        "left_hand.angular_speed_deg_s":900,"right_hand.angular_speed_deg_s":900}

def check(fbx,limits=None):
    fbx=Path(fbx).resolve()
    if fbx.suffix.lower()!=".fbx" or not fbx.is_file():raise SystemExit("ต้องเป็นไฟล์ .fbx (ส่งจาก iClone ด้วย Data Link Send Motion ก่อน)")
    lim=json.loads(Path(limits).read_text(encoding="utf-8")) if limits else LIMITS
    key=hashobj([digest(fbx),lim,digest(SCR/"blender_motion_analyze.py"),digest(SCR/"blender_fbx_motion.py")])
    d=ROOT/"progress"/"motion_analysis";d.mkdir(parents=True,exist_ok=True);p=d/(key+".json")
    if not p.exists():
        t=d/(key+".partial.json");lp=d/(key+".limits.json");lp.write_text(json.dumps(lim),encoding="utf-8")
        r=subprocess.run([blender(),"--background","--factory-startup","--threads","2","--python-exit-code","1",
                          "--python",str(SCR/"blender_fbx_motion.py"),"--",str(fbx),str(t),str(lp)],
                         capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300)
        lp.unlink(missing_ok=True)
        if r.returncode or not t.exists():
            tail=[l for l in (r.stdout+r.stderr).splitlines() if l.strip()][-3:]
            raise SystemExit("Blender อ่านไม่ได้: "+" | ".join(tail))
        q=json.loads(t.read_text(encoding="utf-8"));q.update(source=fbx.name,source_sha256=digest(fbx),cache_key=key)
        t.write_text(json.dumps(q,ensure_ascii=False),encoding="utf-8");t.replace(p)
        Path(str(t).replace(".partial.json",".partial.cfg.json")).unlink(missing_ok=True)
        prune()
    return json.loads(p.read_text(encoding="utf-8")),p

def summary(q):
    m=q["metrics"];f0,f1=q["frames"];fps=q["fps"]
    g=lambda k:m.get(k,{}).get("max",0)
    lines=["โมชั่น %s: %d เฟรม (%.1f วินาที, %g fps)"%(q.get("source","?"),f1-f0+1,(f1-f0)/fps,fps),
           "ตัวเลื่อนจากจุดเริ่ม %.2f ม. · หัวหมุนเร็วสุด %.0f°/s · มือซ้าย/ขวา %.0f/%.0f°/s"%(
               g("root.horizontal_drift_m"),g("head.angular_speed_deg_s"),g("left_hand.angular_speed_deg_s"),g("right_hand.angular_speed_deg_s"))]
    for fl in q["flags"]:
        lines.append("⚠ %s = %.2f (เกิน %.2f) ที่เฟรม %s"%(fl["metric"],fl["max"],fl["limit"],fl["frame"]))
    lines.append("ผ่านเกณฑ์ตัวเลข" if q["pass_thresholds"] else "ไม่ผ่าน: ดูเฟรมที่บอก แค่ภาพเดียวพอ")
    return "\n".join(lines)

if __name__=="__main__":
    if len(sys.argv)<3 or sys.argv[1] not in("check","actor"):raise SystemExit(__doc__)
    if sys.argv[1]=="actor":
        q,p,png=actor(*sys.argv[2:4]);print(summary(q));print("report:",p.relative_to(ROOT));print("ภาพเดียว:",png.relative_to(ROOT))
    else:
        q,p=check(*sys.argv[2:4]);print(summary(q));print("report:",p.relative_to(ROOT))
