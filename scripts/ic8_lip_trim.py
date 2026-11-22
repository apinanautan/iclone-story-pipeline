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
        # 2026-11-22 user: the mouth must CLOSE when a line ends. AccuLips' last key is often an open shape
        # (Pucker / Upper Dental) with nothing after it, so the mouth hung open until the next line.
        # Add a 'None' (ID 0, closed) key just after the last key of every window.
        kv = v.GetVisemeKeys(); ks = [kv[i] for i in range(len(kv))]; shut = 0
        for s, e in w:
            inw = [k for k in ks if s - 0.1 <= k.GetTime().ToFloat() / 6000.0 <= e + 0.15]
            if not inw: continue
            last = max(inw, key=lambda k: k.GetTime().ToFloat())
            if last.GetID() == 0: continue
            c = last.Clone(); c.SetID(0); c.SetWeight(1.0)
            c.SetTime(RLPy.RTime.FromValue(int(round((max(last.GetTime().ToFloat() / 6000.0, e) + 0.12) * 6000))))
            v.AddVisemeKey(c); shut += 1
        out.append('%s closed mouth at %d line end(s)' % (n, shut))
    kv = v.GetVisemeKeys(); left = [kv[i].GetTime().ToFloat() / 6000.0 for i in range(len(kv))]
    out.append('%s clips %d keys %d removed %d left %d range %s' % (n, v.GetClipCount(), len(ks), rm, len(left),
               '%.2f-%.2f' % (min(left), max(left)) if left else '-'))
open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
