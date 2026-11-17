"""Generic camera pass, driven by ic8_jobs/cams.json (any story/part). Never saves.

Follows docs/CAMERA_GUIDE.md recipe: two cameras Cam_A/Cam_B alternate every shot, 2 linear keys per shot,
one axis (toward/away from the fixed target), 12-20 cm. Deletes ALL old cameras first (leftover focal keys
cause bouncing zoom). Sets the switcher, renders ONE still at every shot's middle (+ start/end if
"edges": true), then restores the play range 0..end.

cams.json = {"end": 64.8, "edges": true, "shots": [
   {"t": [0, 7], "pos": [x,y,z], "target": [x,y,z], "focal": 80, "move": 15},   # move>0 push in, <0 pull out
   {"t": [7, 12], ..., "wide": true},   # view/establishing shot: any lens, DOF off
   ...]}
Rules enforced here (docs/rules.md Look + Camera), so every AI gets the same result:
 - character shots: lens 80 or 100 only (else the job stops with ERROR), DOF on, focus on the target.
 - face light: one soft light per avatar, front-left above the face (FaceLight_<name>), made before the cameras.
   Needs a light in the scene to clone; if none, the log says WARNING NO FACE LIGHT.
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


def dof(cam, s, pos, tgt, on):
    d = RLPy.RCameraDofData(); d.SetEnable(on)
    if on:
        d.SetFocus(math.dist(pos, tgt)); d.SetRange(55); d.SetFarTransitionRegion(100); d.SetNearTransitionRegion(70)
        d.SetFarBlurScale(1); d.SetNearBlurScale(1)
    k = RLPy.RKey(); k.SetTime(T(s)); cam.AddDofKey(k, d)


def face_lights():
    lights = list(RLPy.RScene.FindObjects(RLPy.EObjectType_Light))
    # Directional lights (RIDirectionalLight) do not implement SetRange; only
    # clone a range-capable point/spot light for per-avatar fill lights.
    src = next((l for l in lights if l.GetName() == "Point light" and hasattr(l, "SetRange")), None) or next(
        (l for l in lights if not l.GetName().startswith("FaceLight_") and hasattr(l, "SetRange")), None)
    for l in lights:
        if l.GetName().startswith("FaceLight_"): RLPy.RScene.RemoveObject(l)
    if not src:
        LOG.append("WARNING NO FACE LIGHT: scene has no range-capable point/spot light; faces may be dark")
        return
    for a in RLPy.RScene.GetAvatars():
        if not a.IsVisible(T(0)): continue
        tr = a.WorldTransform(); p = tr.T(); q = tr.R()
        yaw = 2 * math.atan2(q.z, q.w)
        fx, fy = math.sin(yaw), -math.cos(yaw)          # facing (rules: yaw = atan2(dx,-dy))
        lx, ly = -fy, fx                                 # character's left
        pos = (p.x + fx * 120 + lx * 60, p.y + fy * 120 + ly * 60, p.z + 200)
        lt = src.Clone(); lt.SetName("FaceLight_" + a.GetName())
        c = lt.GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
        t.T().x, t.T().y, t.T().z = pos; c.SetValue(T(0), t)
        lt.SetColor(T(0), RLPy.RRgb(255, 236, 214)); lt.SetMultiplier(T(0), 0.04); lt.SetRange(T(0), 700); lt.SetCastShadow(False)
        LOG.append("face light %s at %s" % (a.GetName(), tuple(round(v) for v in pos)))


try:
    p = json.load(open(os.path.join(J, "cams.json"), encoding="utf-8"))
    END = p["end"]
    bad = [i + 1 for i, s in enumerate(p["shots"]) if not s.get("wide") and s["focal"] not in (80, 100)]
    if bad: raise ValueError("shots %s: character shots must use 80 or 100 mm (or mark \"wide\": true)" % bad)
    face_lights()
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
        dof(cam, a, c0, tg, not s.get("wide")); dof(cam, stop, c1, tg, not s.get("wide"))
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
