# -*- coding: utf-8 -*-
"""Frame-exhaustive operator QA; heuristics assist human visual review, not replace it."""
from pathlib import Path
from PIL import Image
import argparse,json
import numpy as np

a=argparse.ArgumentParser()
a.add_argument("folder",type=Path)
a.add_argument("--start",type=int,required=True)
a.add_argument("--end",type=int,required=True)
args=a.parse_args()
folder=args.folder
rows={}
for p in folder.glob("batch_*.json"):
    data=json.loads(p.read_text(encoding="utf-8"))
    for row in data["rows"]:
        f=int(row["frame"])
        if f in rows:raise RuntimeError(f"Duplicate frame {f} from two batches")
        rows[f]=row
missing=[i for i in range(args.start,args.end) if i not in rows]
if missing:raise SystemExit(f"FAIL: missing {len(missing)} frames, first={missing[:15]}")
if len([i for i in rows if args.start<=i<args.end])!=args.end-args.start:raise RuntimeError("bad count")
print("FRAME_COUNT_PASS",args.end-args.start)
prev=None;prev_cam=None;diffs=[];suspect=[];camera_runs=[];run_start=args.start;streak=0
for i in range(args.start,args.end):
    row=rows[i];file=Path(row["image"])
    if not file.is_file():raise RuntimeError(f"Missing image: {file}")
    im=Image.open(file).convert("RGB").resize((96,54),Image.Resampling.BILINEAR)
    pix=np.asarray(im,dtype=np.int16)
    luma=float((0.2126*pix[:,:,0]+0.7152*pix[:,:,1]+0.0722*pix[:,:,2]).mean())
    if luma<7:suspect.append({"frame":i,"type":"VERY_DARK","luma":round(luma,2)})
    cam=row["camera"]
    if prev is not None:
        diff=float(np.abs(pix-prev).mean())
        if prev_cam==cam:
            diffs.append(diff)
            if diff>25:suspect.append({"frame":i,"type":"SUDDEN_WITHIN_SAME_CAMERA","mean_abs_diff":round(diff,2),"camera":cam})
            if diff<0.07:streak+=1
            else:streak=0
            if streak==15:suspect.append({"frame":i,"type":"POSSIBLE_FROZEN_15_CONSECUTIVE_FRAMES","camera":cam})
        else:
            camera_runs.append({"start_frame":run_start,"end_frame_exclusive":i,"camera":prev_cam})
            run_start=i;streak=0
    prev=pix;prev_cam=cam
camera_runs.append({"start_frame":run_start,"end_frame_exclusive":args.end,"camera":prev_cam})
report={
    "frame_range":[args.start,args.end],"captured_count":args.end-args.start,
    "camera_runs":camera_runs,"same_camera_mean_abs_diff_avg":round(float(np.mean(diffs)),3) if diffs else None,
    "same_camera_mean_abs_diff_max":round(float(max(diffs)),3) if diffs else None,
    "heuristic_flags":suspect,
    "limitations":"This checks every frame and possible freeze/jumps; visual staging, mouth, eyelines, contact still require looking at ordered storyboards + playback."}
out=folder/f"full_frame_anomalies_{args.start}_{args.end}.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("CAMERA_RUNS",json.dumps(camera_runs,ensure_ascii=False))
print("HEURISTIC_FLAGS",json.dumps(suspect[:40],ensure_ascii=False))
print("SAVED",out)
