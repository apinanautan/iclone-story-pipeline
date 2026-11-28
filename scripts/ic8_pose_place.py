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
FGAP = 1.0        # same rule for face (.iTalk) clips; 1.0 not 0.6 (user 2026-11-22): some .iTalk grow ~0.4 s after load
XOVER = 1.5       # body; face uses FXOVER. Value copied from the user's own drag (2.48 s on a 1.0 s gap).
FXOVER = 1.0
def REND(c, sp):   # real scene end of a clip; re-applies the face speed when iClone reset it after a late load
    if sp and abs(c.GetSpeed() - sp) > 0.01: c.SetSpeed(sp)
    return c.ClipTimeToSceneTime(T(0)).ToFloat() / 6000.0 + c.GetClipLength().ToFloat() / 6000.0
def KT(t):   # feeling-key time, moved OUT of any gap between face clips: a key in a gap makes iClone stretch the
    for s0, e0, s1 in IVS:   # front clip up to the key and reset its speed to 100% (2026-11-22: joins came out 0.05 s)
        if e0 - 0.02 < t < s1 + 0.02: return T(e0 - 0.08 if t - e0 < s1 - t else s1 + 0.08)
    return T(t)
IVS = []
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
    w = w or [(0.0, end)]
    if s.get("motion_from") is not None:   # spec: start the first body clip earlier (pick a calmer phase of the motion)
        w[0] = (min(w[0][0], float(s["motion_from"])), w[0][1])
    return w


MINC, MAXC = 8.0, 20.0   # user 2026-11-22: one pose must not drag on (~1 min of folded arms); change it


def clip_end(st, dur, cuts, minc=MINC, maxc=MAXC):
    """Where this body clip should end (scene s). Prefer the first camera CUT at least `minc` s after the start
    and at most `maxc` s: the next clip then starts on the cut, so the pose change hides in the edit. No cut in
    range: stop at `maxc`. A clip shorter than that just ends by itself."""
    for c in sorted(cuts):
        if st + minc <= c <= st + min(dur, maxc) + 1e-6:
            return min(st + dur, c - GAP)
    return st + min(dur, maxc)


def head(avatar):
    return next(b for b in avatar.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith("Head"))



def reach_actor(a, target_avatar, spec, end):
    # Reuse the measured Edit Motion Layer Jacobian method used by chest_grip.
    # Only the declared work windows get an arm adjustment. No root/face edits.
    from PySide2 import QtWidgets
    sk=a.GetSkeletonComponent()
    bones={b.GetName():b for b in sk.GetSkinBones()}
    side=spec.get("side","R")
    joints=["CC_Base_"+side+"_Upperarm","CC_Base_"+side+"_Forearm"]
    hand=bones["CC_Base_"+side+"_Hand"]
    th=head(target_avatar)
    def xyz(b):
        v=b.WorldTransform().T(); return [v.x,v.y,v.z]
    def settle(t):
        RLPy.RGlobal.SetTime(T(t));QtWidgets.QApplication.processEvents()
        a.Update();target_avatar.Update();RLPy.RGlobal.ForceViewportUpdate()
    def dist(x,y):return math.sqrt(sum((a-b)**2 for a,b in zip(x,y)))
    def solve3(M,b):
        z=[list(row)+[v] for row,v in zip(M,b)]
        for k in range(3):
            q=max(range(k,3),key=lambda i:abs(z[i][k]));z[k],z[q]=z[q],z[k]
            v=z[k][k];z[k]=[x/v for x in z[k]]
            for j in range(3):
                if j!=k:
                    v=z[j][k];z[j]=[x-v*y for x,y in zip(z[j],z[k])]
        return [row[3] for row in z]
    for i in range(sk.GetClipCount()):
        c=sk.GetClip(i);ln=c.GetClipLength()
        start=c.ClipTimeToSceneTime(T(0)).ToFloat()/6000.
        stop=min(end,c.ClipTimeToSceneTime(ln).ToFloat()/6000.)
        for wi,(w0,w1) in enumerate(spec["windows"]):
            lo,hi=max(start,w0),min(stop,w1)
            if hi-lo<.7:continue
            sec=(lo+hi)/2.;tick=c.SceneTimeToClipTime(T(sec))
            controls=[]
            for bn in joints:
                db=c.GetControl("Layer",bones[bn]).GetDataBlock()
                controls.extend(db.GetControl("Rotation/Rotation"+ax) for ax in "XYZ")
            settle(sec)
            target=[x+y for x,y in zip(xyz(th),spec.get("window_offsets",[spec["offset"]]*len(spec["windows"]))[wi])]
            def apply(q):
                for ctrl,deg in zip(controls,q):ctrl.SetValue(tick,math.radians(deg))
                settle(sec);return xyz(hand)
            angles=[0.]*6;current=apply(angles);initial=dist(current,target)
            for _ in range(9):
                err=dist(current,target)
                if err<4.:break
                jac=[]
                for k in range(6):
                    q=angles[:];q[k]+=6.;v=apply(q)
                    jac.append([(v[j]-current[j])/6. for j in range(3)])
                M=[[sum(col[j]*col[k] for col in jac)+(.055 if j==k else 0) for k in range(3)] for j in range(3)]
                step=solve3(M,[target[j]-current[j] for j in range(3)])
                delta=[max(-22.,min(22.,sum(col[j]*step[j] for j in range(3)))) for col in jac]
                best=None
                for gain in (1.,.5,.25):
                    q=[max(-115.,min(115.,x+gain*d)) for x,d in zip(angles,delta)]
                    v=apply(q)
                    if dist(v,target)<err-.1:best=(q,v);break
                if best is None:break
                angles,current=best
            residual=dist(apply(angles),target)
            LOG.append("%s reach %d %.2fs initial %.1f cm final %.1f cm"%(a.GetName(),i,sec,initial,residual))
            if residual>14:raise RuntimeError("work hand target not reachable: %.1fcm"%residual)
            # Keep the achieved position across each work segment; ease out only outside the window.
            for t,q in [(max(start,lo-.5),[0.]*6),(lo,angles),(sec,angles),(hi-.02,angles),(min(stop,hi+.5),[0.]*6)]:
                if t<=lo-.01 or t>=hi+.01 or q is angles:
                    kt=c.SceneTimeToClipTime(T(t))
                    for ctrl,deg in zip(controls,q):ctrl.SetValue(kt,math.radians(deg))

try:
    p = json.load(open(os.path.join(J, "pose_place.json"), encoding="utf-8"))
    END = p["end"]
    CUTS = p.get("cuts", [])   # camera cut times: pose changes land on them
    RLPy.RGlobal.Stop()
    if RLPy.RGlobal.GetProjectLength().ToFloat() < T(END).ToFloat():
        RLPy.RGlobal.SetProjectLength(T(END))  # A short source timeline clamps animation and visibility keys.
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    NAV = len(p["avatars"])
    for ai, (name, s) in enumerate(p["avatars"].items()):
        a = av[name]
        LIVE(100.0 * ai / NAV, "%s: เริ่ม" % name)
        sk = a.GetSkeletonComponent()
        motions = s.get("motions") or ([s["motion"]] if s.get("motion") else [])
        if s.get("external_motion"):
            if not sk.GetClipCount(): raise RuntimeError("external motion not imported")
            clips=[sk.GetClip(i) for i in range(sk.GetClipCount())]
            lengths=[round(c.GetClipLength().ToFloat()/6000.0,2) for c in clips]
            LOG.append("%s external motion clips %s" % (name,lengths))
            if len(clips)!=1 or lengths[0]<END*.9: raise RuntimeError("external motion length/count not verified: "+str(lengths))
        if s.get("blender_pose") and s.get("neutral_body"):
            while sk.GetClipCount(): sk.DeleteClip(sk.GetClip(0))
            c=sk.AddClip(T(0))
            if c is None: raise RuntimeError("could not create neutral edit-layer clip")
            c.SetLength(T(END))
            if c.GetClipLength().ToFloat()<T(END-.1).ToFloat():
                raise RuntimeError("neutral clip length not supported: "+str(c.GetClipLength().ToFloat()))
            motions=[]
            LOG.append("%s neutral Blender pose base %.2fs" % (name,c.GetClipLength().ToFloat()/6000.0))
        if motions:   # clips back to back, each slowed, until the part end
            while sk.GetClipCount():
                sk.DeleteClip(sk.GetClip(0))
            k = 0; ncl = 0; prevclip = None
            # speed 0.65-1.0 (user 2026-11-19): slower clips step at ~12 poses/s = visible judder.
            for (w0, w1) in WINS(s, END):
              cur = w0; kw = 0
              if prevclip is not None:   # windows close together: one chain, the join gets gap + X (2026-11-22)
                  pend = REND(prevclip, None)
                  if w0 - pend < 3.0: cur = pend; kw = 1
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
                e = clip_end(st, raw / speed, CUTS, MINC, float(s.get("max_clip", MAXC)))
                if e < st + raw / speed - 0.05:
                    clip.SetLength(T((e - st) * speed))   # clip time = scene time x speed
                    LOG.append("%s   cut to %.1fs (ends %.1f)" % (name, e - st, e))
                cur = e; k += 1; kw += 1; ncl += 1; prevclip = clip
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
            k = 0; prevclip = None
            for (w0, w1) in WINS(s, END):
              cur = w0; kw = 0; prev_end = w0
              if prevclip is not None:
                  pend = REND(prevclip, fsp)
                  if w0 - pend < 3.0: cur = prev_end = pend; kw = 1
              while cur < w1 - 0.1 and kw < 60:
                path = faces[k % len(faces)]
                if kw: cur = prev_end = REND(prevclip, fsp)   # REAL end: some .iTalk finish loading late and reset speed
                if kw: cur += FGAP   # APART, gap filled by the transition (user 2026-11-22)
                RLPy.RGlobal.SetTime(T(cur))
                RLPy.RScene.ClearSelectObjects(); RLPy.RScene.SelectObject(a)
                n0 = fc.GetClipCount(); RLPy.RFileIO.LoadFile(path); RLPy.RScene.ClearSelectObjects()
                if fc.GetClipCount() <= n0:
                    raise RuntimeError("face clip did not load: %s on %s" % (path, name))
                # the NEW clip is the one not slowed yet (it is not always the last index - 2026-11-22 two face
                # clips stayed at 100% and their joins came out 0.2 s apart)
                new = [fc.GetClip(i) for i in range(fc.GetClipCount()) if abs(fc.GetClip(i).GetSpeed() - fsp) > 0.01]
                clip = new[-1] if new else fc.GetClip(fc.GetClipCount() - 1)
                if len(new) > 1: LOG.append("WARNING %s: %d unslowed face clips after loading %s" % (name, len(new), os.path.basename(path)))
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
        cl = sorted([(fc.GetClip(i).ClipTimeToSceneTime(T(0)).ToFloat() / 6000.0, fc.GetClip(i).GetClipLength().ToFloat() / 6000.0) for i in range(fc.GetClipCount())])
        IVS[:] = [(s0, s0 + l0, s1) for (s0, l0), (s1, _) in zip(cl, cl[1:])]   # (front start, front end, back start)
        if s.get("lookat_prop"):
            target = next(p for p in RLPy.RScene.GetProps() if p.GetName() == s["lookat_prop"])
            la = sk.GetLookAtComponent()
            result = la.AddLookAtKey(T(0), target)
            if result is not None and hasattr(result, "IsError") and result.IsError():
                raise RuntimeError("Look At prop failed: " + str(result))
            LOG.append("%s lookat prop %s result %s" % (name, target.GetName(), result))
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
            fc.BeginKeyEditing(); fc.AddExpressionKeys(KT(0), NM, WT(W0), T(0.1))
            for (t0, t1) in wins:
                fc.AddExpressionKeys(KT(t0), NM, WT(W0), T(0.05))   # every shot starts with a small smile
                t = t0 + 1.5
                while t < t1 - 0.2:
                    f = (t - t0) / (t1 - t0); W = W0 + (PEAK - W0) * f
                    fc.AddExpressionKeys(KT(t), NM, [w * (0.93 + 0.07 * ((int(t) % 3) / 2.0)) for w in WT(W)], T(1.5)); t += 1.5
                fc.AddExpressionKeys(KT(t1), NM, WT(PEAK), T(0.8))
            fc.EndKeyEditing()
            LOG.append("%s smile ramp %.2f->%.2f in %d windows" % (name, W0, PEAK, len(wins)))
        if s.get("think"):   # user 2026-11-22: thinking moments need a visible thinking face, not a blank one
            # "think": true (whole part) or [t0, t1]. Inner brows up, slight squint, lips pressed, eyes drift
            # up-left / up-right and back every ~3 s. Adds on top of the Considering_F face clip.
            th = s["think"]   # true, [t0, t1] or [[t0, t1], [t2, t3]] (several thinking moments, 2026-11-22)
            RNG = [[0.0, END]] if th is True else ([th] if not isinstance(th[0], list) else th)
            f = a.GetFaceComponent()
            BASE = {"Brow_Raise_In_L": 0.55, "Brow_Raise_In_R": 0.55, "Brow_Lateral_L": 0.25, "Brow_Lateral_R": 0.25,
                    "Eye_Squint_Inner_L": 0.25, "Eye_Squint_Inner_R": 0.25, "Mouth_Lips_Press_L": 0.45, "Mouth_Lips_Press_R": 0.45,
                    "Mouth_Left": 0.15}
            LOOK = [{"Eye_Look_Up_L": 0.4, "Eye_Look_Up_R": 0.4, "Eye_Look_Left_L": 0.35, "Eye_Look_Left_R": 0.35},
                    {"Eye_Look_Up_L": 0.15, "Eye_Look_Up_R": 0.15},
                    {"Eye_Look_Up_L": 0.35, "Eye_Look_Up_R": 0.35, "Eye_Look_Right_L": 0.3, "Eye_Look_Right_R": 0.3}]
            EYES = sorted({k for d in LOOK for k in d})
            NM = list(BASE) + EYES
            for t0, t1 in RNG:
                t0, t1 = float(t0), float(t1)
                f.BeginKeyEditing()
                f.AddExpressionKeys(KT(max(0.0, t0 - 0.5)), NM, [0.0] * len(NM), T(0.1))
                t, i = t0, 0
                while t < t1 - 0.5:
                    look = LOOK[i % len(LOOK)]
                    f.AddExpressionKeys(KT(t), NM, [BASE[k] for k in BASE] + [look.get(k, 0.0) for k in EYES], T(0.8))
                    t += 3.0; i += 1
                # hold the last look until 0.6 s before the end (a short range used to fade out over its whole length)
                f.AddExpressionKeys(KT(max(t0, t1 - 0.6)), NM, [BASE[k] for k in BASE] + [look.get(k, 0.0) for k in EYES], T(0.3))
                f.AddExpressionKeys(KT(t1), NM, [0.0] * len(NM), T(0.6))
                f.EndKeyEditing()
                LOG.append("%s think %.1f-%.1f (%d looks)" % (name, t0, t1, i))
        if s.get("face"):
            f = a.GetFaceComponent(); names = list(s["face"]); vals = [s["face"][k] for k in names]
            f.BeginKeyEditing()
            for t in (0.0, END):
                f.AddExpressionKeys(KT(t), names, vals, T(0.5))
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
        if s.get("chest_grip") and s.get("hold_prop"):
            # Solve arm edit-layer angles against a measured chest-space grip target.
            # The solver uses evaluated hand world coordinates, not guessed axis directions.
            from PySide2 import QtWidgets
            bmap = {b.GetName(): b for b in sk.GetSkinBones()}
            hg = s["hold_prop"]
            hb = bmap[hg["bone"]]; fb = bmap.get(hg.get("finger"))
            rb = bmap["CC_Base_R_Upperarm"]; lb = bmap["CC_Base_L_Upperarm"]
            joints = ["CC_Base_R_Upperarm", "CC_Base_R_Forearm"]
            def vec(b):
                v = b.WorldTransform().T()
                return [v.x, v.y, v.z]
            def grip():
                p = vec(hb)
                if fb:
                    q = vec(fb); p = [(x+y)*.5 for x,y in zip(p,q)]
                return p
            def settle(t):
                RLPy.RGlobal.SetTime(t)
                QtWidgets.QApplication.processEvents()
                a.Update()
                RLPy.RGlobal.ForceViewportUpdate()
            def dist(p,q):
                return math.sqrt(sum((x-y)**2 for x,y in zip(p,q)))
            def solve3(M, b):
                z=[list(row)+[v] for row,v in zip(M,b)]
                for k in range(3):
                    j=max(range(k,3),key=lambda j:abs(z[j][k]))
                    z[k],z[j]=z[j],z[k]
                    d=z[k][k]
                    if abs(d)<1e-8:return [0,0,0]
                    z[k]=[v/d for v in z[k]]
                    for j in range(3):
                        if j!=k:
                            d=z[j][k];z[j]=[v-d*w for v,w in zip(z[j],z[k])]
                return [row[3] for row in z]
            for i in range(sk.GetClipCount()):
                c=sk.GetClip(i); ln=c.GetClipLength()
                start=c.ClipTimeToSceneTime(T(0)).ToFloat()/6000.0
                sample=T(min(END-.03,start+.7))
                if s.get("upright_grip"):
                    # Correct leaning from the underlying idle using evaluated shoulder/pelvis positions.
                    pelvis=bmap.get("CC_Base_Hip") or bmap.get("CC_Base_Pelvis")
                    spine=bmap.get("CC_Base_Spine02")
                    if pelvis is not None and spine is not None:
                        db=c.GetControl("Layer",spine).GetDataBlock()
                        sc=[db.GetControl("Rotation/Rotation"+ax) for ax in "XYZ"]
                        def lean(q):
                            for ctrl,deg in zip(sc,q):
                                for tick in (T(0),ln):
                                    ctrl.SetValue(tick,math.radians(deg))
                            settle(sample)
                            rr,ll,pp=vec(rb),vec(lb),vec(pelvis)
                            v=[(rr[k]+ll[k])*.5-pp[k] for k in range(2)]
                            return math.hypot(*v)
                        ang=[0.,0.,0.]; before=lean(ang); err=before
                        for step in (6.,3.):
                            for k in range(3):
                                best=ang[:]
                                for direction in (-1.,1.):
                                    trial=ang[:];trial[k]=max(-15.,min(15.,ang[k]+direction*step))
                                    score=lean(trial)
                                    if score<err-.15:best,err=trial,score
                                ang=best
                        err=lean(ang)
                        LOG.append("%s upright clip %d lean %.1f -> %.1f cm" % (name,i,before,err))
                if s.get("blender_pose"):
                    # Transfer measured Blender rig segment directions through the existing
                    # edit layer, solving against this avatar rather than assuming bone axes.
                    segs=s["blender_pose"]["segments"]
                    rr,ll=vec(rb),vec(lb)
                    rx,ry=rr[0]-ll[0],rr[1]-ll[1]
                    norm=math.hypot(rx,ry)
                    if norm<1: raise RuntimeError("invalid shoulder frame")
                    rx,ry=rx/norm,ry/norm
                    def unit(v):
                        length=math.sqrt(sum(x*x for x in v))
                        if length<1e-4: raise RuntimeError("invalid segment vector")
                        return [x/length for x in v]
                    for bn in ("CC_Base_R_Upperarm","CC_Base_R_Forearm","CC_Base_R_Hand","CC_Base_L_Upperarm","CC_Base_L_Forearm","CC_Base_L_Hand"):
                        seg=segs[bn]; child=bmap[seg["child"]]
                        db=c.GetControl("Layer",bmap[bn]).GetDataBlock()
                        ctrls=[db.GetControl("Rotation/Rotation"+ax) for ax in "XYZ"]
                        x,y,z=seg["direction"]
                        wanted=unit([rx*x-ry*y,ry*x+rx*y,z])
                        def evaluate(q):
                            for ctrl,deg in zip(ctrls,q):
                                for tick in (T(0),ln): ctrl.SetValue(tick,math.radians(deg))
                            settle(sample)
                            v,w=vec(bmap[bn]),vec(child)
                            return unit([b-a for a,b in zip(v,w)])
                        q=list(s.get("bones",{}).get(bn,[0.,0.,0.]))
                        actual=evaluate(q)
                        for iteration in range(9):
                            err=dist(actual,wanted)
                            if err<.075:break
                            jac=[]
                            for k in range(3):
                                v=q[:];v[k]+=5.
                                w=evaluate(v)
                                jac.append([(w[j]-actual[j])/5. for j in range(3)])
                            M=[[sum(col[j]*col[k] for col in jac)+(.000045 if j==k else 0) for k in range(3)] for j in range(3)]
                            step=solve3(M,[wanted[j]-actual[j] for j in range(3)])
                            delta=[max(-35.,min(35.,sum(col[j]*step[j] for j in range(3)))) for col in jac]
                            improved=False
                            for gain in (1.,.5,.25):
                                v=[max(-160.,min(160.,old+gain*d)) for old,d in zip(q,delta)]
                                w=evaluate(v)
                                if dist(w,wanted)<err-.002:
                                    q,actual=v,w;improved=True;break
                            if not improved:break
                        actual=evaluate(q)
                        deg=math.degrees(math.acos(max(-1.,min(1.,sum(x*y for x,y in zip(actual,wanted))))))
                        LOG.append("%s Blender direction %s error %.1f deg layer %s" % (name,bn,deg,[round(v,1) for v in q]))
                        if deg>22: raise RuntimeError("Blender direction failed for "+bn+": %.1f deg"%deg)
                    continue
                controls=[]
                for bn in joints:
                    db=c.GetControl("Layer",bmap[bn]).GetDataBlock()
                    controls.extend(db.GetControl("Rotation/Rotation"+ax) for ax in "XYZ")
                angles=[float(x) for bn in joints for x in s.get("bones",{}).get(bn,[0,0,0])]
                def apply(q):
                    for ctrl,deg in zip(controls,q):
                        for tick in (T(0),ln):
                            ctrl.SetValue(tick,math.radians(deg))
                    settle(sample)
                    return grip()
                current=apply(angles)
                r,l=vec(rb),vec(lb)
                center=[(x+y)*.5 for x,y in zip(r,l)]
                side=[r[k]-center[k] for k in range(3)]
                side_len=max(1.,math.hypot(side[0],side[1]))
                target=[center[0]+side[0]/side_len*8,center[1]+side[1]/side_len*8+22,center[2]-(18 if s.get("upright_grip") else 13)]
                if not all(math.isfinite(x) and abs(x)<2000 for x in current+target):
                    raise RuntimeError("invalid evaluated grip target")
                initial=dist(current,target)
                for itr in range(9):
                    err=dist(current,target)
                    if err<3.0:break
                    jac=[]
                    for k in range(6):
                        q=angles[:];q[k]+=6.
                        p=apply(q)
                        jac.append([(p[j]-current[j])/6. for j in range(3)])
                    M=[[sum(col[j]*col[k] for col in jac)+(0.055 if j==k else 0) for k in range(3)] for j in range(3)]
                    step=solve3(M,[target[j]-current[j] for j in range(3)])
                    delta=[max(-22.,min(22.,sum(col[j]*step[j] for j in range(3)))) for col in jac]
                    best=None
                    for gain in (1.,.5,.25):
                        q=[max(-115.,min(115.,v+gain*d)) for v,d in zip(angles,delta)]
                        p=apply(q)
                        if dist(p,target)<err-.1:
                            best=(q,p);break
                    if best is None:
                        current=apply(angles);break
                    angles,current=best
                current=apply(angles)
                residual=dist(current,target)
                LOG.append("%s chest grip clip %d initial %.1f cm final %.1f cm target %s actual %s angles %s" % (name,i,initial,residual,[round(x,1) for x in target],[round(x,1) for x in current],[round(x,1) for x in angles]))
                if residual>12.:
                    raise RuntimeError("chest grip did not converge (%.1f cm)" % residual)

        if s.get("hand_gesture"):
            from PySide2 import QtWidgets
            root=os.path.join(os.environ["PUBLIC"],"Documents","Reallusion","Reallusion Templates","Animation","Gesture")
            candidates=[os.path.join(d,f) for d,_,fs in os.walk(root) for f in fs if f==s["hand_gesture"]]
            if len(candidates)!=1 or not candidates[0].lower().endswith(".ihand"): raise RuntimeError("missing or ambiguous native hand preset")
            RLPy.RGlobal.SetTime(T(0))
            RLPy.RScene.ClearSelectObjects()
            RLPy.RScene.SelectObject(a)
            before=sk.GetClipCount()
            status=RLPy.RFileIO.LoadFile(candidates[0])
            QtWidgets.QApplication.processEvents()
            a.Update()
            if status is not None and hasattr(status,"IsError") and status.IsError():raise RuntimeError("hand gesture rejected: "+str(status))
            if sk.GetClipCount()!=before:raise RuntimeError("hand gesture changed body clip count")
            RLPy.RScene.ClearSelectObjects()
            LOG.append("%s loaded gesture %s status %s"%(name,s["hand_gesture"],status))
        if s.get("hold_prop"):
            # Generic world-space tracking of a handheld prop's grip pivot.
            from PySide2 import QtWidgets
            h = s["hold_prop"]
            prop = next(o for o in RLPy.RScene.GetProps() if o.GetName() == h["name"])
            bones = {b.GetName(): b for b in sk.GetSkinBones()}
            hand = bones[h["bone"]]; finger = bones.get(h.get("finger"))
            ctl = prop.GetControl("Transform"); tr = RLPy.RTransform()
            ctl.GetValue(T(0), tr); ctl.ClearKeys()
            samples = int(math.ceil(END * 4))
            for j in range(samples + 1):
                tt = min(END, j / 4.0)
                RLPy.RGlobal.SetTime(T(tt)); QtWidgets.QApplication.processEvents()
                a.Update(); RLPy.RGlobal.ForceViewportUpdate()
                v = hand.WorldTransform().T()
                if finger:
                    q = finger.WorldTransform().T()
                    x,y,z = ((v.x+q.x)*.5,(v.y+q.y)*.5,(v.z+q.z)*.5)
                else:
                    x,y,z = v.x,v.y,v.z
                if not all(math.isfinite(k) and abs(k)<2000 for k in (x,y,z)) or z<40: raise RuntimeError("invalid hand world position")
                tr.T().x,tr.T().y,tr.T().z = x,y,z
                ctl.SetValue(T(tt),tr)
            prop.Update()
            LOG.append("%s tracked prop %s with %d hand keys" % (name,h["name"],samples+1))
            if h.get("attach"):
                # Attach only after grip alignment; verify actual parent and spatial offset.
                RLPy.RGlobal.SetTime(T(0)); QtWidgets.QApplication.processEvents()
                a.Update(); prop.Update(); RLPy.RGlobal.ForceViewportUpdate()
                world=prop.WorldTransform()
                def xyz(tr):
                    v=tr.T(); return [v.x,v.y,v.z]
                def separation(u,v): return math.sqrt(sum((a-b)**2 for a,b in zip(u,v)))
                origin=xyz(world)
                if not hasattr(prop,"GetParent"): raise RuntimeError("Cannot verify Attach parent with this API")
                oldparent=prop.GetParent()
                if oldparent and oldparent.GetName()==hand.GetName():
                    LOG.append("%s already attached to %s"%(h["name"],hand.GetName()))
                else:
                    if oldparent and oldparent.GetName() not in ("Scene Root","Scene Root_root","Root","root"):
                        raise RuntimeError("Unexpected existing parent: "+oldparent.GetName())
                    # Preserve frame-zero world pose before converting to a single local key.
                    ctl.ClearKeys();ctl.SetValue(T(0),world);prop.Update()
                    status=prop.SetParent(hand)
                    parent=prop.GetParent()
                    if not parent or parent.GetName()!=hand.GetName() or (hasattr(status,"IsError") and status.IsError()):
                        raise RuntimeError("Attach to bone not supported by current API; actual parent "+str(parent.GetName() if parent else None))
                    prop.Update();RLPy.RGlobal.ForceViewportUpdate()
                    drift=separation(origin,xyz(prop.WorldTransform()))
                    if drift>2.0:
                        prop.SetParent(oldparent)
                        ctl=prop.GetControl("Transform");ctl.ClearKeys();ctl.SetValue(T(0),world);prop.Update()
                        raise RuntimeError("Attach changed aligned grip by %.1f cm; reverted parent"%drift)
                    local=prop.LocalTransform()
                    ctl=prop.GetControl("Transform");ctl.ClearKeys();ctl.SetValue(T(0),local);prop.Update()
                    start_local=xyz(local)
                    for seconds in (0.,END*.5,END-.05):
                        RLPy.RGlobal.SetTime(T(seconds));QtWidgets.QApplication.processEvents();a.Update();prop.Update()
                        if separation(start_local,xyz(prop.LocalTransform()))>1.: raise RuntimeError("Attached local offset changed")
                        if separation(xyz(prop.WorldTransform()),xyz(hand.WorldTransform()))>20.:raise RuntimeError("Attached prop not at hand")
                    LOG.append("%s ATTACH verified parent=%s, stable local offset, three times"%(h["name"],hand.GetName()))
                RLPy.RGlobal.SetTime(T(0))
        LIVE(100.0 * (ai + 0.85) / NAV, "%s: ตั้งตำแหน่ง/การมองเห็น" % name)
        vis = sorted(s.get("visible", []))
        for t, v in vis:
            a.SetVisible(T(t), bool(v))
        if vis:   # (2026-11-22: also for ONE key - part 5 kept part 4 hide keys) old keys from earlier runs survive (no API to delete them): scan every frame, key over any mismatch
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
    for name, cfg in p["avatars"].items():
        if cfg.get("reach_actor"):
            LIVE(95, "วางมือให้สัมพันธ์กับตัวละคร")
            reach_actor(av[name], av[cfg["reach_actor"]["name"]], cfg["reach_actor"], END)
    RLPy.RGlobal.SetTime(T(0))
    LIVE(100, "เสร็จ")
    LOG.append("DONE")
except Exception:
    LOG.append("ERROR\n" + traceback.format_exc())
open(os.path.join(J, "pose_place.log.txt"), "w", encoding="utf-8").write("\n".join(LOG))
