# Part 8 setup (narration only, 32.1 s audio + 5 s tail = 37.1 s): project length.
import RLPy, os, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    RLPy.RGlobal.SetProjectLength(T(37.1)); RLPy.RGlobal.SetEndTime(T(37.1))
    log.append("end %.2f" % (RLPy.RGlobal.GetEndTime().ToFloat() / 6000.0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p8_setup.txt"), "w", encoding="utf-8").write("\n".join(log))
