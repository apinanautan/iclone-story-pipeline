"""Generic avatar staging, driven by ic8_jobs/pose_place.json (any story/part). Never saves.

place.json = {"end": 64.8, "avatars": {"<name>": {
    "motion": "<motion root>/.../X.iMotion", "speed": 0.8,      # optional 0.65-1.0; list repeats with crossfades until end
    "pos": [x, y, z], "yaw": deg, "pitch": deg,       # optional root placement (pitch = tilt back, negative = lean back)
    "lookfront": true,                                 # load Look front.iTalk (natural head motion), or a path to another .iTalk (Happy/Sad/Think...)
    "lookat": "<other avatar name>",                   # head/eyes follow that avatar's head
    "face": {"Eye_Blink_L": 0.0, ...},                 # optional expression keys at 0 and end
    "visible": [[t, 0|1], ...]}}}
Log: ic8_jobs/pose_place.log.txt
"""
import RLPy, os, math, json, traceback, time
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
LOOKFRONT = None   # ic8_part.py passes the real path (found by scripts/paths.py); no drive letter here
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
LOG = []


def LIVE(pct, text):   # also: a file ic8_jobs/pose_stop.flag stops the job at the next step
    if os.path.exists(os.path.join(J, "pose_stop.flag")):
        os.remove(os.path.join(J, "pose_stop.flag")); raise RuntimeError("stopped by pose_stop.flag")
    return _LIVE(pct, text)
def _LIVE(pct, text):   # live progress for the Preview program (progress_app.py reads ic8_jobs/live.json)
    try: open(os.path.join(J, "live.json"), "w", encoding="utf-8").write(json.dumps({"step": "pose", "pct": round(pct), "text": text, "time": time.time()}, ensure_ascii=False))
    except Exception: pass
MIN_SPEED = 0.65   # never slower: judder (user 2026-11-19)
XF = 2.0          # (old) transition inside the clip start - NOT used any more
GAP = 1.0         # user 2026-11-22 (picture 2): clips must sit APART with a small empty gap, and the transition
                  # fills that gap (crossed lines between the clips) - never butted together like picture 1
FGAP = 0.6        # same rule for face (.iTalk) clips
XOVER = 1.5       # body; face uses FXOVER. Value copied from the user's own drag (2.48 s on a 1.0 s gap).
FXOVER = 1.0
def XOUT(front, gap, back):   # the FRONT clip fades out too, from `back` s before its end, across the gap into the
    d = front.GetTransitionData()   # next clip (TransitionData = [in range, in offset, out range, out offset]).
    d[2] = T(gap + back + 0.2); d[3] = T(-back); front.SetTransitionData(d)   # user's own drag: [.., 2.70, -1.48]
# user 2026-11-22 (3rd picture): transition = gap + XOVER, so it reaches INTO the next clip and
                  # iClone draws a full X (front->back, back->front), not a single '/' ending at the clip corner
def WINS(s, end):   # user 2026-11-22: clips only where the character is ON SCREEN (+0.5 s), not a long run over
    vis = sorted(s.get("visible") or [])                   # the whole part; windows closer than 3 s are merged
    if not vis: return [(float(s.get("motion_start", 0.0)), end)]
    w = []
    for i, (t0, on) in enumerate(vis):
        t1 = vis[i + 1][0] if i + 1 < len(vis) else end
        if on and t1 - t0 > 0.1:
            a0, a1 = max(0.0, t0 - 0.5), min(end, t1 + 0.5)
            if w and a0 - w[-1][1] < 3.0: w[-1] = (w[-1][0], a1)
            else: w.append((a0, a1))
    return w or [(0.0, end)]


def head(avatar):
    return next(b for b in avatar.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith("Head"))


try:
    p = json.load(open(os.path.join(J, "pose_place.json"), encoding="utf-8"))
    END = p["end"]
    RLPy.RGlobal.Stop()
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    NAV = len(p["avatars"])
    for ai, (name, s) in enumerate(p["avatars"].items()):
        a = av[name]
        LIVE(100.0 * ai / NAV, "%s: เริ่ม" % name)
        sk = a.GetSkeletonComponent()
        motions = s.get("motions") or ([s["motion"]] if s.get("motion") else [])
        if motions:   # clips back to back, each slowed, until the part end
            while sk.GetClipCount():
                sk.DeleteClip(sk.GetClip(0))
            k = 0; ncl = 0
            # speed 0.65-1.0 (user 2026-11-19): slower clips step at ~12 poses/s = visible judder.
            for (w0, w1) in WINS(s, END):
              cur = w0; kw = 0
              while cur < w1 - 0.1 and kw < 40:
                path = motions[k % len(motions)]
                LIVE(100.0 * (ai + min(0.8, cur / max(END, 1) * 0.8)) / NAV, "%s ← %s (คลิป %d)" % (name, os.path.basename(path), ncl + 1))
                start = cur + (GAP if kw else 0.0)   # APART by GAP, never touching or overlapping (user 2026-11-22)
                RLPy.RFileIO.LoadMotion(path, T(start), a)
                clip = sk.GetClip(sk.GetClipCount() - 1)
                raw = clip.GetClipLength().ToFloat() / 6000.0
                if raw <= 0:
                    raise RuntimeError("motion load failed (len 0): " + path)
                speed = s.get("speed") or 1.0   # 1.0 = every frame a new pose at 60fps (iClone does not interpolate mocap keys)
                speed = max(MIN_SPEED, min(1.0, speed))
                clip.SetSpeed(speed)
                if kw: clip.SetTransitionRange(T(GAP + XOVER)); XOUT(prevclip, GAP, XOVER)   # fade-in + fade-out = the X
                st = clip.ClipTimeToSceneTime(T(0)).ToFloat() / 6000.0
                if kw: LOG.append("%s gap %.2f transition %.2f" % (name, st - cur, GAP + XOVER))
                LOG.append("%s %s at %.1f raw %.1fs speed %.2f -> %.1fs" % (name, os.path.basename(path), st, raw, speed, raw / speed))
                cur = st + raw / speed; k += 1; kw += 1; ncl += 1; prevclip = clip
            LOG.append("%s body %d clips in windows %s" % (name, ncl, ["%.1f-%.1f" % w for w in WINS(s, END)]))
        if "pos" in s:
            ctl = a.GetControl("Transform"); tr = RLPy.RTransform(); ctl.GetValue(T(0), tr)
            tr.T().x, tr.T().y, tr.T().z = s["pos"]
            h = math.radians(s.get("yaw", 0)) / 2; g = math.radians(s.get("pitch", 0)) / 2
            cy, sy, cz, sz = math.cos(g), math.sin(g), math.cos(h), math.sin(h)
            tr.R().x, tr.R().y, tr.R().z, tr.R().w = -sy * sz, sy * cz, cy * sz, cy * cz
            ctl.SetValue(T(0), tr)
        # Every character blinks (rules.md: auto blink 'Normal'; it was missing here until 2026-11-22, user noticed).
        # spec "blink": None/Normal/Nervous/Speechless/Charming/Child, default Normal.
        bl = s.get("blink", "Normal")
        a.GetFaceComponent().SetAutoBlinkName(bl)
        LOG.append("%s blink %s" % (name, bl))
        # Look At is appropriate for conversation, not for independent physical work.
        # Explicit False clears prior tracking weights from loaded projects, both body and eyes.
        if s.get("lookat") is False:
            la = sk.GetLookAtComponent()
            for is_body in (True, False):
                data = la.GetLookAtWeightDataBlock(is_body)
                for att in (data.GetAttributes() if data else []):
                    ctrl = data.GetControl(att.GetName())
                    ctrl.ClearKeys()
                    ctrl.SetValue(T(0), 0.0)
                    ctrl.SetValue(T(END), 0.0)
            LOG.append("%s work mode: look-at body/eyes disabled for all part" % name)
        # FACE FLOW (user 2026-11-22): 1 auto blink (above) -> 2 face motion (.iTalk clips) -> 3 feeling keys
        # (smile/think/face, below). The clips go FIRST: keys added before a clip load get lost.
        # "faces": [.iTalk, ...] chained over the whole part like body motions: speed 0.65-0.75, back to back
        # (never overlapping), each later clip blended in by its transition range. Old "lookfront" = one clip.
        faces = s.get("faces") or ([s["lookfront"] if isinstance(s["lookfront"], str) else LOOKFRONT] if s.get("lookfront") else [])
        faces = [f for f in faces if f]
        fc = a.GetFaceComponent()
        while fc.GetClipCount():
            fc.DeleteClip(fc.GetClip(0))
        if faces:
            fsp = max(0.65, min(0.75, float(s.get("face_speed", 0.7))))
            k = 0
            for (w0, w1) in WINS(s, END):
              cur = w0; kw = 0; prev_end = w0
              while cur < w1 - 0.1 and kw < 60:
                path = faces[k % len(faces)]
                if kw: cur += FGAP   # APART, gap filled by the transition (user 2026-11-22)
                RLPy.RGlobal.SetTime(T(cur))
                RLPy.RScene.ClearSelectObjects(); RLPy.RScene.SelectObject(a)
                n0 = fc.GetClipCount(); RLPy.RFileIO.LoadFile(path); RLPy.RScene.ClearSelectObjects()
                if fc.GetClipCount() <= n0:
                    raise RuntimeError("face clip did not load: %s on %s" % (path, name))
                clip = fc.GetClip(fc.GetClipCount() - 1)
                raw = clip.GetClipLength().ToFloat() / 6000.0
                if raw <= 0: raise RuntimeError("face clip len 0: " + path)
                clip.SetSpeed(fsp)
                if kw: clip.SetTransitionRange(T(FGAP + FXOVER)); XOUT(prevclip, FGAP, FXOVER)
                st = clip.ClipTimeToSceneTime(T(0)).ToFloat() / 6000.0
                if kw: LOG.append("%s face gap %.2f" % (name, st - prev_end))
                LOG.append("%s face %s at %.1f (clip starts %.1f) raw %.1fs speed %.2f -> %.1fs" % (name, os.path.basename(path), cur, st, raw, fsp, raw / fsp))
                cur = st + raw / fsp; prev_end = cur; k += 1; kw += 1; prevclip = clip
            RLPy.RGlobal.SetTime(T(0))
        else:
            LOG.append("%s face NONE" % name)
        if s.get("lookat"):
            la = sk.GetLookAtComponent()
            la.AddLookAtKey(T(0), T(1), head(av[s["lookat"]]), s.get("lookat_strength", 1.0), 0.0)
            LOG.append("%s lookat %s" % (name, s["lookat"]))
        if s.get("smile"):   # user 2026-11-22: smile RAMPS UP slowly in every visible window - starts ~10%,
            # ends at the peak; peak never over 0.8 (a 100% smile looks like a Joker). Same breathing wobble.
            PEAK = min(0.8, float(s["smile"])); W0 = min(0.1, PEAK); fc = a.GetFaceComponent()
            NM = ["Mouth_Corner_Up_L", "Mouth_Corner_Up_R", "Mouth_Corner_Pull_L", "Mouth_Corner_Pull_R",
                  "Eye_Cheek_Raise_L", "Eye_Cheek_Raise_R", "Brow_Raise_Outer_L", "Brow_Raise_Outer_R",
                  "Mouth_Corner_Down_L", "Mouth_Corner_Down_R", "Brow_Drop_L", "Brow_Drop_R", "Brow_Compress_L", "Brow_Compress_R"]
            WT = lambda W: [0.8 * W, 0.8 * W, 0.55 * W, 0.55 * W, 0.6 * W, 0.6 * W, 0.2 * W, 0.2 * W] + [0.0] * 6
            vis = sorted(s.get("visible") or [[0, 1]]); wins = []
            for i, (t0, on) in enumerate(vis):
                t1 = vis[i + 1][0] if i + 1 < len(vis) else END
                if on and t1 - t0 > 0.3: wins.append((t0, t1))
            fc.BeginKeyEditing(); fc.AddExpressionKeys(T(0), NM, WT(W0), T(0.1))
            for (t0, t1) in wins:
                fc.AddExpressionKeys(T(t0), NM, WT(W0), T(0.05))   # every shot starts with a small smile
                t = t0 + 1.5
                while t < t1 - 0.2:
                    f = (t - t0) / (t1 - t0); W = W0 + (PEAK - W0) * f
                    fc.AddExpressionKeys(T(t), NM, [w * (0.93 + 0.07 * ((int(t) % 3) / 2.0)) for w in WT(W)], T(1.5)); t += 1.5
                fc.AddExpressionKeys(T(t1), NM, WT(PEAK), T(0.8))
            fc.EndKeyEditing()
            LOG.append("%s smile ramp %.2f->%.2f in %d windows" % (name, W0, PEAK, len(wins)))
        if s.get("think"):   # user 2026-11-22: thinking moments need a visible thinking face, not a blank one
            # "think": true (whole part) or [t0, t1]. Inner brows up, slight squint, lips pressed, eyes drift
            # up-left / up-right and back every ~3 s. Adds on top of the Considering_F face clip.
            t0, t1 = (0.0, END) if s["think"] is True else (float(s["think"][0]), float(s["think"][1]))
            f = a.GetFaceComponent()
            BASE = {"Brow_Raise_In_L": 0.55, "Brow_Raise_In_R": 0.55, "Brow_Lateral_L": 0.25, "Brow_Lateral_R": 0.25,
                    "Eye_Squint_Inner_L": 0.25, "Eye_Squint_Inner_R": 0.25, "Mouth_Lips_Press_L": 0.45, "Mouth_Lips_Press_R": 0.45,
                    "Mouth_Left": 0.15}
            LOOK = [{"Eye_Look_Up_L": 0.4, "Eye_Look_Up_R": 0.4, "Eye_Look_Left_L": 0.35, "Eye_Look_Left_R": 0.35},
                    {"Eye_Look_Up_L": 0.15, "Eye_Look_Up_R": 0.15},
                    {"Eye_Look_Up_L": 0.35, "Eye_Look_Up_R": 0.35, "Eye_Look_Right_L": 0.3, "Eye_Look_Right_R": 0.3}]
            EYES = sorted({k for d in LOOK for k in d})
            NM = list(BASE) + EYES
            f.BeginKeyEditing()
            f.AddExpressionKeys(T(max(0.0, t0 - 0.5)), NM, [0.0] * len(NM), T(0.1))
            t, i = t0, 0
            while t < t1 - 0.5:
                look = LOOK[i % len(LOOK)]
                f.AddExpressionKeys(T(t), NM, [BASE[k] for k in BASE] + [look.get(k, 0.0) for k in EYES], T(0.8))
                t += 3.0; i += 1
            f.AddExpressionKeys(T(t1), NM, [0.0] * len(NM), T(0.6))
            f.EndKeyEditing()
            LOG.append("%s think %.1f-%.1f (%d looks)" % (name, t0, t1, i))
        if s.get("face"):
            f = a.GetFaceComponent(); names = list(s["face"]); vals = [s["face"][k] for k in names]
            f.BeginKeyEditing()
            for t in (0.0, END):
                f.AddExpressionKeys(T(t), names, vals, T(0.5))
            f.EndKeyEditing()
        # "swing": {"bones": ["CC_Base_L_Calf", "CC_Base_R_Calf"], "axis": "X", "deg": 15, "period": 1.6, "t": [a, b]}
        # gentle alternating leg swing on the Edit Motion Layer (pose-bones skill), keyed every quarter period
        sw = s.get("swing")
        if sw:
            bones = {b.GetName(): b for b in sk.GetSkinBones()}
            if not sk.GetClipCount(): sk.AddClip(T(0))
            # Layer keys live on a clip in CLIP-LOCAL time: key each time on the last clip that starts before it
            clips = sorted((sk.GetClip(i) for i in range(sk.GetClipCount())), key=lambda c: c.ClipTimeToSceneTime(T(0)).ToFloat())
            a0, b0 = sw.get("t", [0, END]); per = sw.get("period", 1.6); amp = math.radians(sw.get("deg", 15))
            for j, bn in enumerate(sw.get("bones", ["CC_Base_L_Calf", "CC_Base_R_Calf"])):
                t = a0; ph = math.pi * j   # left and right in opposite phase
                while t <= b0 + 1e-6:
                    c = [c for c in clips if c.ClipTimeToSceneTime(T(0)).ToFloat() / 6000.0 <= t + 1e-6][-1]
                    ctl = c.GetControl("Layer", bones[bn]).GetDataBlock().GetControl("Rotation/Rotation" + sw.get("axis", "X"))
                    ctl.SetValue(c.SceneTimeToClipTime(T(t)), amp * math.sin(2 * math.pi * (t - a0) / per + ph))
                    t += per / 8
            a.Update()   # layer keys do nothing until the avatar is updated (ic8_pose_face.py)
            LOG.append("%s clips at %s" % (name, [round(c.ClipTimeToSceneTime(T(0)).ToFloat() / 6000.0, 1) for c in clips]))
            LOG.append("%s swing %s %.0fdeg period %.1fs %.1f-%.1f" % (name, sw.get("bones"), sw.get("deg", 15), per, a0, b0))
        # "bones": {"CC_Base_R_Upperarm": [x, y, z], ...} degrees on the Edit Motion Layer, held for the whole
        # part (a still POSE on top of a calm idle, e.g. holding a plate). Keyed at start + end of EVERY clip.
        if s.get("bones"):
            bones = {b.GetName(): b for b in sk.GetSkinBones()}
            if not sk.GetClipCount(): sk.AddClip(T(0))
            for i in range(sk.GetClipCount()):
                c = sk.GetClip(i); ln = c.GetClipLength()
                for bn, xyz in s["bones"].items():
                    if bn not in bones: LOG.append("%s no bone %s" % (name, bn)); continue
                    db = c.GetControl("Layer", bones[bn]).GetDataBlock()
                    for ax, deg in zip("XYZ", xyz):
                        ctl = db.GetControl("Rotation/Rotation" + ax)
                        for tt in (RLPy.RTime.FromValue(0), ln):
                            ctl.SetValue(tt, math.radians(deg))
            a.Update()
            LOG.append("%s pose bones %s on %d clip(s)" % (name, s["bones"], sk.GetClipCount()))
        LIVE(100.0 * (ai + 0.85) / NAV, "%s: ตั้งตำแหน่ง/การมองเห็น" % name)
        vis = sorted(s.get("visible", []))
        for t, v in vis:
            a.SetVisible(T(t), bool(v))
        if len(vis) > 1:   # old keys from earlier runs survive (no API to delete them): scan every frame, key over any mismatch
            want = lambda tt: bool([v for t, v in vis if t <= tt + 1e-6][-1]) if tt + 1e-6 >= vis[0][0] else bool(vis[0][1])
            # coarse 1 s pass (per-frame over the whole part was minutes slow); on a mismatch step back frame by frame
            fixed = 0
            f = 0
            while f / 60.0 <= END + 1e-6:
                tt = f / 60.0
                if a.IsVisible(T(tt)) != want(tt) and fixed < 200:
                    g = f
                    while g > max(0, f - 60) and a.IsVisible(T((g - 1) / 60.0)) != want((g - 1) / 60.0): g -= 1
                    a.SetVisible(T(g / 60.0), want(g / 60.0)); fixed += 1
                    continue   # re-check the same time after the fix
                f += 60
            if fixed: LOG.append("%s visible: overwrote %d stale key(s)" % (name, fixed))
    RLPy.RGlobal.SetTime(T(0))
    LIVE(100, "เสร็จ")
    LOG.append("DONE")
except Exception:
    LOG.append("ERROR\n" + traceback.format_exc())
open(os.path.join(J, "pose_place.log.txt"), "w", encoding="utf-8").write("\n".join(LOG))
