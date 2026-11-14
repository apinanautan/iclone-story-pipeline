# Part 8 cameras (same scene as part 3) (approved part 2 style): two cameras alternating via Switcher, dense linear keys (constant speed),
# slow zoom/pan, chest-up / centred, DOF on character shots, none on statue view shots.
# MODE "stills" renders the middle of every shot -> ic8_jobs\c3_NN.png
import math, os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
MODE = "stills"
END = 37.1
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
    H = {}
    for n, a in av.items():
        if n.startswith("p3_"):
            b = [b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head')][0]
            h = b.WorldTransform().T(); H[n[3:]] = (h.x, h.y, h.z)

    def front(n, ang, dist, dz=-5, face=(0, -1)):
        """camera position in front of head n, rotated ang degrees around it"""
        x, y, z = H[n]; a = math.radians(ang); fx, fy = face
        dx, dy = fx*math.cos(a) - fy*math.sin(a), fx*math.sin(a) + fy*math.cos(a)
        return (x + dx*dist, y + dy*dist, z + dz)

    def mid(*ns, dz=0):
        return tuple(sum(H[n][k] for n in ns) / len(ns) + (dz if k == 2 else 0) for k in range(3))

    hy = H['young']; hm = H['monk']; hw = H['woman']
    grp = mid('old', 'commf', 'young', 'girl')
    # (start, end, cam0, cam1, target0, target1, focal, dof range or None)
    SHOTS = [  # part 8 (37.1 s): folk-tale pacing, 7 shots (about one cut per 5 s)
        (0.0, 8.92, front('oi', -55, 300, dz=-3, face=(-1, 0)), front('oi', -53, 275, dz=-3, face=(-1, 0)), (H['oi'][0], H['oi'][1], H['oi'][2] - 3), (H['oi'][0], H['oi'][1], H['oi'][2] - 3), 100, 30),
        (8.92, 13.67, (700, -640, 100), (720, -625, 100), (grp[0] + 40, -470, 100), (grp[0] + 40, -470, 100), 80, 300),
        (13.67, 19.11, (H['im'][0] - 125, H['im'][1] + 68, H['im'][2] - 2), (H['im'][0] - 108, H['im'][1] + 60, H['im'][2] - 2), (H['oi'][0], H['oi'][1], H['oi'][2] - 3), (H['oi'][0], H['oi'][1], H['oi'][2] - 3), 100, 30),  # OTS over Naai Im's shoulder, focus Seeka Oi
        (19.11, 24.09, (700, 3150, 200), (720, 3000, 200), (973, -924, 600), (973, -924, 600), 80, None),  # left of the axis, WHOLE statue + both Nagas; the other north/east spots were inside roofs/trees
        (24.09, 28.10, front('oi', 55, 200, dz=-3, face=(-1, 0)), front('oi', 53, 215, dz=-3, face=(-1, 0)), (H['oi'][0], H['oi'][1], H['oi'][2] - 3), (H['oi'][0], H['oi'][1], H['oi'][2] - 3), 100, 30),
        (28.10, 31.55, (1200, -650, H['young'][2] - 3), (1180, -625, H['young'][2] - 3), mid('x4', 'young'), mid('x4', 'young'), 80, 250),  # from the south-east: no standing woman in the background
        (31.55, END, (-300, -600, 300), (-270, -590, 300), (grp[0], -420, 90), (grp[0], -420, 90), 80, None),  # (200,-1000) was inside the Naga head
    ]
    SLOW = 0.5  # user: camera must move even slower -> keep only half of each shot's travel
    SHOTS = [(a, b, c0, tuple(c0[q] + (c1[q] - c0[q]) * SLOW for q in range(3)), t0, t1, f, r) for (a, b, c0, c1, t0, t1, f, r) in SHOTS]
    CAMS = [c for n in ('Camera', 'Camera_0') for c in RLPy.RScene.GetCameras() if c.GetName() == n]
    for c in CAMS: RLPy.RGlobal.RemoveAllAnimations(c)

    def setk(cam, s, c, q, f, dist, rng):
        ctl = cam.GetControl("Transform")
        t = RLPy.RTransform(); ctl.GetValue(T(s), t)
        t.T().x, t.T().y, t.T().z = c
        t.R().x, t.R().y, t.R().z, t.R().w = q
        ctl.SetValue(T(s), t)
        cam.SetFocalLength(T(s), f)
        d = RLPy.RCameraDofData(); d.SetEnable(rng is not None)
        if rng is not None:
            d.SetFocus(dist); d.SetRange(rng); d.SetFarTransitionRegion(120); d.SetNearTransitionRegion(60)
            d.SetFarBlurScale(1); d.SetNearBlurScale(1)
        k = RLPy.RKey(); k.SetTime(T(s)); cam.AddDofKey(k, d)

    switch = []; mids = []
    for i, (s, e, c0, c1, t0, t1, f, rng) in enumerate(SHOTS):
        cam = CAMS[i % 2]; switch.append((s, cam))
        e2 = e - 1/60.0 if e < END else e
        nk = max(2, int((e2 - s) / 0.25) + 1)
        for j in range(-2, nk + 3):
            ts = s + (e2 - s) * j / nk
            if not 0 <= ts <= END: continue
            u = j / nk
            cu = tuple(c0[k] + (c1[k] - c0[k]) * u for k in range(3))
            tu = tuple(t0[k] + (t1[k] - t0[k]) * u for k in range(3))
            setk(cam, ts, cu, look(cu, tu), f, math.dist(cu, tu), rng)
        mids.append((i, (s + e) / 2))
        log.append("shot %d %.2f-%.2f cam %s" % (i, s, e, tuple(round(v) for v in c0)))
    RLPy.RScene.ClearSwitchCameraKeys()
    for s0, c in switch: RLPy.RScene.AddSwitchCameraKey(T(s0), c)
    if MODE == "stills":
        for i, m in mids:
            RLPy.RScene.SetCurrentCamera(switch[i][1])
            RLPy.RGlobal.SetTime(T(m))
            RLPy.RGlobal.RenderImage(os.path.join(J, "c8_%02d.png" % i))
    RLPy.RScene.SetCurrentCamera(CAMS[0])
    RLPy.RGlobal.SetTime(T(0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "c8_log.txt"), "w", encoding="utf-8").write("\n".join(log))
