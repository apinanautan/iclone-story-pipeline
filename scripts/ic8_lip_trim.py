# Trim viseme keys to each speaker's window after the FULL N.mp3 was imported via
# Animation > Create Script > Audio File (GUI; RAudio.LoadAudioToObject makes no visemes).
import RLPy, os
import json as _j
WIN = _j.loads(os.environ.get('LIPWIN', 'null')) or {'p2_old': (1.4, 4.7), 'p2_im': (13.4, 24.6), 'p2_woman': (31.7, 40.5), 'p2_young': (40.8, 50.6)}
OUT = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs', 'lip_trim.txt')
out = []
for a in RLPy.RScene.GetAvatars():
    n = a.GetName(); v = a.GetVisemeComponent()
    kv = v.GetVisemeKeys(); ks = [kv[i] for i in range(len(kv))]; rm = 0
    if n in WIN:
        w = WIN[n]   # [s, e] or [[s, e], ...]; [] = mouth closed all part
        w = [w] if w and not isinstance(w[0], (list, tuple)) else w
        for k in ks:
            t = k.GetTime().ToFloat() / 6000.0
            if not any(s - 0.1 <= t <= e + 0.15 for s, e in w):
                v.RemoveVisemesKey(k); rm += 1
    kv = v.GetVisemeKeys(); left = [kv[i].GetTime().ToFloat() / 6000.0 for i in range(len(kv))]
    out.append('%s clips %d keys %d removed %d left %d range %s' % (n, v.GetClipCount(), len(ks), rm, len(left),
               '%.2f-%.2f' % (min(left), max(left)) if left else '-'))
open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
