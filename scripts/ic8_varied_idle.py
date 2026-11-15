import os, traceback, RLPy
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
M = r'G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\โมชั่น'
FACE = r'G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Digital Soul 100+\1.Watch\Look front.iTalk'
L = 67.3
# name: (motion list, speed)  -- different motion + speed per character so nobody moves in sync
CFG = {
 'สุดา': ([M + r'\04_CC MixMove_Female\Stand00.iMotion'], 0.55),
 'วารี': ([M + r'\04_CC MixMove_Female\Stand00.iMotion'], 0.75),
 'นางจีไล': ([M + r'\04_CC MixMove_Female\Stand00.iMotion'], 0.65),
 'นายสมหวัง': ([M + r'\03_CC MixMove_Male\Stand00.iMotion'], 1.0),
 'ชาวบ้าน (ตัวแทนคนแรก)': ([M + r'\03_CC MixMove_Male\Stand00.iMotion'], 0.7),
}
ONLY = None
log = []
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
try:
    for av in RLPy.RScene.GetAvatars():
        nm = av.GetName()
        if nm not in CFG: continue
        mots, spd = CFG[nm]
        sk = av.GetSkeletonComponent()
        RLPy.RGlobal.RemoveAllAnimations(av)
        cur, i = 0.0, 0
        while cur < L - 0.05:
            RLPy.RFileIO.LoadMotion(mots[i % len(mots)], T(cur), av)
            cl = sk.GetClip(sk.GetClipCount() - 1)
            cl.SetSpeed(spd)
            d = cl.GetClipLength().ToFloat() / 6000
            if d <= 0.5: log.append('! short clip'); break
            if cur + d > L: cl.SetLength(T((L - cur) * spd)); d = L - cur
            log.append('%s %.1f-%.1f %s' % (nm, cur, cur + d, os.path.basename(mots[i % len(mots)])))
            cur += d; i += 1
        for k in range(1, sk.GetClipCount()):
            sk.GetClip(k).SetTransitionRange(T(min(2.5, 0.4 * d)))
        fc = av.GetFaceComponent()
        RLPy.RScene.ClearSelectObjects(); RLPy.RScene.SelectObject(av)
        cur = 0.0
        while cur < L - 0.05:
            RLPy.RGlobal.SetTime(T(cur))
            RLPy.RFileIO.LoadFile(FACE)
            cl = fc.GetClip(fc.GetClipCount() - 1)
            cl.SetSpeed(1.0)
            raw = cl.GetClipLength().ToFloat() / 6000
            sp = max(0.5, raw / L); cl.SetSpeed(sp)
            cur += raw / sp
        for k in range(1, fc.GetClipCount()):
            fc.GetClip(k).SetTransitionRange(T(8.58))
        fc.SetAutoBlinkName('Normal')
        RLPy.RGlobal.SetTime(T(0))
        log.append('%s body %d face %d' % (nm, sk.GetClipCount(), fc.GetClipCount()))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, 't2i_motion.txt'), 'w', encoding='utf-8').write('\n'.join(log))

