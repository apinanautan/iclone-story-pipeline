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


def LIVE(pct, text):   # live progress for the Preview program (progress_app.py reads ic8_jobs/live.json)
    try: open(os.path.join(J, "live.json"), "w", encoding="utf-8").write(json.dumps({"step": "pose", "pct": round(pct), "text": text, "time": time.time()}, ensure_ascii=False))
    except Exception: pass
MIN_SPEED = 0.65   # never slower: judder (user 2026-11-19)
XF = 2.0          # seconds of transition (blend) at the start of each chained clip; clips never overlap


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
            cur = float(s.get("motion_start", 0.0)); k = 0   # motion_start: shift clip joins out of the visible shots
            # speed 0.65-1.0 (user 2026-11-19): slower clips step at ~12 poses/s = visible judder.
            # Too short? cycle the motion list again with a crossfade instead of stretching.
            while cur < END - 0.1 and k < 40:
                path = motions[k % len(motions)]
                LIVE(100.0 * (ai + min(0.8, cur / max(END, 1) * 0.8)) / NAV, "%s ← %s (คลิป %d)" % (name, os.path.basename(path), k + 1))
                start = cur   # back to back, NO overlap (user 2026-11-21: overlapped clips look fast/awkward); the blend is the transition range
                RLPy.RFileIO.LoadMotion(path, T(start), a)
                clip = sk.GetClip(sk.GetClipCount() - 1)
                raw = clip.GetClipLength().ToFloat() / 6000.0
                if raw <= 0:
                    raise RuntimeError("motion load failed (len 0): " + path)
                speed = s.get("speed") or 1.0   # 1.0 = every frame a new pose at 60fps (iClone does not interpolate mocap keys)
                speed = max(MIN_SPEED, min(1.0, speed))
                clip.SetSpeed(speed)
                if k: clip.SetTransitionRange(T(min(XF, 0.4 * raw / speed)))
                LOG.append("%s %s at %.1f raw %.1fs speed %.2f -> %.1fs" % (name, os.path.basename(path), start, raw, speed, raw / speed))
                cur = start + raw / speed; k += 1
            if cur < END - 0.1:
                LOG.append("WARNING %s motion ends at %.1f < %.1f" % (name, cur, END))
        if "pos" in s:
            ctl = a.GetControl("Transform"); tr = RLPy.RTransform(); ctl.GetValue(T(0), tr)
            tr.T().x, tr.T().y, tr.T().z = s["pos"]
            h = math.radians(s.get("yaw", 0)) / 2; g = math.radians(s.get("pitch", 0)) / 2
            cy, sy, cz, sz = math.cos(g), math.sin(g), math.cos(h), math.sin(h)
            tr.R().x, tr.R().y, tr.R().z, tr.R().w = -sy * sz, sy * cz, cy * sz, cy * cz
            ctl.SetValue(T(0), tr)
        # Explicit working action: no automatic head look-front clip; preserve all body motion clips.
        if s.get("lookfront") is False:
            fc = a.GetFaceComponent()
            removed = fc.GetClipCount()
            while fc.GetClipCount():
                fc.DeleteClip(fc.GetClip(0))
            LOG.append("%s work mode: removed %d look-front/face clips" % (name, removed))
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
        if s.get("lookfront"):
            RLPy.RScene.ClearSelectObjects(); RLPy.RScene.SelectObject(a)
            fc_file = s["lookfront"] if isinstance(s["lookfront"], str) else LOOKFRONT
            if not fc_file: LOG.append("%s lookfront: no path (run through ic8_part.py)" % name)   # true = Look front, or a path to any .iTalk
            else: LOG.append("%s face clip %s %s" % (name, os.path.basename(fc_file), RLPy.RFileIO.LoadFile(fc_file)))
            RLPy.RScene.ClearSelectObjects()
        if s.get("lookat"):
            la = sk.GetLookAtComponent()
            la.AddLookAtKey(T(0), T(1), head(av[s["lookat"]]), s.get("lookat_strength", 1.0), 0.0)
            LOG.append("%s lookat %s" % (name, s["lookat"]))
        if s.get("smile"):   # gentle smile 0-1 over the whole part, breathing a little (user 2026-11-21: lovers smile)
            W = float(s["smile"]); fc = a.GetFaceComponent()
            NM = ["Mouth_Corner_Up_L", "Mouth_Corner_Up_R", "Mouth_Corner_Pull_L", "Mouth_Corner_Pull_R",
                  "Eye_Cheek_Raise_L", "Eye_Cheek_Raise_R", "Brow_Raise_Outer_L", "Brow_Raise_Outer_R",
                  "Mouth_Corner_Down_L", "Mouth_Corner_Down_R", "Brow_Drop_L", "Brow_Drop_R", "Brow_Compress_L", "Brow_Compress_R"]
            WT = [0.8 * W, 0.8 * W, 0.55 * W, 0.55 * W, 0.6 * W, 0.6 * W, 0.2 * W, 0.2 * W] + [0.0] * 6
            fc.BeginKeyEditing(); fc.AddExpressionKeys(T(0), NM, WT, T(0.1)); t = 4.0 + ai
            while t < END - 2:
                fc.AddExpressionKeys(T(t), NM, [w * (0.85 + 0.15 * ((int(t) % 3) / 2.0)) for w in WT], T(2.0)); t += 4.0
            fc.AddExpressionKeys(T(END), NM, WT, T(1.0)); fc.EndKeyEditing()
            LOG.append("%s smile %.2f" % (name, W))
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
