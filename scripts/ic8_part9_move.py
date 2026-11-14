# Part 9: workers clean the area in front of the temple stairs (floor is lit there; the north yard renders black in several shots).
# Moves p3_x1..x4, p3_im, p3_oi and their buckets (same offset as before). Im and Oi face each other (OTS shot).
import math, os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
NEW = {"p3_x1": (-1150, 300), "p3_x2": (-700, 330), "p3_x3": (-1050, 160), "p3_x4": (-720, 170), "p3_im": (-1085, 380), "p3_oi": (-1010, 370)}
BUCKET = {"bucket_1": "p3_x1", "bucket_2": "p3_x2", "bucket_3": "p3_x3", "bucket_4": "p3_x4", "bucket_5": "p3_oi"}
OLD = {"p3_x1": (720, -500), "p3_x2": (1160, -470), "p3_x3": (870, -250), "p3_x4": (1010, -280), "p3_oi": (602, -265)}
log = []


def zq(d):
    h = math.radians(d) / 2
    return (0.0, 0.0, math.sin(h), math.cos(h))


def put(o, x, y, yaw=None):
    c = o.GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
    t.T().x, t.T().y = x, y
    if yaw is not None:
        q = zq(yaw); t.R().x, t.R().y, t.R().z, t.R().w = q
    c.SetValue(T(0), t)


try:
    RLPy.RGlobal.SetTime(T(0))
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    pr = {p.GetName(): p for p in RLPy.RScene.GetProps()}
    dx = NEW["p3_oi"][0] - NEW["p3_im"][0]; dy = NEW["p3_oi"][1] - NEW["p3_im"][1]
    yim = math.degrees(math.atan2(dx, -dy))
    for n, (x, y) in NEW.items():
        put(av[n], x, y, yim if n == "p3_im" else (yim + 180 if n == "p3_oi" else None))
        log.append("%s -> (%d,%d)" % (n, x, y))
    for b, w in BUCKET.items():
        ox, oy = OLD[w]; wx, wy = NEW[w]
        c = pr[b].GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
        put(pr[b], t.T().x - ox + wx, t.T().y - oy + wy)
        log.append("%s moved with %s" % (b, w))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p9_move.txt"), "w", encoding="utf-8").write("\n".join(log))
