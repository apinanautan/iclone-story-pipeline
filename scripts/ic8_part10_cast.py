# Part 7 cast: Naai Im + Seeka Oi standing. (copy of part 3 build): scene วัด(ยังไม่มีร้านกาแฟ)150. Believers kneel in front of Thao Wessuwan (node_3) between
# the two Naga statues; the monk stands in front of the temple stairs with one believer kneeling before him.
# Loads cast, places them, monk body = Stand00 slowed, face = Look front slowed, auto blink, soft face light
# (only if the scene has a "Spotlight" to clone). Kneeling poses: AccuPOSE in the GUI afterwards.
# Re-runnable. Log: ic8_jobs\p10_cast_log.txt, overview still p3_top.png
import math, os, traceback
import RLPy

J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
CH = r"G:\ไดรฟ์ของฉัน\มหาอกหัก (นิทาน)\มหาอกหัก"
MO = r"G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น"
FACE = MO + r"\Digital Soul 100+\1.Watch\Look front.iTalk"
STAND = MO + r"\Stand00.iMotion"
L = 13.84
Z0 = 0.0
# yaw: 0 = faces -Y (toward the statues), 180 = faces +Y
CAST = {
    "monk": ('1. พระมหาสมชาติ\\พระมหาสมชาติ เจ้าอาวาส วัย 48.iAvatar', (-860,450,0), STAND),
    "oi": (r"5. สีกาอ๋อย\สีกาอ๋อย หญิงหม้ายดูสาว วัย 40.iAvatar", (-860,300,180), None),
}
ONLY = None  # one character per job (iClone froze loading all at once); 'still' = overview only
log = []


def T(s):
    return RLPy.RTime.FromValue(int(round(s * 6000)))


def zq(d):
    h = math.radians(d) / 2
    return (0.0, 0.0, math.sin(h), math.cos(h))


def qm(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)


def look(cp, tg):
    dx, dy, dz = tg[0]-cp[0], tg[1]-cp[1], tg[2]-cp[2]
    p = math.atan2(dz, math.hypot(dx, dy))
    return qm(zq(math.degrees(math.atan2(-dx, dy))), qm((math.sin(p/2), 0, 0, math.cos(p/2)), (math.sin(math.radians(45)), 0, 0, math.cos(math.radians(45)))))


def setT(obj, pos, q):
    c = obj.GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
    t.T().x, t.T().y, t.T().z = pos
    t.R().x, t.R().y, t.R().z, t.R().w = q
    c.SetValue(T(0), t)


def fill(clip):
    clip.SetSpeed(1.0)
    raw = clip.GetClipLength().ToFloat() / 6000
    sp = max(0.5, raw / L)
    clip.SetSpeed(sp)
    return raw / sp, sp


try:
    RLPy.RGlobal.SetProjectLength(T(L)); RLPy.RGlobal.SetEndTime(T(L))
    lights = {l.GetName(): l for l in RLPy.RScene.FindObjects(RLPy.EObjectType_Light)}
    spot = [l for l in lights.values() if l.GetName() in ("Spotlight", "Spot")] or \
           [l for l in lights.values() if "spot" in l.GetName().lower()]
    log.append("lights: " + ", ".join(lights))
    for key, (f, (x, y, yaw), body) in CAST.items():
        if ONLY != key: continue
        name = "p3_" + key
        av = next((a for a in RLPy.RScene.GetAvatars() if a.GetName() == name), None)
        if not av:
            before = set(a.GetID() for a in RLPy.RScene.GetAvatars())
            RLPy.RScene.ClearSelectObjects()
            RLPy.RFileIO.LoadFile(os.path.join(CH, f))
            av = [a for a in RLPy.RScene.GetAvatars() if a.GetID() not in before][0]
            av.SetName(name)
        RLPy.RGlobal.RemoveAllAnimations(av)
        setT(av, (x, y, Z0), zq(yaw))
        sk = av.GetSkeletonComponent()
        cur = 0.0
        while body and cur < L - 0.05:
            RLPy.RFileIO.LoadMotion(body, T(cur), av)
            cl = sk.GetClip(sk.GetClipCount() - 1)
            d, sp = fill(cl)
            if cur + d > L:
                cl.SetLength(T((L - cur) * sp))
            cur += d
        fc = av.GetFaceComponent()
        RLPy.RScene.ClearSelectObjects(); RLPy.RScene.SelectObject(av)
        cur = 0.0
        while body and cur < L - 0.05:
            RLPy.RGlobal.SetTime(T(cur))
            RLPy.RFileIO.LoadFile(FACE)
            cl = fc.GetClip(fc.GetClipCount() - 1)
            d, sp = fill(cl)
            cur += d
        fc.SetAutoBlinkName("Normal")
        lname = "FaceLight_" + key
        lt = lights.get(lname)
        if not lt and spot:
            lt = spot[0].Clone(); lt.SetName(lname)
        if lt:
            fz = Z0 + (160 if body else 95)
            fdir = (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))
            side = (-fdir[1], fdir[0])
            lp = (x + fdir[0] * 220 + side[0] * 120, y + fdir[1] * 220 + side[1] * 120, fz + 55)
            setT(lt, lp, look(lp, (x, y, fz)))
            lt.SetColor(T(0), RLPy.RRgb(255, 236, 214)); lt.SetMultiplier(T(0), 0.04)
            lt.SetRange(T(0), 700); lt.SetCastShadow(False)
        log.append("%s (%.0f,%.0f) yaw %d body %d face %d light %s" % (name, x, y, yaw, sk.GetClipCount(), fc.GetClipCount(), bool(lt)))

    if ONLY != 'still': raise SystemExit
    cam = [c for c in RLPy.RScene.GetCameras()][0]
    RLPy.RGlobal.RemoveAllAnimations(cam)
    cam.SetFocalLength(T(0), 35)
    d = RLPy.RCameraDofData(); d.SetEnable(False); k = RLPy.RKey(); k.SetTime(T(0)); cam.AddDofKey(k, d)
    cp = (-300, 900, 350)
    setT(cam, cp, look(cp, (500, -500, 60)))
    RLPy.RScene.SetCurrentCamera(cam)
    RLPy.RGlobal.SetTime(T(3))
    RLPy.RGlobal.RenderImage(os.path.join(J, "p3_top.png"))
except SystemExit:
    pass
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p10_cast_log.txt"), "a", encoding="utf-8").write("\n".join(log))
