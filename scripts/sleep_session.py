"""Opt-in, plan-bounded Sleep Mode. Never record AI approval as user's words."""
from pathlib import Path
from urllib.parse import urlsplit
import re,time,uuid
from cinematic_qa import read,write,hashobj,digest,folder
class SleepError(RuntimeError):pass
def state(root):return read(Path(root)/"progress"/"sleep_session.json")
def save(root,s):write(Path(root)/"progress"/"sleep_session.json",s);return s
def plan(root,story):
    folder(root,story,"1")
    d=read(Path(root)/"stories"/(story+".json"))
    if not d.get("story_plan_ok") or not d.get("teacher_range_confirmed"):raise SleepError("approve story plan/range first")
    rows=d.get("parts",[]);ids=[str(x.get("n")) for x in rows];tr=d.get("teacher_range",[])
    if not ids or len(set(ids))!=len(ids) or any(not re.fullmatch(r"\d+(?:\.\d+)?",n) for n in ids):raise SleepError("invalid planned parts")
    if len(tr)!=2 or any(not isinstance(x.get("master"),list) or len(x["master"])!=2 or not x["master"][0]<x["master"][1] for x in rows):raise SleepError("invalid timeline")
    if abs(rows[0]["master"][0]-tr[0])>.1 or abs(rows[-1]["master"][1]-tr[1])>1.0 or any(abs(a["master"][1]-b["master"][0])>.1 for a,b in zip(rows,rows[1:])):raise SleepError("timeline gaps")
    return ids,hashobj({"range":tr,"parts":rows,"approval":d["story_plan_ok"]})
def project_url(url):
    u=urlsplit(url);m=re.fullmatch(r"(/g/[^/]+)/c/[a-zA-Z0-9-]+/?",u.path)
    if u.scheme!="https" or u.netloc!="chatgpt.com" or not m:raise SleepError("select exact project conversation")
    return "https://chatgpt.com"+m[1]
def complete(root,story,n):
    from paths import expand
    root=Path(root);spec=read(root/"parts"/f"{story}_{n}.json");d=read(root/"progress"/f"{story}_{n}.json")
    if not spec.get("project") or not spec.get("video"):return False
    p,v=Path(expand(spec["project"])),Path(expand(spec["video"]))
    if not p.is_file() or not v.is_file() or not p.stat().st_size or not v.stat().st_size:return False
    sd=d.get("steps_done",{})
    if "final_review" not in sd:
        # Migration: only previously approved, render+video_check marked parts, from the old workflow.
        # Revalidate actual media, never manufacture a new editorial receipt.
        if "scene_review" in sd or not d.get("ok",{}).get("step5") or not all(k in sd for k in ("render","video_check")):return False
        try:
            import subprocess
            from paths import ffmpeg
            wav=Path(expand(spec["wav"]))
            if not wav.is_file():return False
            def probe(path):
                x=subprocess.run([ffmpeg("ffprobe"),"-v","error","-show_entries","format=duration:stream=codec_type","-of","json",str(path)],capture_output=True,text=True,check=True,timeout=20)
                return json.loads(x.stdout)
            import json
            vv,aa=probe(v),probe(wav)
            types={x["codec_type"] for x in vv.get("streams",[])}
            return types >= {"video","audio"} and float(vv["format"]["duration"])+.05>=float(aa["format"]["duration"])
        except (OSError,ValueError,KeyError,RuntimeError,subprocess.SubprocessError,SystemExit):return False
    if not all(k in sd for k in ("render","video_check","final_review")):return False
    r=read(folder(root,story,n)/"final_receipt.json")
    return bool(r and r.get("size")==v.stat().st_size and r.get("mtime_ns")==v.stat().st_mtime_ns and r.get("project_size")==p.stat().st_size and r.get("project_mtime_ns")==p.stat().st_mtime_ns)
def start(root,story,url,confirmed,from_part=None,protect_part=None):
    if confirmed is not True:raise SleepError("explicit Sleep Mode confirmation required")
    ids,h=plan(root,story);project=project_url(url)
    if state(root).get("enabled"):raise SleepError("already running")
    s={"enabled":True,"session":uuid.uuid4().hex,"story":story,"parts":ids,"plan":h,"project":project,"url":url.rstrip("/"),"started":time.time(),"history":[],"phase":"work"}
    if from_part is not None and str(from_part) not in ids:raise SleepError("selected part is not in approved plan")
    scope=ids[ids.index(str(from_part)):] if from_part is not None else ids
    s["scope_start"]=scope[0]
    s["part"]=next((n for n in scope if not complete(root,story,n)),None)
    if protect_part is not None and str(protect_part) in ids and s["part"] is not None and ids.index(s["part"])<ids.index(str(protect_part)):
        raise SleepError("Earlier part needs review. To preserve the open project, choose Start current part onward.")
    if from_part is not None:
        s["earlier_unverified"]=[n for n in ids[:ids.index(str(from_part))] if not complete(root,story,n)]
    if s["part"] is None:s.update(enabled=False,phase="complete")
    else:s.update(phase="handoff",old_url=s["url"],url=None)
    return save(root,s)
def active(root,story,n):
    s=state(root)
    try:return bool(s.get("enabled") and s.get("phase")=="work" and s.get("story")==story and s.get("part")==str(n) and plan(root,story)==(s["parts"],s["plan"]))
    except (SleepError,KeyError,TypeError,ValueError):return False
def approve(root,story,n):
    if not active(root,story,n):raise SleepError("no active scoped Sleep Mode")
    root=Path(root);p=root/"progress"/f"{story}_{n}.json";d=read(p);sd=d.get("steps_done",{})
    required=("check","motion_plan","open","cast","sound","pose","scene_review","prop_review","camera_replan","cams","cam_check","motion_check","light_check","face_check","editorial_review","switch")
    if any(k not in sd for k in required):raise SleepError("QA incomplete")
    spec=root/"parts"/f"{story}_{n}.json"
    if any(x.get("who") not in ("บรรยาย","narrator") for x in read(spec).get("lines",[])) and "lip" not in sd:raise SleepError("lip incomplete")
    q=folder(root,story,n);er=read(q/"editorial_receipt.json");m=read(q/"camera_manifest.json")
    if not er or er.get("spec_sha256")!=digest(spec) or er.get("manifest")!=hashobj(m) or er.get("notes")!=hashobj(read(q/"editorial_notes.json")):raise SleepError("editorial evidence stale")
    d["sleep_approval"]={"session":state(root)["session"],"spec":digest(spec),"editorial":hashobj(er),"time":time.time(),"source":"AI QA under explicit Sleep Mode scope"}
    write(p,d)
def approval_valid(root,story,n,d):
    if not active(root,story,n):return False
    a=d.get("sleep_approval",{})
    try:return a.get("session")==state(root)["session"] and a.get("spec")==digest(Path(root)/"parts"/f"{story}_{n}.json") and a.get("editorial")==hashobj(read(folder(root,story,n)/"editorial_receipt.json"))
    except (OSError,ValueError):return False
def advance(root):
    s=state(root)
    if not active(root,s.get("story"),s.get("part")):raise SleepError("not active or plan changed")
    if not complete(root,s["story"],s["part"]):raise SleepError("final review not verified")
    s["history"].append({"part":s["part"],"url":s["url"],"completed":time.time()})
    nxt=next((n for n in s["parts"][s["parts"].index(s["part"])+1:] if not complete(root,s["story"],n)),None)
    if nxt is None:s.update(enabled=False,phase="complete",part=None)
    else:s.update(phase="handoff",part=nxt,old_url=s["url"],url=None)
    return save(root,s)
def bind_next(root,url):
    s=state(root)
    if not s.get("enabled") or s.get("phase")!="handoff":raise SleepError("not waiting for next chat")
    if plan(root,s["story"])!=(s["parts"],s["plan"]) or project_url(url)!=s["project"] or url.rstrip("/")==s.get("old_url") or any(x.get("url")==url.rstrip("/") for x in s["history"]):raise SleepError("wrong project or old chat")
    s.update(phase="work",url=url.rstrip("/"));return save(root,s)
def pause(root):
    s=state(root);s.update(enabled=False,phase="paused");return save(root,s)
