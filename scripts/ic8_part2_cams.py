# Part 2 cameras: one camera "Camera", hard cuts (hold keys + next shot 1/60 s later), DOF per shot,
# Switcher key at 0. Shots from docs/part2_plan.md. Framing = chest-up, eye level.
# Each shot: (start, end, subject avatar, angle deg from subject's facing dir, dist cm, focal, push_end_dist or None,
#             over-shoulder avatar or None)
# MODE "stills": also renders the middle of each shot to ic8_jobs\cam_NN.png
import math, os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
MODE = "stills"
END = 86.5
SHOTS = [
    (0.0,   7.0,   'p2_old',  -20, 270, 100, None, None),
    (7.0,   13.45, 'p2_monk',   0, 260, 100, None, None),
    (13.45, 24.88, 'p2_im',    20, 270, 100, None, None),
    (24.88, 31.74, 'p2_im',     0, 300, 100, None, 'GROUP'),
    (31.74, 40.81, 'p2_woman', -20, 270, 100, None, None),
    (40.81, 50.80, 'p2_young', -20, 270, 100, None, None),
    (50.80, 53.82, 'p2_commf',  0, 270, 100, None, None),
    (53.82, 75.5,  'p2_monk', -12, 330, 100, 270, None),
    (75.5,  END,   'p2_old',  -25, 270, 100, None, None),
]
FACE = {'p2_old': (1, 0), 'p2_im': (1, 0), 'p2_young': (1, 0), 'p2_woman': (-1, 0), 'p2_commf': (-1, 0), 'p2_monk': (0, -1)}
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)
def look(c, t):
    dx, dy, dz = t[0]-c[0], t[1]-c[1], t[2]-c[2]
    yaw = math.atan2(-dx, dy); pit = math.atan2(dz, math.hypot(dx, dy))
    qf = (math.sin(math.radians(45)), 0, 0, math.cos(math.radians(45)))
    return qmul((0, 0, math.sin(yaw/2), math.cos(yaw/2)), qmul((math.sin(pit/2), 0, 0, math.cos(pit/2)), qf))
try:
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    RLPy.RGlobal.SetTime(T(1))
    head = {}
    for n, a in av.items():
        b = [b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head')][0]
        h = b.WorldTransform().T(); head[n] = (h.x, h.y, h.z)
    cam = [c for c in RLPy.RScene.GetCameras() if c.GetName() == 'Camera'][0]
    RLPy.RGlobal.RemoveAllAnimations(cam)
    ctl = cam.GetControl("Transform")
    def setk(s, c, q, f, dist):
        t = RLPy.RTransform(); ctl.GetValue(T(s), t)
        t.T().x, t.T().y, t.T().z = c
        t.R().x, t.R().y, t.R().z, t.R().w = q
        ctl.SetValue(T(s), t)
        cam.SetFocalLength(T(s), f)
        d = RLPy.RCameraDofData(); d.SetEnable(True); d.SetFocus(dist); d.SetRange(30)
        d.SetFarTransitionRegion(120); d.SetNearTransitionRegion(60); d.SetFarBlurScale(1); d.SetNearBlurScale(1)
        k = RLPy.RKey(); k.SetTime(T(s)); cam.AddDofKey(k, d)
    mids = []
    for i, (s, e, n, ang, dist, f, push, ots) in enumerate(SHOTS):
        hx, hy, hz = head[n]
        tgt = (hx, hy, hz - 6)
        fx, fy = FACE[n]; a = math.radians(ang)
        dx, dy = fx*math.cos(a) - fy*math.sin(a), fx*math.sin(a) + fy*math.cos(a)
        tgt1 = tgt
        if ots == 'GROUP':  # villagers group view from behind the east row: foreground heads peek in, slow pan
            wx, wy, wz = head['p2_woman']
            # from the aisle's far (south) end, diagonally along the west row: heads overlap in depth
            c0 = (120, head['p2_young'][1] - 150, hz - 4)
            c1 = (105, head['p2_young'][1] - 130, hz - 4)
            tgt = (hx, (head['p2_im'][1] + head['p2_old'][1]) / 2, hz + 2)
            tgt1 = (hx, head['p2_old'][1] - 10, hz + 2)
        elif ots:  # camera just behind the shoulder of `ots`, looking at subject
            ox, oy, oz = head[ots]
            vx, vy = ox - hx, oy - hy; L = math.hypot(vx, vy)
            c0 = (ox + vx/L*60 + (-vy/L)*35, oy + vy/L*60 + (vx/L)*35, oz + 5)
            c1 = c0
        else:  # user: never static -> slow zoom (alternate in/out) + slow pan (orbit a few degrees)
            d1 = push or (dist * 0.85 if i % 2 == 0 else dist)
            if not push and i % 2: dist = dist * 0.85
            a1 = a + math.radians(5 if i % 2 == 0 else -5)
            ex, ey = fx*math.cos(a1) - fy*math.sin(a1), fx*math.sin(a1) + fy*math.cos(a1)
            c0 = (hx + dx*dist, hy + dy*dist, hz - 5)
            c1 = (hx + ex*d1, hy + ey*d1, hz - 5)
        e2 = e - 1/60.0 if e < END else e
        D0 = math.dist(c0, tgt); D1 = math.dist(c1, tgt1)
        setk(s, c0, look(c0, tgt), f, D0)
        setk(e2, c1, look(c1, tgt1), f, D1)
        mids.append((i, (s + e) / 2))
        log.append("shot %d %.2f-%.2f %s cam %s" % (i, s, e, n, tuple(round(v) for v in c0)))
    RLPy.RScene.ClearSwitchCameraKeys()
    RLPy.RScene.AddSwitchCameraKey(T(0), cam)
    RLPy.RScene.SetCurrentCamera(cam)
    if MODE == "stills":
        for i, m in mids:
            RLPy.RGlobal.SetTime(T(m))
            RLPy.RGlobal.RenderImage(os.path.join(J, "cam_%02d.png" % i))
    RLPy.RGlobal.SetTime(T(0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "cam_log.txt"), "w", encoding="utf-8").write("\n".join(log))
