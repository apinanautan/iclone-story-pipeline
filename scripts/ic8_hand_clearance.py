import os

import RLPy,json,math,traceback
from PySide2 import QtWidgets
from pathlib import Path
J=Path(os.environ["LOCALAPPDATA"])/"Tidmunz Studio"/"snapgen_data"/"ic8_jobs"
cfg=json.loads((J/"hand_clearance_job.json").read_text(encoding="utf8"))
out=Path(cfg["output"])
actors={a.GetName():a for a in RLPy.RScene.GetAvatars()}
sty=actors[cfg["actor"]];cus=actors[cfg["other"]]
def selected(a,mode):
 result={}
 for b in a.GetSkeletonComponent().GetSkinBones():
  k=b.GetName()
  if mode=="head":
   if not any(x in k.lower() for x in ("head","neck")):continue
  else:
   if not any(x in k.lower() for x in ("hand","finger","thumb","index","mid","ring","pinky","forearm")):continue
  result[k]=b
 return result
hands=selected(sty,"hand");head=selected(cus,"head")
assert any("hand" in k.lower() for k in hands) and any(k.endswith("_Head") for k in head),(list(hands),list(head))
def pos(b):
 v=b.WorldTransform().T();return [v.x,v.y,v.z]
old=RLPy.RGlobal.GetTime();samples=[]
try:
 RLPy.RGlobal.Stop()
 for a,z in cfg["windows"]:
  for i in range(math.floor(a*cfg["fps"]),math.ceil(z*cfg["fps"])+1):
   t=i/cfg["fps"]
   RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(round(t*6000)));QtWidgets.QApplication.processEvents()
   sty.Update();cus.Update()
   hp={k:pos(b) for k,b in head.items()};sp={k:pos(b) for k,b in hands.items()}
   p=next(v for k,v in hp.items() if k.endswith("_Head"))
   vals={k:math.dist(v,p) for k,v in sp.items()}
   k=min(vals,key=vals.get)
   samples.append({"frame":i,"t":t,"head":hp,"hand":sp,"nearest_bone":k,"nearest_cm":vals[k]})
finally:
 RLPy.RGlobal.SetTime(old);QtWidgets.QApplication.processEvents()
out.write_text(json.dumps({"fps":cfg["fps"],"samples":samples,"hand_bones":list(hands),"head_bones":list(head),"min":min(samples,key=lambda x:x["nearest_cm"])},ensure_ascii=False),encoding="utf8")
