"""Generic camera pass, driven by ic8_jobs/cams.json (any story/part). Never saves.

Follows docs/CAMERA_GUIDE.md recipe: two cameras Cam_A/Cam_B alternate every shot, 2 linear keys per shot,
one axis (toward/away from the fixed target), 12-20 cm. Deletes ALL old cameras first (leftover focal keys
cause bouncing zoom). Sets the switcher, renders stills: "per_sec": 1 = ~1 per second (3-8 per shot, full check), 0 = middle only (quick pass), else middle (+ start/end if
"edges": true), then restores the play range 0..end.

cams.json = {"end": 64.8, "edges": true, "shots": [
   {"t": [0, 7], "pos": [x,y,z], "target": [x,y,z], "focal": 80, "move": 15},   # move>0 push in, <0 pull out
   {"t": [7, 12], ..., "wide": true},   # view/establishing shot: any lens, DOF off
   ...], "only": [3, 5]}   # only = re-shoot stills of these shots (cameras are still built for all)
Rules enforced here (docs/rules.md Look + Camera), so every AI gets the same result:
 - character shots: lens 80 or 100 only (else the job stops with ERROR), DOF on, focus on the target.
 - face light: one weak shadowless spotlight per avatar, straight in front of the face, linked to the head
   (FaceLight_<name>), made before the cameras. See docs/lighting_notes.md.
   Needs a light in the scene to clone; if none, the log says WARNING NO FACE LIGHT.
Stills: ic8_jobs/cam_NN_mid.png (+ _a/_b). Log: ic8_jobs/cams.log.txt
Every still: SetCurrentCamera + settle (Qt events + ForceViewportUpdate x2) BEFORE RenderImage, then the camera
position at that time is compared with the planned one; log line "still S01 ... err=0.4cm" (STILL_MISMATCH if > 3 cm).
scripts/still_check.py then compares neighbouring stills of each shot and fails on jumps / A-B-A flip-flops.
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


MOVE_RATE = 0.015   # user 2026-11-22: camera move is TIME based - 1.5% of the camera->face distance per second,
MOVE_MIN, MOVE_MAX = 0.06, 0.20   # same steady speed in every shot (subtle but visible); total 6-20% of the distance
def move_cm(s, d):   # signed cm: spec "move" sign = direction (+ push in, - pull out); "move_fixed": true keeps old cm
    m = s.get("move", 15)
    if s.get("move_fixed"): return m
    pct = min(MOVE_MAX, max(MOVE_MIN, s.get("move_rate", MOVE_RATE) * (s["t"][1] - s["t"][0])))
    return (1 if m >= 0 else -1) * d * pct


def key(cam, s, pos, tgt, focal):
    c = cam.GetControl("Transform"); tr = RLPy.RTransform(); c.GetValue(T(s), tr)
    tr.T().x, tr.T().y, tr.T().z = pos
    tr.R().x, tr.R().y, tr.R().z, tr.R().w = look(pos, tgt)
    c.SetValue(T(s), tr)
    c.SetKeyTransition(T(s), RLPy.ETransitionType_Linear, 0.0)  # verified constant-speed camera travel
    cam.SetFocalLength(T(s), focal)


def settle(s):
    """Move to time s and wait until iClone has really evaluated it (Qt events + viewport refresh, twice)."""
    RLPy.RGlobal.SetTime(T(s))
    for _ in range(2):
        QtWidgets.QApplication.processEvents()
        RLPy.RGlobal.ForceViewportUpdate()
        QtWidgets.QApplication.processEvents()
        time.sleep(0.15)


def campos(cam, s):
    c = cam.GetControl("Transform"); tr = RLPy.RTransform(); c.GetValue(T(s), tr)
    return (tr.T().x, tr.T().y, tr.T().z)


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
    preferred = p.get("face_light_source")
    src = next((l for l in lights if l.GetName() == preferred and hasattr(l, "SetRange")), None) or next(
        (l for l in lights if not l.GetName().startswith("FaceLight_") and hasattr(l, "SetSpotLightBeam")), None) or next(
        (l for l in lights if l.GetName() == "Spot Light" and hasattr(l, "SetRange")), None) or next(
        (l for l in lights if l.GetName() == "Point light" and hasattr(l, "SetRange")), None) or next(
        (l for l in lights if not l.GetName().startswith("FaceLight_") and hasattr(l, "SetRange")), None)
    for l in lights:
        if l.GetName().startswith("FaceLight_"): RLPy.RScene.RemoveObject(l)
    lights = [l for l in lights if not l.GetName().startswith("FaceLight_")]
    if not src:
        # Scene lit only by a sun (Directional). Never load an .iLight template: it REPLACES every scene light.
        # ADD one front fill instead: a clone of the sun, aimed like the average shot camera, low, no shadow.
        sun = next((l for l in lights if hasattr(l, "Clone") and not l.GetName().startswith("FaceLight_")), None)
        if sun:
            sh = globals()["p"]["shots"]
            cx = sum(s["pos"][0] for s in sh) / len(sh); cy = sum(s["pos"][1] for s in sh) / len(sh)
            tx = sum(s["target"][0] for s in sh) / len(sh); ty = sum(s["target"][1] for s in sh) / len(sh)
            fl = sun.Clone(); fl.SetName("FaceLight_Fill")
            c = fl.GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
            q = look((cx, cy, 300), (tx, ty, 120)); t.R().x, t.R().y, t.R().z, t.R().w = q; c.SetValue(T(0), t)
            fl.SetMultiplier(T(0), globals().get("FACE_LIGHT_MULTIPLIER", 0.4))
            try: fl.SetCastShadow(False)
            except Exception: pass
            LOG.append("added front fill (clone of %s), sun kept" % sun.GetName())
            return
    if not src:
        LOG.append("WARNING NO FACE LIGHT: scene has no range-capable point/spot light; faces may be dark")
        return
    # Per-cast face fill (docs/lighting_notes.md, user 2026-11-21): a weak SHADOWLESS spotlight straight in front of
    # each face, short range + soft wide falloff so it lights the face only, LINKED to the head so it follows moves.
    # RLPy cannot create lights, so clone a scene spotlight (point light as last resort).
    LOG.append("fill source=%s class=%s" % (src.GetName(), type(src).__name__))
    samples = [time for shot in p["shots"] for time in (shot["t"][0], sum(shot["t"]) / 2)]
    for a in RLPy.RScene.GetAvatars():
        visible_at = next((time for time in samples if a.IsVisible(T(time))), None)
        if visible_at is None: continue   # cast often hidden at 0 (wide opening shot)
        anchor = T(visible_at)
        RLPy.RGlobal.SetTime(anchor)   # measure and link while the avatar is actually visible
        tr = a.WorldTransform(); q = tr.R()
        yaw = 2 * math.atan2(q.z, q.w)
        fx, fy = math.sin(yaw), -math.cos(yaw)          # facing (rules: yaw = atan2(dx,-dy))
        mx, cc, mn = RLPy.RVector3(), RLPy.RVector3(), RLPy.RVector3(); a.GetBounds(mx, cc, mn)
        face = (cc.x, cc.y, mx.z - 15)                  # same face point as the camera auto-aim
        pos = (face[0] + fx * 110, face[1] + fy * 110, face[2] + 20)   # straight-on, slightly above eye line
        lt = src.Clone(); lt.SetName("FaceLight_" + a.GetName())
        if hasattr(RLPy.RScene, "Show"): RLPy.RScene.Show(lt)   # presets sometimes keep the source hidden
        if hasattr(lt, "SetActive"):
            lt.SetActive(T(0), True)  # A visible clone can still inherit a switched-off light source.
            lt.SetActive(anchor, True)
        c = lt.GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
        t.T().x, t.T().y, t.T().z = pos
        t.R().x, t.R().y, t.R().z, t.R().w = look(pos, face)   # clones keep the source's direction otherwise
        c.SetValue(anchor, t)
        lt.SetColor(T(0), RLPy.RRgb(1.0, 0.88, 0.76))  # RRgb takes normalized channel values.
        multiplier = p.get("face_light_overrides", {}).get(a.GetName(), FACE_LIGHT_MULTIPLIER)
        lt.SetMultiplier(T(0), multiplier)
        lt.SetRange(T(0), 220)                         # reaches the face (~110 cm), dies before the set behind
        lt.SetCastShadow(False)
        for fn, args in (("SetSpotLightBeam", (T(0), 45.0, 90.0, 1.0)),   # angle, soft falloff, gentle attenuation
                         ("SetTubeShape", (False,)), ("SetRectangleShape", (False,))):
            if not hasattr(lt, fn): continue
            try: getattr(lt, fn)(*args)
            except Exception as e: LOG.append("  %s skipped: %s" % (fn, e))
        if hasattr(lt, 'SetVisible'): lt.SetVisible(T(0), True)
        # follow the face: link to the head bone, else to the avatar
        bone = next((b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith("Head")), None)
        link = "none"
        for par in ([bone] if bone else []) + [a]:
            try:
                status = lt.LinkTo(par, RLPy.ELinkObjectAlignType__None, anchor)
                if lt.GetLinkedObject(anchor) is not None:
                    link = "%s (%s)" % (par.GetName(), status)
                    break
            except Exception as e:
                LOG.append("  LinkTo %s failed: %s" % (par.GetName(), e))
        LOG.append("face light %s at %s linked=%s" % (a.GetName(), tuple(round(v) for v in pos), link))
    RLPy.RGlobal.SetTime(T(0))


def LIVE(pct, text):   # live progress for the Preview program (progress_app.py reads ic8_jobs/live.json)
    try: open(os.path.join(J, "live.json"), "w", encoding="utf-8").write(json.dumps({"step": "cams", "pct": round(pct), "text": text, "time": time.time()}, ensure_ascii=False))
    except Exception: pass


try:
    p = json.load(open(os.path.join(J, "cams.json"), encoding="utf-8"))
    END = p["end"]
    # 2026-11-21: a new scene file can be SHORTER than the part (บ้านนายชัยยศ = ~30 s). SetTime past the project end
    # clamps, so auto-aim and every still after it rendered the last frame. Make the project long enough FIRST.
    if RLPy.RGlobal.GetProjectLength().ToFloat() / 6000.0 < END + float(p.get("tail", 5.0)):
        RLPy.RGlobal.SetProjectLength(T(END + float(p.get("tail", 5.0))))
        RLPy.RGlobal.SetEndTime(T(END + float(p.get("tail", 5.0))))
    FACE_LIGHT_MULTIPLIER = p.get("face_light_multiplier", 0.04)
    bad = [i + 1 for i, s in enumerate(p["shots"]) if not s.get("wide") and s["focal"] not in (80, 100)]
    if bad: raise ValueError("shots %s: character shots must use 80 or 100 mm (or mark \"wide\": true)" % bad)
    LIVE(2, "ไฟหน้าตัวละคร")
    face_lights()
    LIVE(8, "สร้างกล้อง Cam_A / Cam_B")
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
    # "subject": like select + Home in iClone: read that avatar's real bounds at the shot middle, aim at the face
    # (top - face_drop cm) and shift the camera by the same offset, keeping the planned angle and distance.
    avs = {x.GetName(): x for x in RLPy.RScene.GetAvatars()}
    for i, s in enumerate(p["shots"]):
        sub = avs.get(s.get("subject") or "")
        if not sub: continue
        LIVE(12 + 8.0 * i / len(p["shots"]), "เล็งหน้า ช็อต %d: %s" % (i + 1, s["subject"]))
        RLPy.RGlobal.SetTime(T(sum(s["t"]) / 2)); QtWidgets.QApplication.processEvents()
        mx, c, mn = RLPy.RVector3(), RLPy.RVector3(), RLPy.RVector3(); sub.GetBounds(mx, c, mn)
        new = [c.x, c.y, mx.z - s.get("face_drop", 15)]
        dv = [new[k] - s["target"][k] for k in range(3)]
        s["pos"] = [s["pos"][k] + dv[k] for k in range(3)]; s["target"] = new
        LOG.append("shot %d subject %s -> target %s" % (i + 1, s["subject"], [round(v) for v in new]))
    for i, s in enumerate(p["shots"]):
        cam = cams[i % 2]; a, b = s["t"]
        # 2026-11-22 camera bounce fix (read back from part 4 video): the end key used to sit 1 frame BEFORE the cut,
        # so the last frame(s) of every shot already showed the camera leaving for its next shot = a jerk before the cut.
        # End key now sits ON the first frame at/after the cut: every frame of the shot stays on its own straight move.
        stop = math.ceil(b * 60 - 1e-6) / 60.0
        LIVE(20 + 10.0 * i / len(p["shots"]), "คีย์กล้อง ช็อต %d/%d" % (i + 1, len(p["shots"])))
        c0 = s["pos"]; tg = s["target"]; d = math.dist(c0, tg); m = move_cm(s, d)
        c1 = [c0[k] + (tg[k] - c0[k]) * m / d for k in range(3)]
        key(cam, a, c0, tg, s["focal"]); key(cam, stop, c1, tg, s["focal"])
        dof(cam, a, c0, tg, not (s.get("wide") or s.get("no_dof"))); dof(cam, stop, c1, tg, not (s.get("wide") or s.get("no_dof")))
        RLPy.RScene.AddSwitchCameraKey(T(a), cam)
        LOG.append("shot %d %s %.1f-%.1f focal %d move %+d" % (i + 1, cam.GetName(), a, b, s["focal"], m))
    import glob as _g
    only = set(p.get("only") or [])   # 1-based shot numbers to re-shoot; empty = all shots
    for f in _g.glob(os.path.join(J, "cam_*.png")):   # no stale stills from an older pass (of the shots re-shot)
        if not only or int(os.path.basename(f)[4:6]) in only: os.remove(f)
    todo = [i for i in range(len(p["shots"])) if not only or i + 1 in only]
    for i, s in enumerate(p["shots"]):
        if only and i + 1 not in only: continue
        LIVE(30 + 70.0 * todo.index(i) / max(1, len(todo)), "ภาพนิ่ง ช็อต %d (%d/%d)" % (i + 1, todo.index(i) + 1, len(todo)))
        cam = cams[i % 2]; a, b = s["t"]
        if p.get("per_sec"):   # standard: ~1 still per second, 3..8 per shot, evenly from start to end
            n = max(3, min(8, int(round((b - a) * p["per_sec"])) + 1))
            times = [("%02d_%05.1fs" % (k + 1, t), t) for k, t in
                     enumerate(a + 0.2 + (b - a - 0.4) * k / (n - 1) for k in range(n))]
        else:
            times = [("mid", (a + b) / 2)] + ([("a", a + 0.2), ("b", b - 0.2)] if p.get("edges") else [])
        stop = b - fr if i < len(p["shots"]) - 1 else b
        c0 = s["pos"]; tg = s["target"]; d = math.dist(c0, tg); m = move_cm(s, d)
        c1 = [c0[k] + (tg[k] - c0[k]) * m / d for k in range(3)]
        for tag, t in times:
            # Settle BEFORE every still (user 2026-11-20: stills flip-flopped between frames because RenderImage
            # ran before iClone finished evaluating the new time -> stale camera/pose in the picture).
            f = min(1.0, max(0.0, (t - a) / (stop - a))) if stop > a else 0.0
            want = [c0[k] + (c1[k] - c0[k]) * f for k in range(3)]
            for attempt in range(3):
                RLPy.RScene.SetCurrentCamera(cam)
                settle(t)
                got = campos(cam, t)
                err = math.dist(got, want)
                if err <= 3.0: break
            if err > 3.0:
                LOG.append("STILL_MISMATCH S%02d %s err=%.2fcm (limit 3.0cm)" % (i + 1, tag, err))
                raise RuntimeError("STILL_MISMATCH S%02d %s: camera did not reach planned position" % (i + 1, tag))
            actual = RLPy.RScene.GetCurrentCamera()
            if actual is None or actual.GetID() != cam.GetID():
                LOG.append("STILL_MISMATCH S%02d %s: viewport selected wrong camera" % (i + 1, tag))
                raise RuntimeError("STILL_MISMATCH: wrong current camera")
            path = os.path.join(J, "cam_%02d_%s.png" % (i + 1, tag))
            RLPy.RGlobal.RenderImage(path)
            if not os.path.isfile(path) or os.path.getsize(path) < 10000:
                raise RuntimeError("STILL_CAPTURE_MISSING S%02d %s: image not written" % (i + 1, tag))
            settle(t)   # let the render finish before the next SetTime
            LOG.append("still S%02d %s cam=%s t=%.2f pos=(%.0f,%.0f,%.0f) want=(%.0f,%.0f,%.0f) err=%.1fcm" % (
                i + 1, tag, cam.GetName(), t, got[0], got[1], got[2], want[0], want[1], want[2], err))
    TAIL_END = END + float(p.get("tail", 5.0))
    RLPy.RGlobal.SetProjectLength(T(TAIL_END))
    RLPy.RGlobal.SetStartTime(T(0)); RLPy.RGlobal.SetEndTime(T(TAIL_END))
    RLPy.RGlobal.SetPreviewStartTime(T(0)); RLPy.RGlobal.SetPreviewEndTime(T(TAIL_END))
    RLPy.RGlobal.SetTime(T(0))
    LIVE(100, "เสร็จ")
    LOG.append("DONE (viewport is NOT Switch yet: set the toolbar dropdown to Switch)")
except Exception:
    LOG.append("ERROR\n" + traceback.format_exc())
open(os.path.join(J, "cams.log.txt"), "w", encoding="utf-8").write("\n".join(LOG))
