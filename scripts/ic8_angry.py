import os, traceback, RLPy
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
CAND = ['Brow_Down_L','Brow_Down_R','Eye_Squint_Inner_L','Eye_Squint_Inner_R','Eye_Lid_Press_L','Eye_Lid_Press_R','Nose_Wrinkle_L','Nose_Wrinkle_R','Mouth_Corner_Depress_L','Mouth_Corner_Depress_R','Mouth_Lips_Thin_UL','Mouth_Lips_Thin_UR','Mouth_Corner_Down_L','Mouth_Corner_Down_R','Jaw_Clench_L','Jaw_Clench_R']
BASE = [0.9,0.9,0.5,0.5,0.4,0.4,0.25,0.25,0.6,0.6,0.4,0.4,0.4,0.4,0.5,0.5]
try:
    a = next(x for x in RLPy.RScene.GetAvatars() if x.GetName() == 'สุนีย์')
    fc = a.GetFaceComponent()
    have = set()
    for g in ('Brows', 'MouthBase', 'MouthMove', 'EyeLid', 'Nose', 'Jaw'):
        try: have |= set(fc.GetExpressionNames(g))
        except Exception: pass
    names = [n for n in CAND if n in have]
    base = [w for n, w in zip(CAND, BASE) if n in have]
    log.append('names used: %s | missing: %s' % (names, [n for n in CAND if n not in have]))
    def wts(k): return [w * k for w in base]
    fc.BeginKeyEditing()
    fc.AddExpressionKeys(T(0), names, wts(0.0), T(0.1))
    fc.AddExpressionKeys(T(3), names, wts(0.55), T(3))      # stern from the start
    fc.AddExpressionKeys(T(22), names, wts(0.7), T(4))
    fc.AddExpressionKeys(T(26), names, wts(1.0), T(2))      # caught him: angry
    fc.AddExpressionKeys(T(36), names, wts(1.15), T(3))     # shouting at the rental
    fc.AddExpressionKeys(T(43.8), names, wts(1.0), T(1))
    fc.EndKeyEditing()
    log.append('angry keys ok')
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, 'p1_angry_log.txt'), 'w', encoding='utf-8').write('\n'.join(log))

