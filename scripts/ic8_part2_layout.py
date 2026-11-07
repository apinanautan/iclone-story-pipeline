# Part 2 layout (user): villagers in two rows facing each other, monk at the head (far end, +Y side) in the middle.
# Moves avatars (frame-0 transform key only; AccuPOSE poses stay) and re-aims each FaceLight_<id>.
import math, os
import RLPy

J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
CX, CY, Z0 = 33.0, 566.0, 25774.0      # marker Box_001 centre, floor height
GAP = 130.0                             # half distance between the two rows
# yaw: 0 = faces -Y, 90 = faces +X, -90 = faces -X
SEATS = {
    "monk":  (CX, CY + 330, 0),                 # head of the table, faces down the aisle
    "im":    (CX - GAP, CY + 170, 90),          # left row, faces right
    "old":   (CX - GAP, CY + 20, 90),
    "young": (CX - GAP, CY - 130, 90),
    "woman": (CX + GAP, CY + 120, -90),         # right row, faces left
    "commf": (CX + GAP, CY - 50, -90),
}


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


log = []
avs = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
lts = {l.GetName(): l for l in RLPy.RScene.FindObjects(RLPy.EObjectType_Light)}
for key, (x, y, yaw) in SEATS.items():
    av = avs.get("p2_" + key)
    if not av:
        log.append("missing " + key); continue
    setT(av, (x, y, Z0), zq(yaw))
    lt = lts.get("FaceLight_" + key)
    if lt:
        fdir = (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))
        side = (-fdir[1], fdir[0])
        face = (x, y, Z0 + 95)
        lp = (x + fdir[0] * 220 + side[0] * 120, y + fdir[1] * 220 + side[1] * 120, Z0 + 150)
        setT(lt, lp, look(lp, face))
    log.append("%s -> (%.0f,%.0f) yaw %d" % (key, x, y, yaw))
RLPy.RGlobal.SetTime(T(0))
open(os.path.join(J, "layout_log.txt"), "w", encoding="utf-8").write("\n".join(log))
