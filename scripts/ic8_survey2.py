import os, RLPy
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
out = []
def row(kind, o):
    try:
        t = o.WorldTransform().T()
        mx, c, mn = RLPy.RVector3(), RLPy.RVector3(), RLPy.RVector3()
        o.GetBounds(mx, c, mn)
        out.append("%s\t%s\tpos %.0f %.0f %.0f\tmin %.0f %.0f %.0f\tmax %.0f %.0f %.0f" % (
            kind, o.GetName(), t.x, t.y, t.z, mn.x, mn.y, mn.z, mx.x, mx.y, mx.z))
    except Exception as e:
        out.append("%s\t%s\t! %s" % (kind, o.GetName(), e))
for kind, lst in (("prop", RLPy.RScene.GetProps()), ("avatar", RLPy.RScene.GetAvatars()),
                  ("camera", RLPy.RScene.GetCameras())):
    for o in lst:
        row(kind, o)
open(os.path.join(J, "survey.txt"), "w", encoding="utf-8").write("\n".join(out))
cam = RLPy.RScene.GetCurrentCamera()
RLPy.RScene.ClearSelectObjects()
cam.SetCameraLocation(RLPy.ECameraLocationType_Top)
cam.SetCameraLocation(RLPy.ECameraLocationType_Focus)
RLPy.RGlobal.RenderImage(os.path.join(J, "look_top.png"))
