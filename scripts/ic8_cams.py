"""Generic camera pass, driven by ic8_jobs/cams.json (any story/part). Never saves.

Follows docs/CAMERA_GUIDE.md recipe: two cameras Cam_A/Cam_B alternate every shot, 2 linear keys per shot,
one axis (toward/away from the fixed target), 12-20 cm. Deletes ALL old cameras first (leftover focal keys
cause bouncing zoom). Sets the switcher, renders ONE still at every shot's middle (+ start/end if
"edges": true), then restores the play range 0..end.

cams.json = {"end": 64.8, "edges": true, "shots": [
   {"t": [0, 7], "pos": [x,y,z], "target": [x,y,z], "focal": 95, "move": 15},   # move>0 push in, <0 pull out
   ...]}
Stills: ic8_jobs/cam_NN_mid.png (+ _a/_b). Log: ic8_jobs/cams.log.txt
"""
import RLPy, os, math, json, time, traceback
from PySide2 import QtWidgets
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
ICAM = r"C:\Users\Public\Documents\Reallusion\Reallusion Templates\Stage\Camera\IC Camera\Long Shot\Long Shot01.iCam"
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
LOG = []


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)


def look(c, t):
    dx, dy, dz = (t[i] - c[i] for i in range(3))
    yaw = math.atan2(-dx, dy); pitch = math.atan2(dz, math.hypot(dx, dy)); r = math.sqrt(.5)
    return qmul((0, 0, math.sin(yaw/2), math.cos(yaw/2)), qmul((math.sin(pitch/2), 0, 0, math.cos(pitch/2)), (r, 0, 0, r)))


def key(cam, s, pos, tgt, focal):
    c = cam.GetControl("Transform"); tr = RLPy.RTransform(); c.GetValue(T(s), tr)
    tr.T().x, tr.T().y, tr.T().z = pos
    tr.R().x, tr.R().y, tr.R().z, tr.R().w = look(pos, tgt)
    c.SetValue(T(s), tr)
    cam.SetFocalLength(T(s), focal)


try:
    p = json.load(open(os.path.join(J, "cams.json"), encoding="utf-8"))
    END = p["end"]
    RLPy.RGlobal.Stop(); RLPy.RScene.ClearSelectObjects()
    for _ in range(50):   # some old cameras report no Transform control: delete them all, by name loop
        old = RLPy.RScene.GetCameras()
        if not old:
            break
        RLPy.RScene.RemoveObject(old[0])
    cams = []
    for name in ("Cam_A", "Cam_B"):
        before = {c.GetID() for c in RLPy.RScene.GetCameras()}
        RLPy.RFileIO.LoadFile(ICAM); QtWidgets.QApplication.processEvents(); time.sleep(0.3)
        new = [c for c in RLPy.RScene.GetCameras() if c.GetID() not in before]
        new[0].SetName(name); RLPy.RGlobal.RemoveAllAnimations(new[0]); cams.append(new[0])
    RLPy.RScene.ClearSwitchCameraKeys()
    fr = 1 / 60.0
    for i, s in enumerate(p["shots"]):
        cam = cams[i % 2]; a, b = s["t"]; stop = b - fr if i < len(p["shots"]) - 1 else b
        c0 = s["pos"]; tg = s["target"]; d = math.dist(c0, tg); m = s.get("move", 15)
        c1 = [c0[k] + (tg[k] - c0[k]) * m / d for k in range(3)]
        key(cam, a, c0, tg, s["focal"]); key(cam, stop, c1, tg, s["focal"])
        RLPy.RScene.AddSwitchCameraKey(T(a), cam)
        LOG.append("shot %d %s %.1f-%.1f focal %d move %+d" % (i + 1, cam.GetName(), a, b, s["focal"], m))
    for i, s in enumerate(p["shots"]):
        cam = cams[i % 2]; a, b = s["t"]
        times = [("mid", (a + b) / 2)] + ([("a", a + 0.2), ("b", b - 0.2)] if p.get("edges") else [])
        RLPy.RScene.SetCurrentCamera(cam)
        for tag, t in times:
            RLPy.RGlobal.SetTime(T(t)); RLPy.RGlobal.ForceViewportUpdate()
            RLPy.RGlobal.RenderImage(os.path.join(J, "cam_%02d_%s.png" % (i + 1, tag)))
    RLPy.RGlobal.SetStartTime(T(0)); RLPy.RGlobal.SetEndTime(T(END))
    RLPy.RGlobal.SetPreviewStartTime(T(0)); RLPy.RGlobal.SetPreviewEndTime(T(END))
    RLPy.RGlobal.SetTime(T(0))
    LOG.append("DONE (viewport is NOT Switch yet: set the toolbar dropdown to Switch)")
except Exception:
    LOG.append("ERROR\n" + traceback.format_exc())
open(os.path.join(J, "cams.log.txt"), "w", encoding="utf-8").write("\n".join(LOG))
