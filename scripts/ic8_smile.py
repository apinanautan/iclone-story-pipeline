# Gentle smile for avatars over the whole timeline (user 2026-11-07: Seeka Oi must look happy, not grumpy).
# Face expression keys layered over the body/face clip. Edit AVS (name -> strength 0-1) and L.
# Brow drop/compress keyed to 0 so a Mograph "listen" clip can't leave a frown under the smile.
import os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
AVS, L = {"สุดา": 0.75, "นางจีไล": 0.6, "นายสมหวัง": 0.45}, 67.3
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
NAMES = ["Mouth_Corner_Up_L", "Mouth_Corner_Up_R", "Mouth_Corner_Pull_L", "Mouth_Corner_Pull_R",
         "Eye_Cheek_Raise_L", "Eye_Cheek_Raise_R", "Brow_Raise_Outer_L", "Brow_Raise_Outer_R",
         "Mouth_Corner_Down_L", "Mouth_Corner_Down_R", "Brow_Drop_L", "Brow_Drop_R",
         "Brow_Compress_L", "Brow_Compress_R"]
log = []
for AV, W in AVS.items():
    try:
        WTS = [0.8 * W, 0.8 * W, 0.55 * W, 0.55 * W, 0.6 * W, 0.6 * W, 0.2 * W, 0.2 * W] + [0.0] * 6
        a = next(x for x in RLPy.RScene.GetAvatars() if x.GetName() == AV)
        fc = a.GetFaceComponent()
        fc.BeginKeyEditing()
        fc.AddExpressionKeys(T(0), NAMES, WTS, T(0.1))
        t = 4.0
        while t < L - 2:
            fc.AddExpressionKeys(T(t), NAMES, [w * (0.85 + 0.15 * ((int(t) % 3) / 2.0)) for w in WTS], T(2.0))
            t += 4.0
        fc.AddExpressionKeys(T(L), NAMES, WTS, T(1.0))
        fc.EndKeyEditing()
        log.append("%s smile keys ok (W=%.2f, L=%.1f)" % (AV, W, L))
    except Exception:
        log.append(AV + " " + traceback.format_exc())
open(os.path.join(J, "smile_log.txt"), "w", encoding="utf-8").write("\n".join(log))
