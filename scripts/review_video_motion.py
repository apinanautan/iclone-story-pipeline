# Read-only quality-control scan for video frame discontinuities.
# py -3 scripts/review_video_motion.py "<mp4>" "<report_dir>"
import cv2,json,sys
from pathlib import Path
from statistics import median
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
cap=cv2.VideoCapture(str(src));fps=cap.get(cv2.CAP_PROP_FPS)
if fps<=0:raise RuntimeError("Cannot read video")
samples=[];prev=None;frame=0
while True:
 ok,img=cap.read()
 if not ok:break
 small=cv2.cvtColor(cv2.resize(img,(256,144)),cv2.COLOR_BGR2GRAY)
 if prev is not None:
  d=cv2.absdiff(prev,small)
  samples.append((frame/fps,float(d.mean()),float((d>25).mean())))
 prev=small;frame+=1
cap.release();flag=[]
for i,(t,d,area) in enumerate(samples):
 lo=max(i-18,0);hi=min(i+19,len(samples))
 med=median(x[1] for x in samples[lo:hi])
 if d>max(18.0,med*4) and area>0.14:
  flag.append({"time":round(t,3),"frame_diff":round(d,2),"changed_fraction":round(area,3),"possible_camera_cut":True})
report={"input":str(src),"fps":fps,"frames":frame,"seconds":frame/fps,"candidate_discontinuities":flag,"note":"Visual change is not proof of animation glitch. Inspect continuously and compare actor/camera keys."}
(out/'motion_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
