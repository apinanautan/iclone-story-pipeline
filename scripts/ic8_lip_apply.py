# Replace an avatar's viseme keys with keys from tools/lip_from_audio.py (ic8_jobs\lipkeys_<avatar>.json).
# Needs an existing viseme clip on the avatar (made by Animation > Create Script > Audio File). Set AV below.
import json, os
import RLPy
AVS = ["ชาวบ้านหญิง", "นายสมหวัง"]  # avatars that SPEAK in this part (edit per part); narration-only avatars get no lip keys
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
out = []
for AV in AVS:
    try:
        d = json.load(open(os.path.join(J, "lipkeys_%s.json" % AV), encoding="utf-8"))
        a = [x for x in RLPy.RScene.GetAvatars() if x.GetName() == AV][0]
        v = a.GetVisemeComponent()
        kv = v.GetVisemeKeys(); old = [kv[i] for i in range(len(kv))]
        for k in old:
            v.RemoveVisemesKey(k)
        n = 0; err = ""
        for t, vid, w in d["keys"]:
            k = RLPy.RVisemeKey()
            k.SetTime(RLPy.RTime.FromValue(int(t * 6000)))
            k.SetID(getattr(RLPy, "EVisemeID_" + vid))
            k.SetWeight(w * 100.0 if vid != "NONE" else 100.0)  # SetWeight takes percent (0-100)
            try:
                v.AddVisemeKey(k); n += 1
            except Exception as e:
                err = repr(e)
        kv = v.GetVisemeKeys()
        out.append("%s removed %d added %d now %d %s" % (AV, len(old), n, len(kv), err))
    except Exception as e:
        out.append("%s ERROR %r" % (AV, e))
open(os.path.join(J, "lip_apply.txt"), "w", encoding="utf-8").write("\n".join(out))
