"""Read-only: every avatar's body clips (start, length, speed) + clip API names -> ic8_jobs/speed_probe.txt.
Used to fix judder (speed < 0.65) in an existing project (user 2026-11-19)."""
import RLPy, os
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
out = ["fps %s  end %.2f" % (RLPy.RGlobal.GetFps(), RLPy.RGlobal.GetEndTime().ToFloat() / 6000)]
api = None
for a in RLPy.RScene.GetAvatars():
    sk = a.GetSkeletonComponent()
    for i in range(sk.GetClipCount()):
        c = sk.GetClip(i); api = api or c
        out.append("%s clip%d start %.2f len %.2f speed %.3f" % (a.GetName(), i, c.GetClipStartTime().ToFloat() / 6000 if hasattr(c, "GetClipStartTime") else -1,
                   c.GetClipLength().ToFloat() / 6000, c.GetSpeed()))
if api: out.append("API " + " ".join(m for m in dir(api) if not m.startswith("_")))
open(os.path.join(J, "speed_probe.txt"), "w", encoding="utf-8").write("\n".join(out))
