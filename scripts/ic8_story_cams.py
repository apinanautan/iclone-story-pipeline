import os, math, traceback, RLPy
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
MODE = 'stills'   # 'stills' = render middle frame of every shot; 'keys' = keys only
L = 43.8
# start, end, focal, C0, C1, target
SHOTS = [
 (0.0, 10.4, 80, (-4150, -3760, 190), (-4150, -3754, 190), (-4150, -3180, 185)),
 (10.4, 18.0, 100, (-4118, -3560, 190), (-4118, -3556, 190), (-4128, -3165, 190)),
 (18.0, 25.4, 100, (-4177, -3408, 190), (-4173, -3406, 190), (-4105, -3180, 190)),
 (25.4, 30.5, 80, (-4125, -3471, 235), (-4128, -3468, 235), (-4200, -3180, 235)),
 (30.5, 36.2, 100, (-4127, -3378, 185), (-4125, -3376, 185), (-4150, -3150, 185)),
 (36.2, 43.8, 100, (-4246, -3405, 240), (-4249, -3403, 240), (-4200, -3180, 240)),
]
log = []
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
def qm(a, b):
    x, y, z, w = a; X, Y, Z, W = b
    return (w*X+x*W+y*Z-z*Y, w*Y-x*Z+y*W+z*X, w*Z+x*Y-y*X+z*W, w*W-x*X-y*Y-z*Z)
def look(c, t):
    dx, dy, dz = [t[i]-c[i] for i in range(3)]
    y = math.atan2(-dx, dy); p = math.atan2(dz, math.hypot(dx, dy))
    return qm((0, 0, math.sin(y/2), math.cos(y/2)), qm((math.sin(p/2), 0, 0, math.cos(p/2)), (math.sqrt(.5), 0, 0, math.sqrt(.5))))
def setkey(cam, s, pos, q):
    c = cam.GetControl('Transform'); t = RLPy.RTransform(); c.GetValue(T(s), t)
    t.T().x, t.T().y, t.T().z = pos; t.R().x, t.R().y, t.R().z, t.R().w = q
    c.SetValue(T(s), t)
try:
    cam = RLPy.RScene.GetCameras()[0]
    RLPy.RScene.SetCurrentCamera(cam)
    RLPy.RGlobal.RemoveAllAnimations(cam)
    fr = 1/60.0
    for i, (a, b, f, c0, c1, tg) in enumerate(SHOTS):
        stop = b - fr if i < len(SHOTS)-1 else b
        cam.SetFocalLength(T(a), f); cam.SetFocalLength(T(stop), f)
        q = look(c0, tg); q1 = look(c1, tg)
        n = max(1, int(round((stop - a) / 0.25)))
        for k in range(n + 1):   # dense keys on a straight line, constant speed
            u = k / n; s = a + (stop - a) * u
            pos = [c0[j] + (c1[j]-c0[j]) * u for j in range(3)]
            setkey(cam, s, pos, look(pos, tg))
        d = RLPy.RCameraDofData(); d.SetEnable(True); d.SetFocus(math.dist(c0, tg)); d.SetRange(250)
        d.SetFarTransitionRegion(150); d.SetNearTransitionRegion(80); d.SetFarBlurScale(1); d.SetNearBlurScale(1)
        k = RLPy.RKey(); k.SetTime(T(a)); cam.AddDofKey(k, d)
        log.append('shot %d %.1f-%.1f f%d' % (i+1, a, b, f))
    if MODE == 'stills':
        for i, (a, b, *_r) in enumerate(SHOTS):
            RLPy.RGlobal.SetTime(T((a + b) / 2))
            r = RLPy.RGlobal.RenderImage(os.path.join(J, 'p1_shot%d.png' % (i+1)))
            log.append('still %d %s' % (i+1, r))
    RLPy.RGlobal.SetTime(T(0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, 'p1_cams_log.txt'), 'w', encoding='utf-8').write('\n'.join(log))





