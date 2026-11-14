# Part 5 setup (narration only, 20.4 s audio + 5 s tail = 25.4 s): project length + remove the monk's viseme clip.
import RLPy, os, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    RLPy.RGlobal.SetProjectLength(T(25.4)); RLPy.RGlobal.SetEndTime(T(25.4))
    log.append("end %.2f" % (RLPy.RGlobal.GetEndTime().ToFloat() / 6000.0))
    m = next(a for a in RLPy.RScene.GetAvatars() if a.GetName() == "p3_monk")
    v = m.GetVisemeComponent()
    log.append("viseme clips before %d" % v.GetClipCount())
    while v.GetClipCount() > 0:
        before = v.GetClipCount()
        c = v.GetClip(0)
        # the clip sits at ~23.3-35.9 s; any time inside it removes it
        v.RemoveVisemesClip(T(30.0))
        if v.GetClipCount() == before:
            break
    kv = v.GetVisemeKeys()
    log.append("viseme clips after %d keys %d" % (v.GetClipCount(), len(kv)))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p5_setup.txt"), "w", encoding="utf-8").write("\n".join(log))
