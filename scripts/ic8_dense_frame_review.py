# -*- coding: utf-8 -*-
"""In-iClone watcher job: frame-by-frame QA (not a movie render). RLPy required.
Job JSON: %LOCALAPPDATA%/Tidmunz Studio/snapgen_data/ic8_jobs/dense_frame_review_job.json
Fields: start_frame, end_frame (half open), fps=30, out_dir, required_camera_prefix, replace_existing=false
"""
import os, json, traceback
from pathlib import Path
import RLPy
J=Path(os.environ["LOCALAPPDATA"])/"Tidmunz Studio"/"snapgen_data"/"ic8_jobs"
job=json.loads((J/"dense_frame_review_job.json").read_text(encoding="utf-8"))
fps=int(job.get("fps",30))
start,end=int(job["start_frame"]),int(job["end_frame"])
if fps!=30 or end<=start or end-start>60: raise ValueError("Only 30fps, 1–60 frame batches permitted")
out=Path(job["out_dir"]);out.mkdir(parents=True,exist_ok=True)
req=job.get("required_camera_prefix")
cams=list(RLPy.RScene.GetCameras())
if not cams:raise RuntimeError("No scene camera")
if req and not any(c.GetName().startswith(req) for c in cams):
    raise RuntimeError("Unexpected iClone scene cameras; do not capture wrong project")
cam_by_name={c.GetName():c for c in cams}
project_fps=RLPy.RGlobal.GetFps()
project_fps_float=project_fps.ToFloat()
switch=sorted([(int(f)/project_fps_float,c.GetName()) for c,f in RLPy.RScene.GetSwitchCameraFrameIndexs(project_fps)])
if not switch: raise RuntimeError("No active Switch Camera keys; cannot verify actual shot sequence")
def current_camera(seconds):
    name=switch[0][1]
    for ts,nm in switch:
        if ts>seconds+1e-8:break
        name=nm
    if name not in cam_by_name:raise RuntimeError("Switcher references missing camera "+name)
    return cam_by_name[name],name

old_time=None
old_camera=None
try: old_time=RLPy.RGlobal.GetTime()
except Exception:pass
try: old_camera=RLPy.RScene.GetCurrentCamera()
except Exception:pass
rows=[]
try:
    for i in range(start,end):
        sec=i/fps
        cam,nm=current_camera(sec)
        path=out/("frame_%05d.png"%i)
        if path.exists() and not job.get("replace_existing",False):
            raise FileExistsError("QA frame already exists; refuse silent reuse: "+str(path))
        RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(int(round(sec*6000))))
        RLPy.RScene.SetCurrentCamera(cam)
        st=RLPy.RGlobal.RenderImage(str(path))
        err=bool(st.IsError()) if hasattr(st,"IsError") else False
        if not path.exists() or path.stat().st_size<1000 or err:
            raise RuntimeError("RenderImage QA failed at frame "+str(i))
        rows.append({"frame":i,"time":round(sec,7),"camera":nm,"image":str(path),"bytes":path.stat().st_size})
finally:
    if old_time is not None:
        try: RLPy.RGlobal.SetTime(old_time)
        except Exception:pass
    if old_camera is not None:
        try: RLPy.RScene.SetCurrentCamera(old_camera)
        except Exception:pass
log={
    "ok":True,"fps":fps,"project_fps":project_fps_float,
    "start_frame":start,"end_frame":end,"captured":len(rows),
    "switch":[{"time":round(t,6),"camera":n} for t,n in switch],
    "rows":rows}
(out/("batch_%05d_%05d.json"%(start,end))).write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding="utf-8")
(J/"dense_frame_review_result.txt").write_text("PASS frames %d..%d (%d frames) %s"%(start,end-1,len(rows),out),encoding="utf-8")
