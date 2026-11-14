# Part 9 (user 2026-11-07): helpers must really WORK, not kneel/stand still. Replace the kneel pose of p3_x1..x4 (and give Seeka Oi a chore motion)
# with Home Life cleaning/chore mocap, chained to cover the whole timeline with crossfades. Face clips / smile / nods stay.
import os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
HL = r"G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Home_life_Clean_\Studio Mocap-Home Life"
L = 31.1
SPEED = 0.85
WORK = {  # avatar: (motion file, start offset s)
    "p3_x1": (HL + r"\Kitchen\Kitchen_CleanTable_M.rlMotion", 0.0),
    "p3_x2": (HL + r"\Yard\Yard_Weeding_M.rlMotion", 0.0),
    "p3_x3": (HL + r"\Living Room\LivingRoom_DoChores&Squat_F.rlMotion", 0.0),
    "p3_x4": (HL + r"\Kitchen\Kitchen_CleanTable_M.rlMotion", 0.0),
    "p3_oi": (HL + r"\Living Room\LivingRoom_DoChores_F.rlMotion", 0.0),
}
ONLY = None  # one avatar per job if iClone is slow
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    av = {a.GetName(): a for a in RLPy.RScene.GetAvatars()}
    for name, (path, off) in WORK.items():
        if ONLY and name != ONLY:
            continue
        a = av[name]; sk = a.GetSkeletonComponent()
        p0 = a.WorldTransform().T(); x0, y0 = p0.x, p0.y
        while sk.GetClipCount() > 0:
            n = sk.GetClipCount()
            try:
                sk.DeleteClip(sk.GetClip(0))
            except Exception:
                sk.DeleteClip(0)
            if sk.GetClipCount() == n:
                break
        cur = 0.0; k = 0
        while cur < L - 0.05 and k < 6:
            RLPy.RFileIO.LoadMotion(path, T(cur), a)
            cl = sk.GetClip(sk.GetClipCount() - 1)
            cl.SetSpeed(1.0); raw = cl.GetClipLength().ToFloat() / 6000.0
            cl.SetSpeed(SPEED)
            d = raw / SPEED
            if k > 0:
                cl.SetTransitionRange(T(1.5))
            if cur + d > L:
                cl.SetLength(T((L - cur) * SPEED))
            log.append("%s clip %d start %.1f len %.1f" % (name, k, cur, d))
            cur += d - (1.5 if k >= 0 else 0); k += 1
        RLPy.RGlobal.SetTime(T(1))
        pts = []
        for t in (1, 8, 16, 24, 30):
            RLPy.RGlobal.SetTime(T(t))
            h = next(b for b in sk.GetSkinBones() if b.GetName().endswith("Head")).WorldTransform().T()
            pts.append("t%d head(%.0f,%.0f,%.0f)" % (t, h.x, h.y, h.z))
        log.append("%s origin(%.0f,%.0f) " % (name, x0, y0) + " ".join(pts))
    RLPy.RGlobal.SetTime(T(0))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p9_work_log.txt"), "w", encoding="utf-8").write("\n".join(log))
