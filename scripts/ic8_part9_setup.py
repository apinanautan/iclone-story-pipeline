# Part 9 setup (narration only, 26.1 s audio + 5 s tail = 31.1 s): project length.
import RLPy, os, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    RLPy.RGlobal.SetProjectLength(T(31.1)); RLPy.RGlobal.SetEndTime(T(31.1))
    log.append("end %.2f" % (RLPy.RGlobal.GetEndTime().ToFloat() / 6000.0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p9_setup.txt"), "w", encoding="utf-8").write("\n".join(log))
