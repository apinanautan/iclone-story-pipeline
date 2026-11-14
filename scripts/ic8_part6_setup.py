# Part 6 setup (narration only, 35.7 s audio + 5 s tail = 40.7 s): project length.
import RLPy, os, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    RLPy.RGlobal.SetProjectLength(T(40.7)); RLPy.RGlobal.SetEndTime(T(40.7))
    log.append("end %.2f" % (RLPy.RGlobal.GetEndTime().ToFloat() / 6000.0))
    for a in RLPy.RScene.GetAvatars():
        if a.GetName().startswith("p3_"):
            v = a.GetVisemeComponent()
            log.append("%s viseme clips %d" % (a.GetName(), v.GetClipCount()))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p6_setup.txt"), "w", encoding="utf-8").write("\n".join(log))
