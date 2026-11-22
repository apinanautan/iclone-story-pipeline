"""Stage a 67.2 second Krong Katanyu trial using the generic pose/camera jobs."""
import json
import os
import runpy
import RLPy

ROOT = r"C:\Users\Apinan\Documents\iClone Story Pipeline"
JOBS = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")

with open(os.path.join(ROOT, "parts", "กรงกตัญญู_1.json"), encoding="utf-8") as source:
    spec = json.load(source)

end = spec["preview_end_seconds"]
end_time = RLPy.RTime.FromValue(round(end * 6000))
RLPy.RGlobal.SetProjectLength(end_time)
RLPy.RGlobal.SetEndTime(end_time)
RLPy.RGlobal.SetPreviewEndTime(end_time)
avatars = dict(spec["cast"])
for name in spec["hide"]:
    avatars[name] = {"visible": [[0, 0]]}

steps = [("cams.json", {"end": end, "edges": False, "shots": spec["shots"]}, "ic8_cams.py")]
cast = {actor.GetName(): actor for actor in RLPy.RScene.GetAvatars()}
if not all(cast[name].GetSkeletonComponent().GetClipCount() for name in spec["cast"]):
    steps.insert(0, ("pose_place.json", {"end": end, "avatars": avatars}, "ic8_pose_place.py"))
for config, data, script in steps:
    with open(os.path.join(JOBS, config), "w", encoding="utf-8") as output:
        json.dump(data, output, ensure_ascii=False)
    runpy.run_path(os.path.join(ROOT, "scripts", script))
