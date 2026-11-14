# Part 7: slow head nods (different period/phase) for p3_im / p3_oi + both look at the monk's head (rule: standing people look at who they face).
import os, random, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
L = 28.0
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
rnd = random.Random(31)
try:
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    monk_head = next(b for b in av["p3_monk"].GetSkeletonComponent().GetSkinBones() if b.GetName().endswith("Head"))
    for name in ("p3_im", "p3_oi"):
        a = av[name]
        fc = a.GetFaceComponent()
        period = rnd.uniform(4.5, 7.5); amp = rnd.uniform(0.18, 0.30)
        t = rnd.uniform(0.0, period / 2); down = rnd.random() < 0.5; n = 0
        fc.BeginKeyEditing()
        fc.AddExpressionKeys(T(0), ["Head_Turn_Down", "Head_Turn_Up"], [0.0, 0.0], T(0.5))
        while t < L:
            w = amp * rnd.uniform(0.8, 1.1)
            if down:
                fc.AddExpressionKeys(T(t), ["Head_Turn_Down", "Head_Turn_Up"], [w, 0.0], T(period / 2))
            else:
                fc.AddExpressionKeys(T(t), ["Head_Turn_Down", "Head_Turn_Up"], [0.0, w * 0.4], T(period / 2))
            down = not down; t += period / 2 * rnd.uniform(0.85, 1.15); n += 1
        fc.EndKeyEditing()
        try:
            a.GetSkeletonComponent().GetLookAtComponent().AddLookAtKey(T(0), T(1), monk_head, 1.0, 0.0)
            la = "lookat ok"
        except Exception as e:
            la = "lookat ERR %r" % e
        log.append("%s period %.1f amp %.2f keys %d %s" % (name, period, amp, n, la))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p7_cast_extras.txt"), "w", encoding="utf-8").write("\n".join(log))
