# Part 7 setup (narration only, 23.0 s audio + 5 s tail = 28.0 s): project length.
import RLPy, os, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    RLPy.RGlobal.SetProjectLength(T(28.0)); RLPy.RGlobal.SetEndTime(T(28.0))
    log.append("end %.2f" % (RLPy.RGlobal.GetEndTime().ToFloat() / 6000.0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p7_setup.txt"), "w", encoding="utf-8").write("\n".join(log))
