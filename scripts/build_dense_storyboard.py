# -*- coding: utf-8 -*-
"""Internal operator-only chronological storyboard. 30 consecutive frames per sheet."""
from PIL import Image,ImageDraw
from pathlib import Path
import argparse,math,json
p=argparse.ArgumentParser()
p.add_argument("input",type=Path);p.add_argument("--output",type=Path)
p.add_argument("--start",type=int);p.add_argument("--end",type=int)
p.add_argument("--columns",type=int,default=5)
a=p.parse_args()
frames=sorted(a.input.glob("frame_*.png"))
if a.start is not None:frames=[x for x in frames if int(x.stem.split("_")[1])>=a.start]
if a.end is not None:frames=[x for x in frames if int(x.stem.split("_")[1])<a.end]
if not frames:raise SystemExit("No frames")
output=a.output or a.input/"storyboard"
output.mkdir(parents=True,exist_ok=True)
for chunk_start in range(0,len(frames),30):
    chunk=frames[chunk_start:chunk_start+30]
    cols=min(a.columns,len(chunk));rows=math.ceil(len(chunk)/cols)
    cw,ch=320,208
    panel=Image.new("RGB",(cw*cols,ch*rows),(22,22,22))
    d=ImageDraw.Draw(panel)
    for i,file in enumerate(chunk):
        frame=int(file.stem.split("_")[1])
        im=Image.open(file).convert("RGB")
        im.thumbnail((cw,175))
        x=(i%cols)*cw+(cw-im.width)//2
        y=(i//cols)*ch+29
        panel.paste(im,(x,y))
        d.text(((i%cols)*cw+7,(i//cols)*ch+7),f"F{frame} / {frame/30:.3f}s",fill=(245,236,195))
    path=output/f"sheet_{int(chunk[0].stem.split('_')[1]):05d}_{int(chunk[-1].stem.split('_')[1]):05d}.jpg"
    panel.save(path,format="JPEG",quality=87)
    print("SHEET",path,"frames",len(chunk))
