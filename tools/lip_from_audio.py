# Make mouth keys from the audio loudness (AccuLips is ~0.5 s off on Thai). Output: ic8_jobs\lipkeys_<avatar>.json
# Usage: python tools/lip_from_audio.py <N> <avatar> <start> <end>
# Then run scripts/ic8_lip_apply.py (watcher) which replaces that avatar's viseme keys with these.
import json, os, random, subprocess, sys
import numpy as np
n, av, s0, s1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
FF = r"C:\Users\Apinan\AppData\Local\Tidmunz Studio\snapgen_data\tools\ffmpeg\ffmpeg.exe"
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
raw = subprocess.run([FF, "-v", "error", "-i", (n if n.lower().endswith((".wav", ".mp3")) else rf"C:\Users\Apinan\Downloads\audio_output\{n}.mp3"), "-af", "highpass=f=200,lowpass=f=3500",
                      "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(float)
STEP = 0.06
keys = []
seg = a[int(s0 * 16000):int(s1 * 16000)]
fr = [np.sqrt(np.mean(seg[int(i * STEP * 16000):int((i + 1) * STEP * 16000)] ** 2)) for i in range(int((s1 - s0) / STEP))]
fr = np.array(fr); peak = np.percentile(fr, 95); floor = np.percentile(fr, 30)
rnd = random.Random(1)
VIS = ["AH", "AE", "EE", "IH", "OH", "W_OO", "T_L_D_N", "S_Z", "K_G_H_NG", "B_M_P"]
prev = None
for i, r in enumerate(fr):
    t = s0 + i * STEP
    w = float(np.clip((r - floor) / (peak - floor + 1e-9), 0, 1))
    if w < 0.12:
        vid, w = "NONE", 0.0
    else:
        vid = rnd.choice([v for v in VIS if v != prev]); w = 0.35 + 0.6 * w
    if vid != prev or vid != "NONE":
        keys.append([round(t, 3), vid, round(w, 2)])
    prev = vid
keys.append([round(s1, 3), "NONE", 0.0])
json.dump({"avatar": av, "start": s0, "end": s1, "keys": keys}, open(os.path.join(J, f"lipkeys_{av}.json"), "w"))
print(av, len(keys), "keys")
