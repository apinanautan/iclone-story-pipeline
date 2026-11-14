# User (2026-11-07): heads must not look still -> slow up/down head motion for every character, each with its own
# period, phase and amount, so they don't move in sync. Uses face expression keys Head_Turn_Down / Head_Turn_Up
# (layered over the Look-front face clip; AccuPOSE body untouched). Re-runnable: keys are overwritten.
import os, random
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
PREFIX = "p3_x"
L = 40.7
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
rnd = random.Random(23)
for a in RLPy.RScene.GetAvatars():
    if not a.GetName().startswith(PREFIX):
        continue
    fc = a.GetFaceComponent()
    period = rnd.uniform(4.5, 7.5)            # seconds for one down-up cycle (slow)
    amp = rnd.uniform(0.18, 0.32)             # how far down
    if a.GetName().endswith("monk"):
        amp *= 0.6                            # the monk: calmer
    t = rnd.uniform(0.0, period / 2)          # different start for each person
    down = rnd.random() < 0.5
    n = 0
    fc.BeginKeyEditing()
    fc.AddExpressionKeys(T(0), ["Head_Turn_Down", "Head_Turn_Up"], [0.0, 0.0], T(0.5))
    while t < L:
        w = amp * rnd.uniform(0.8, 1.1)
        if down:
            fc.AddExpressionKeys(T(t), ["Head_Turn_Down", "Head_Turn_Up"], [w, 0.0], T(period / 2))
        else:
            fc.AddExpressionKeys(T(t), ["Head_Turn_Down", "Head_Turn_Up"], [0.0, w * 0.4], T(period / 2))
        down = not down
        t += period / 2 * rnd.uniform(0.85, 1.15)
        n += 1
    fc.EndKeyEditing()
    log.append("%s period %.1fs amp %.2f keys %d" % (a.GetName(), period, amp, n))
open(os.path.join(J, "nod6x_log.txt"), "w", encoding="utf-8").write("\n".join(log))
