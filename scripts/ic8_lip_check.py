"""Generic: count viseme keys per avatar and the time span they cover. Log: ic8_jobs/lip_check.txt"""
import RLPy, os
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
out = []
for a in RLPy.RScene.GetAvatars():
    kv = a.GetVisemeComponent().GetVisemeKeys()
    ts = [kv[i].GetTime().ToFloat() / 6000.0 for i in range(len(kv))]
    out.append("%s visemes %d span %s" % (a.GetName(), len(ts), ("%.1f-%.1f" % (min(ts), max(ts))) if ts else "-"))
open(os.path.join(J, "lip_check.txt"), "w", encoding="utf-8").write("\n".join(out))
