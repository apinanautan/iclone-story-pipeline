# Part 9: blue bucket + cloth (user's Props(94).iProp) next to every worker. Re-runnable (removes old bucket_* first).
import os, traceback
import RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
P94 = r"G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Prop ของใช้ต่างๆ\เสื้อผ้า-ทรงผม\Reallusion Custom\Props\Props(94).iProp"
SPOTS = {"bucket_1": (655, -445), "bucket_2": (1115, -420), "bucket_3": (915, -205), "bucket_4": (1065, -235), "bucket_5": (640, -215)}
Z = 0.0
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
log = []
try:
    for o in list(RLPy.RScene.GetProps()):
        if o.GetName().startswith("bucket_"):
            RLPy.RScene.RemoveObject(o)
    for name, (x, y) in SPOTS.items():
        before = set(o.GetID() for o in RLPy.RScene.GetProps())
        RLPy.RScene.ClearSelectObjects()
        RLPy.RFileIO.LoadFile(P94)
        new = [o for o in RLPy.RScene.GetProps() if o.GetID() not in before]
        for o in new:
            o.SetName(name)
            c = o.GetControl("Transform"); t = RLPy.RTransform(); c.GetValue(T(0), t)
            t.T().x, t.T().y, t.T().z = x, y, Z
            c.SetValue(T(0), t)
        log.append("%s %d obj at (%d,%d)" % (name, len(new), x, y))
except Exception:
    log.append(traceback.format_exc())
open(os.path.join(J, "p9_buckets.txt"), "w", encoding="utf-8").write("\n".join(log))
