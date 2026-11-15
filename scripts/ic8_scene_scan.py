"""Generic, read-only: measure the open scene once -> ic8_jobs/scene_scan.json (props/buildings with bounding boxes,
avatars, cameras). Then: python scripts/ic8_story.py <story> scan <scene name>  copies it into the story file.
Never saves, never moves anything."""
import RLPy, os, json, traceback
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
out = {"objects": [], "errors": []}


def row(kind, o):
    try:
        t = o.WorldTransform().T()
        mx, c, mn = RLPy.RVector3(), RLPy.RVector3(), RLPy.RVector3()
        o.GetBounds(mx, c, mn)
        out["objects"].append({"kind": kind, "name": o.GetName(), "pos": [round(t.x), round(t.y), round(t.z)],
                               "min": [round(mn.x), round(mn.y), round(mn.z)], "max": [round(mx.x), round(mx.y), round(mx.z)]})
    except Exception as e:
        out["errors"].append("%s %s: %s" % (kind, o.GetName(), e))


try:
    for kind, lst in (("prop", RLPy.RScene.GetProps()), ("building", RLPy.RScene.GetBuildings()),
                      ("avatar", RLPy.RScene.GetAvatars()), ("camera", RLPy.RScene.GetCameras())):
        for o in lst:
            row(kind, o)
except Exception:
    out["errors"].append(traceback.format_exc())
json.dump(out, open(os.path.join(J, "scene_scan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
