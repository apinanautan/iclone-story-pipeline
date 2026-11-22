"""Load the opening couple into the verified Krong Katanyu trial project."""
import json
import os

import RLPy

ROOT = r"E:\ไฟล์งาน\ไฟล์ Save\นิทาน\กรงกตัญญู\GPT_ทดลอง"
JOBS = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
RLPy.RGlobal.Stop()
RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(0))
for name in ("นายสมจิต", "นางอุไร"):
    avatars = list(RLPy.RScene.GetAvatars())
    if any(actor.GetName() == name for actor in avatars):
        continue
    existing_ids = {actor.GetID() for actor in avatars}
    RLPy.RScene.ClearSelectObjects()
    RLPy.RFileIO.LoadFile(os.path.join(ROOT, name + " วัย 40.iAvatar"))
    added = [actor for actor in RLPy.RScene.GetAvatars() if actor.GetID() not in existing_ids]
    if len(added) != 1:
        raise RuntimeError("Expected one new avatar: " + name)
    added[0].SetName(name)

RLPy.RScene.ClearSelectObjects()
with open(os.path.join(JOBS, "krong_trial_cast.json"), "w", encoding="utf-8") as report:
    json.dump([actor.GetName() for actor in RLPy.RScene.GetAvatars()], report, ensure_ascii=False)
