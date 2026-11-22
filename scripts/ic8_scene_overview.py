"""Generic optional scene overview survey, not a production camera pass.
Reads ic8_jobs/scene_overview.json with view proposals measured from a scene scan;
captures real iClone images. Restores existing camera transform/focal/time/viewport.
Never Save Project, place cast, render video, or approve survey views automatically.
"""
import os, json, math, traceback
import RLPy
from PySide2 import QtWidgets
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
CONF = os.path.join(J, "scene_overview.json")
OUT = os.path.join(J, "scene_overview")
T = RLPy.RTime.FromValue(0)

def qmul(a, b):
    ax,ay,az,aw=a;bx,by,bz,bw=b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx,
            aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)

def look(pos, target):
    dx,dy,dz=[target[i]-pos[i] for i in range(3)]
    yaw=math.atan2(-dx,dy)
    pitch=math.atan2(dz,math.hypot(dx,dy))
    return qmul((0,0,math.sin(yaw/2),math.cos(yaw/2)),
                qmul((math.sin(pitch/2),0,0,math.cos(pitch/2)),
                     (math.sin(math.pi/4),0,0,math.cos(math.pi/4))))

rows=[]; errors=[]; cam=None; ctrl=None; old=None; oldf=None; original=None
try:
    cfg=json.load(open(CONF,encoding="utf-8"))
    assert cfg.get("survey_only") is True
    assert 1 <= len(cfg["views"]) <= 8
    RLPy.RGlobal.Stop()
    RLPy.RGlobal.SetTime(T)
    original=RLPy.RScene.GetCurrentCamera()
    cams=RLPy.RScene.GetCameras()
    cam=next((c for c in cams if c.GetName()==cfg.get("camera","Cam_A")),None)
    if cam is None:  # scene without cameras: use an existing one, else load a template camera
        cam=next(iter(cams),None)
    if cam is None:
        RLPy.RFileIO.LoadFile(r"C:\Users\Public\Documents\Reallusion\Reallusion Templates\Stage\Camera\IC Camera\Long Shot\Long Shot01.iCam")
        QtWidgets.QApplication.processEvents()
        cam=next(iter(RLPy.RScene.GetCameras()),None)
    assert cam is not None, "survey camera missing"
    ctrl=cam.GetControl("Transform")
    assert ctrl is not None
    old=RLPy.RTransform()
    ctrl.GetValue(T,old)
    old=RLPy.RTransform(old)
    oldf=cam.GetFocalLength(T)
    before_keycount=ctrl.GetKeyCount()
    os.makedirs(OUT,exist_ok=True)
    RLPy.RScene.SetCurrentCamera(cam)
    for idx,v in enumerate(cfg["views"],1):
        p,t=v["pos"],v["target"]
        assert len(p)==3 and len(t)==3 and p!=t
        tr=RLPy.RTransform(old)
        tr.T().x,tr.T().y,tr.T().z=map(float,p)
        q=look(p,t)
        tr.R().x,tr.R().y,tr.R().z,tr.R().w=q
        ctrl.SetValue(T,tr)
        cam.SetFocalLength(T,float(v.get("focal",24.)))
        RLPy.RGlobal.SetTime(T)
        QtWidgets.QApplication.processEvents()
        RLPy.RGlobal.ForceViewportUpdate()
        path=os.path.join(OUT,"overview_%02d.png"%idx)
        render_result=RLPy.RGlobal.RenderImage(path)
        rows.append({"idx":idx,"label":v.get("label","view %d"%idx),"path":path,"exists":os.path.exists(path),
                     "pos":p,"target":t,"focal":v.get("focal",24.),"render":str(render_result)})
except Exception:
    errors.append(traceback.format_exc())
finally:
    try:
        if ctrl is not None and old is not None:
            ctrl.SetValue(T,old)
        if cam is not None and oldf is not None:
            cam.SetFocalLength(T,oldf)
        if original is not None:
            RLPy.RScene.SetCurrentCamera(original)
        RLPy.RGlobal.SetTime(T)
        QtWidgets.QApplication.processEvents()
        if cam and ctrl:
            rows.append({"restored_cam":cam.GetName(),"key_count_before":before_keycount,"key_count_after":ctrl.GetKeyCount()})
    except Exception:
        errors.append("RESTORE: "+traceback.format_exc())
    with open(os.path.join(OUT,"survey_result.json"),"w",encoding="utf-8") as f:
        json.dump({"views":rows,"errors":errors},f,ensure_ascii=False,indent=2)