"""Generic avatar staging, driven by ic8_jobs/pose_place.json (any story/part). Never saves.

place.json = {"end": 64.8, "avatars": {"<name>": {
    "motion": "G:/.../X.iMotion", "speed": 0.2,      # optional: replace body clips with ONE clip stretched to end
    "pos": [x, y, z], "yaw": deg, "pitch": deg,       # optional root placement (pitch = tilt back, negative = lean back)
    "lookfront": true,                                 # load Look front.iTalk (natural head motion)
    "lookat": "<other avatar name>",                   # head/eyes follow that avatar's head
    "face": {"Eye_Blink_L": 0.0, ...},                 # optional expression keys at 0 and end
    "visible": [[t, 0|1], ...]}}}
Log: ic8_jobs/pose_place.log.txt
"""
import RLPy, os, math, json, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
LOOKFRONT = r"G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Digital Soul 100+\1.Watch\Look front.iTalk"
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
LOG = []


def head(avatar):
    return next(b for b in avatar.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith("Head"))


try:
    p = json.load(open(os.path.join(J, "pose_place.json"), encoding="utf-8"))
    END = p["end"]
    RLPy.RGlobal.Stop()
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    for name, s in p["avatars"].items():
        a = av[name]
        sk = a.GetSkeletonComponent()
        motions = s.get("motions") or ([s["motion"]] if s.get("motion") else [])
        if motions:   # clips back to back, each slowed, until the part end
            while sk.GetClipCount():
                sk.DeleteClip(sk.GetClip(0))
            cur = 0.0
            for path in motions:
                if cur >= END - 0.1:
                    break
                RLPy.RFileIO.LoadMotion(path, T(cur), a)
                clip = sk.GetClip(sk.GetClipCount() - 1)
                raw = clip.GetClipLength().ToFloat() / 6000.0
                if raw <= 0:
                    raise RuntimeError("motion load failed (len 0): " + path)
                speed = s.get("speed") or max(0.15, min(0.30, raw / END))
                clip.SetSpeed(speed)
                LOG.append("%s %s at %.1f raw %.1fs speed %.2f -> %.1fs" % (name, os.path.basename(path), cur, raw, speed, raw / speed))
                cur += raw / speed
            if cur < END - 0.1:
                LOG.append("WARNING %s motion ends at %.1f < %.1f" % (name, cur, END))
        if "pos" in s:
            ctl = a.GetControl("Transform"); tr = RLPy.RTransform(); ctl.GetValue(T(0), tr)
            tr.T().x, tr.T().y, tr.T().z = s["pos"]
            h = math.radians(s.get("yaw", 0)) / 2; g = math.radians(s.get("pitch", 0)) / 2
            cy, sy, cz, sz = math.cos(g), math.sin(g), math.cos(h), math.sin(h)
            tr.R().x, tr.R().y, tr.R().z, tr.R().w = -sy * sz, sy * cz, cy * sz, cy * cz
            ctl.SetValue(T(0), tr)
        if s.get("lookfront"):
            RLPy.RScene.ClearSelectObjects(); RLPy.RScene.SelectObject(a)
            LOG.append("%s lookfront %s" % (name, RLPy.RFileIO.LoadFile(LOOKFRONT)))
            RLPy.RScene.ClearSelectObjects()
        if s.get("lookat"):
            la = sk.GetLookAtComponent()
            la.AddLookAtKey(T(0), T(1), head(av[s["lookat"]]), s.get("lookat_strength", 1.0), 0.0)
            LOG.append("%s lookat %s" % (name, s["lookat"]))
        if s.get("face"):
            f = a.GetFaceComponent(); names = list(s["face"]); vals = [s["face"][k] for k in names]
            f.BeginKeyEditing()
            for t in (0.0, END):
                f.AddExpressionKeys(T(t), names, vals, T(0.5))
            f.EndKeyEditing()
        for t, v in s.get("visible", []):
            a.SetVisible(T(t), bool(v))
    RLPy.RGlobal.SetTime(T(0))
    LOG.append("DONE")
except Exception:
    LOG.append("ERROR\n" + traceback.format_exc())
open(os.path.join(J, "pose_place.log.txt"), "w", encoding="utf-8").write("\n".join(LOG))
