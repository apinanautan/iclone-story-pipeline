# Lip-sync QA: close-up stills of each speaker at 2 speaking times + 1 silent time, via Camera_0.
# Output: ic8_jobs\mouth_<name>_<sec>.png + mouth_log.txt
import math, os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
SPK = {  # name: (facing dir x, y), [speaking secs], silent sec
    'p2_old': ((1, 0), [2.5, 3.8], 8.0),
    'p2_im': ((1, 0), [16.0, 20.0], 28.0),
    'p2_woman': ((-1, 0), [34.0, 38.0], 28.0),
    'p2_young': ((1, 0), [44.0, 48.0], 28.0),
}
log = []
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)
try:
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    cam = [c for c in RLPy.RScene.GetCameras() if c.GetName() == 'Camera_0'][0]
    RLPy.RScene.SetCurrentCamera(cam)
    RLPy.RGlobal.RemoveAllAnimations(cam)
    for n, ((fx, fy), talk, quiet) in SPK.items():
        a = av[n]
        RLPy.RGlobal.SetTime(T(talk[0]))
        head = [b for b in a.GetSkeletonComponent().GetSkinBones() if b.GetName().endswith('Head')][0]
        h = head.WorldTransform().T()
        hx, hy, hz = h.x, h.y, h.z + 8
        c = (hx + fx * 90, hy + fy * 90, hz)
        dx, dy = hx - c[0], hy - c[1]
        yaw = math.degrees(math.atan2(-dx, dy)) / 2
        q = qmul((0, 0, math.sin(math.radians(yaw)), math.cos(math.radians(yaw))), (math.sin(math.radians(45)), 0, 0, math.cos(math.radians(45))))
        ctl = cam.GetControl("Transform")
        for s in talk + [quiet]:
            t = RLPy.RTransform(); ctl.GetValue(T(s), t)
            t.T().x, t.T().y, t.T().z = c
            t.R().x, t.R().y, t.R().z, t.R().w = q
            ctl.SetValue(T(s), t)
            cam.SetFocalLength(T(s), 50)
            RLPy.RGlobal.SetTime(T(s))
            RLPy.RGlobal.RenderImage(os.path.join(J, "mouth_%s_%04.1f.png" % (n, s)))
        log.append("%s head %.0f %.0f %.0f ok" % (n, hx, hy, hz))
    RLPy.RGlobal.RemoveAllAnimations(cam)
    RLPy.RGlobal.SetTime(T(0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "mouth_log.txt"), "w", encoding="utf-8").write("\n".join(log))
