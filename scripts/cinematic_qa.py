"""Scene evidence and editorial gates. Observations are AI work, not inferred from file existence."""
import json,hashlib,re,time,shutil,subprocess,sys
from pathlib import Path
from PIL import Image
def read(p):
    try:return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except (OSError,ValueError):return {}
def write(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(".tmp");t.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");t.replace(p)
def hashobj(d):return hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def digest(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def folder(root,story,part):
    if not story or story in (".","..") or any(c in story for c in '/\\:*?"<>|') or not re.fullmatch(r"\d+(?:\.\d+)?",str(part)):raise ValueError("invalid story/part")
    return Path(root)/"progress"/"cinematic_qa"/story/str(part)
def images(q,pattern):
    d={}
    for p in sorted(q.glob(pattern)):
        with Image.open(p) as im:im.verify()
        d[p.name]=digest(p)
    return d
def text(x):return isinstance(x,str) and len(x.strip())>=12
def work(say,msg):say("AI WORK: "+msg);raise SystemExit(3)
def shots(S):return hashobj(S["shots"])
def plan_errors(rows):
    e=[]
    for i,s in enumerate(rows):
        if s.get("size") not in ("EST","MS","MCU","CU","OTS","TWO","INSERT") or not text(s.get("purpose")) or not text(s.get("scene_evidence")):e.append(f"S{i+1}: size, purpose, scene_evidence required")
        if i and not text(s.get("cut_reason")):e.append(f"S{i+1}: why cut instead of hold?")
        if s["t"][1]-s["t"][0]<5 and not text(s.get("short_reason")):e.append(f"S{i+1}: justify short shot")
        if i>=2 and all(x["t"][1]-x["t"][0]<5 for x in rows[i-2:i+1]):e.append(f"S{i+1}: three short cuts; merge or hold")
    if len(rows)>=4 and sum(s.get("size")=="CU" for s in rows)/len(rows)>.6:e.append("face-only CU dominates")
    for i,(a,b) in enumerate(zip(rows,rows[1:]),2):
        if a.get("subject") and a.get("subject")==b.get("subject") and a.get("size")==b.get("size"):e.append(f"S{i}: same subject and scale; merge or redesign")
    return e
def scene_review(S,root,J,job,fail,say):
    q=folder(root,S["story"],S["part"]);q.mkdir(parents=True,exist_ok=True)
    sd=read(root/"progress"/f'{S["story"]}_{S["part"]}.json').get("steps_done",{})
    stage=hashobj([{k:S.get(k) for k in ("project","cast","hide","props","lines","scene")},{k:sd.get(k) for k in ("open","cast","pose","lip")}])
    m=read(q/"scene_manifest.json")
    if m.get("stage")!=stage or not m.get("images") or m["images"]!=images(q,"scene_*.png"):
        for p in q.glob("scene_*.png"):p.unlink()
        (q/"scene_capture.json").unlink(missing_ok=True)
        write(J/"scene_review_request.json",{"directory":str(q),"cast":list(S["cast"]),"shots":S["shots"],"room":S.get("_scene",{}).get("room") or S.get("_scene",{}).get("area")})
        prefix=(root/"scripts"/"ic8_cams.py").read_text(encoding="utf-8").split('\ntry:\n    p = json.load',1)[0]
        job(prefix+"\n"+(root/"scripts"/"ic8_scene_review.py").read_text(encoding="utf-8"),"zz_scene_review")
        result=read(q/"scene_capture.json");im=images(q,"scene_*.png")
        if result.get("ok") is not True or len(im)<4:fail("scene survey incomplete: "+str(result.get("error")))
        m={"stage":stage,"images":im,"capture":result};write(q/"scene_manifest.json",m)
        from PIL import ImageDraw
        cols=4;w,h=480,270;names=sorted(im);sheet=Image.new("RGB",(cols*w,((len(names)+cols-1)//cols)*h),"#202020")
        for i,n in enumerate(names):
            with Image.open(q/n) as src:tile=src.convert("RGB").resize((w,h),Image.LANCZOS)
            d=ImageDraw.Draw(tile);d.rectangle((0,0,w,18),fill="black");d.text((6,2),n,fill="white")
            sheet.paste(tile,((i%cols)*w,(i//cols)*h))
        sheet.save(q/"scene_overview.jpg",quality=85)
        bridge=root/"tools"/"chrome_preview_bridge"/"queue_preview.py"
        if bridge.is_file():
            proc=subprocess.run([sys.executable,str(bridge),str(q/"scene_overview.jpg"),S["story"],str(S["part"]),"scene_review"],capture_output=True,text=True,encoding="utf-8",errors="replace")
            say("Scene preview bridge: "+proc.stdout.strip())
    d=read(q/"scene_notes.json")
    if d.get("manifest")!=hashobj(m) or set(d.get("seen_images",[]))!=set(m["images"]) or not all(text(d.get(k)) for k in ("blocking","good_angles","blocked_angles","background","action_props")):
        work(say,f"Inspect all images in {q}; write scene_notes.json manifest={hashobj(m)}, seen_images, blocking, good_angles, blocked_angles, background, action_props. If prop missing use Blender skill, update spec and repair cast before resurvey.")
    say("OK actual scene review")
def check_replan(S,root,J,fail,say):
    q=folder(root,S["story"],S["part"]);m=read(q/"scene_manifest.json")
    if not m.get("images") or m["images"]!=images(q,"scene_*.png") or read(q/"scene_notes.json").get("manifest")!=hashobj(m):fail("scene evidence missing/stale")
    r=read(q/"prop_receipt.json")
    if r.get("scene")!=hashobj(m) or r.get("props")!=hashobj(S.get("props",{})):fail("prop review missing/stale")
    e=plan_errors(S["shots"])
    if e:work(say,"Replan from real scene: "+"; ".join(e))
    if not all(any(n in s["scene_evidence"] for n in m["images"]) for s in S["shots"]):work(say,"Reference actual scene filename for each shot")
    write(q/"replan_receipt.json",{"shots":shots(S),"scene":hashobj(m)})
    say("OK camera replan")
def require_replan(S,root):
    q=folder(root,S["story"],S["part"]);m=read(q/"scene_manifest.json");r=read(q/"replan_receipt.json")
    return bool(m.get("images") and m["images"]==images(q,"scene_*.png") and r.get("shots")==shots(S) and r.get("scene")==hashobj(m))
def capture_cams(S,root,J):
    q=folder(root,S["story"],S["part"]);q.mkdir(parents=True,exist_ok=True)
    for p in q.glob("cam_*.png"):p.unlink()
    for p in J.glob("cam_*.png"):shutil.copy2(p,q/p.name)
    im=images(q,"cam_*.png")
    for i in range(1,len(S["shots"])+1):
        if sum(n.startswith(f"cam_{i:02d}_") for n in im)<3:raise ValueError("missing samples for shot "+str(i))
    write(q/"camera_manifest.json",{"shots":shots(S),"images":im,"time":time.time()})
def check_editorial(S,root,J,fail,say):
    q=folder(root,S["story"],S["part"]);m=read(q/"camera_manifest.json");d=read(q/"editorial_notes.json")
    if m.get("shots")!=shots(S) or not m.get("images") or m["images"]!=images(q,"cam_*.png"):fail("camera evidence missing/stale")
    if d.get("manifest")!=hashobj(m) or set(d.get("seen_images",[]))!=set(m["images"]) or not all(text(d.get(k)) for k in ("story_review","editor_review","pacing","continuity","scale_rhythm")):
        work(say,f"Inspect ALL images in sequence in {q}; second pass editorial_notes.json manifest={hashobj(m)}, seen_images, story_review, editor_review, pacing, continuity, scale_rhythm, shots=[{{shot:1,actual_size:MCU,observation:...,pass:true}}], pass=true only if verified. Stills do not prove playback.")
    rows=d.get("shots",[])
    if [x.get("shot") for x in rows]!=list(range(1,len(S["shots"])+1)) or any(not text(x.get("observation")) or x.get("actual_size") not in ("EST","MS","MCU","CU","OTS","TWO","INSERT") for x in rows):work(say,"Complete each shot observation")
    if d.get("pass") is not True or any(x.get("pass") is not True for x in rows) or (len(rows)>=4 and sum(x.get("actual_size")=="CU" for x in rows)/len(rows)>.6):fail("editorial review rejected; repair and recheck")
    write(q/"editorial_receipt.json",{"manifest":hashobj(m),"notes":hashobj(d),"shots":shots(S),"spec_sha256":digest(S["_spec"]) if S.get("_spec") else None})
    say("OK editorial still sequence review; final playback required")
def check_final(S,root,fail,say):
    q=folder(root,S["story"],S["part"]);p=Path(S["video"]);pr=Path(S["project"])
    if not p.is_file() or not pr.is_file():fail("video/project missing")
    h=digest(p);d=read(q/"final_notes.json")
    if d.get("video_sha256")!=h or not all(text(d.get(k)) for k in ("moving_review","audio_review","cuts_review","continuity")):
        work(say,f"Review actual complete MP4 {p} including moving playback, audio and cuts; write {q/'final_notes.json'} with video_sha256={h}, moving_review,audio_review,cuts_review,continuity,pass=true only if verified")
    if d.get("pass") is not True:fail("final review rejected")
    write(q/"final_receipt.json",{"video_sha256":h,"size":p.stat().st_size,"mtime_ns":p.stat().st_mtime_ns,"project_size":pr.stat().st_size,"project_mtime_ns":pr.stat().st_mtime_ns})
    say("OK final review")

def prop_review(S,root,J,job,load_props,fail,say):
    """Verify prop decision from scene evidence; import only newly requested props and re-survey."""
    q=folder(root,S["story"],S["part"]);m=read(q/"scene_manifest.json")
    d=read(q/"prop_review.json");applied=read(q/"prop_apply_receipt.json")
    # On retry following a new import, capture fresh scene and ask for new observations.
    if applied.get("pending_resurvey"):
        scene_review(S,root,J,job,fail,say)
        applied["pending_resurvey"]=False;write(q/"prop_apply_receipt.json",applied)
        m=read(q/"scene_manifest.json");d=read(q/"prop_review.json")
    if not m.get("images") or m["images"]!=images(q,"scene_*.png"):fail("missing current scene survey")
    if d.get("manifest")!=hashobj(m) or not text(d.get("reason")) or not isinstance(d.get("missing"),list):
        work(say,f"Inspect actual scene. {q/'prop_review.json'}: manifest={hashobj(m)}, reason (why needed/not needed), missing=[prop names] or [], pass=true only after all props visible. For missing items use existing asset or Blender skill, add spec props with fbx,pos,yaw,scale and asset_receipt for generated geometry; no mandatory prop creation.")
    missing=d["missing"]
    if not missing:
        if d.get("pass") is not True:work(say,"Review actual props and set pass only if suitable")
        write(q/"prop_receipt.json",{"scene":hashobj(m),"props":hashobj(S.get("props",{})),"notes":hashobj(d)})
        say("OK prop review");return
    if len(set(missing))!=len(missing) or any(n not in S.get("props",{}) for n in missing):work(say,"Add needed props in spec; use Blender builder for authored models")
    selected={n:S["props"][n] for n in missing}
    for n,c in selected.items():
        p=Path(c["fbx"])
        if not p.is_file():work(say,"Missing exported FBX: "+n)
        if c.get("asset_receipt"):
            a=read(c["asset_receipt"])
            if a.get("geometry_pass") is not True or a.get("fbx_sha256")!=digest(p):fail("Blender asset QA receipt mismatch: "+n)
        elif c.get("generated"):fail("generated prop requires geometry QA receipt: "+n)
    if applied.get("props")==hashobj(selected):fail("same props already imported; inspect actual scene, repair placement if needed")
    load_props(dict(S,props=selected))
    write(q/"prop_apply_receipt.json",{"props":hashobj(selected),"pending_resurvey":True})
    # Force new evidence even if previously planned item was not visible.
    (q/"scene_manifest.json").unlink(missing_ok=True)
    work(say,"Props imported. Run do again for fresh scene survey; visually verify material, size, placement and contact. If handled prop requires pose repair, repair pose before camera replan.")

def editorial_valid(S,root):
    q=folder(root,S["story"],S["part"])
    r=read(q/"editorial_receipt.json");m=read(q/"camera_manifest.json");d=read(q/"editorial_notes.json")
    return bool(S.get("_spec") and r.get("spec_sha256")==digest(S["_spec"]) and r.get("shots")==shots(S) and r.get("manifest")==hashobj(m) and r.get("notes")==hashobj(d) and d.get("pass") is True and m.get("images") and m["images"]==images(q,"cam_*.png"))
