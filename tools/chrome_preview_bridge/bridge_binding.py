"""Explicit local preview binding; never infer a new chat from browser history."""
from pathlib import Path
from urllib.parse import urlsplit
import json,re,time,uuid
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent/'preview_bridge_local'
def read(p):
    try:return json.loads(p.read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return {}
def current():
    import sys
    sys.path.insert(0,str(ROOT.parent.parent/"scripts"))
    from workflow_state import active_context
    n=active_context(ROOT.parent.parent)
    s,p=n.get('story'),str(n.get('part',''))
    if not isinstance(s,str) or not s or not re.fullmatch(r'\d+(?:\.\d+)?',p):raise ValueError('No valid active story/part')
    return n
def binding():
    return read(STATE/'authorization.local.json')
def bind(url):
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc!='chatgpt.com' or not re.search(r'/c/[a-zA-Z0-9-]+/?$',u.path):raise ValueError('Invalid conversation URL')
    n=current()
    j=read(STATE/'job.json')
    if j.get('state') in ('pending','claimed','needs_review') or (n.get('step')=='cams' and n.get('state')=='running'):raise ValueError('Preview is busy; resolve it before rebinding')
    b={'story':n['story'],'url':u.origin if hasattr(u,'origin') else 'https://chatgpt.com'+u.path.rstrip('/')}
    STATE.mkdir(exist_ok=True)
    p=STATE/'authorization.tmp';p.write_text(json.dumps(b,ensure_ascii=False),encoding='utf-8');p.replace(STATE/'authorization.local.json')
    return b

def handoff_pending():
    h=read(STATE/"handoff.json")
    if h.get("state")=="pending" and time.time()-h.get("created",0)<86400:return h
    return {}

def handoff_options():
    import sys
    sys.path.insert(0,str(ROOT.parent.parent/"scripts"))
    from workflow_state import active_context
    from sleep_session import complete,state
    base=ROOT.parent.parent
    if state(base).get("enabled"):raise ValueError("Sleep is active")
    n=active_context(base);story=n.get("story");part=str(n.get("part",""))
    if not story:raise ValueError("No active story")
    # Use the actual plan order, plus valid existing specs (same supported IDs as CLI).
    data=read(base/"stories"/(story+".json"))
    ids=list(dict.fromkeys(str(p["n"]) for p in data.get("parts",[]) if re.fullmatch(r"\d+(?:\.\d+)?",str(p.get("n","")))))
    extra={p.stem[len(story)+1:] for p in (base/"parts").glob(story+"_*.json")}
    ids.extend(sorted((x for x in extra if x not in ids and re.fullmatch(r"\d+(?:\.\d+)?",x)),key=lambda x:tuple(map(int,x.split(".")))))
    if part not in ids:raise ValueError("No valid selected part")
    default=part
    if ids.index(part)+1<len(ids) and complete(base,story,part):default=ids[ids.index(part)+1]
    return {"story":story,"parts":ids,"selected":part,"default":default}

def chat_code():
    """Code GPT writes in its reply so the plugin binds THAT chat (user 2026-11-28: no bind button)."""
    from sleep_session import state
    if state(ROOT.parent.parent).get("enabled"):return ""
    h=handoff_pending()
    if not h:
        h=dict(id=uuid.uuid4().hex,state="pending",created=time.time(),mode="generic")
        STATE.mkdir(exist_ok=True)
        p=STATE/"handoff.tmp";p.write_text(json.dumps(h,ensure_ascii=False),encoding="utf-8");p.replace(STATE/"handoff.json")
    return "[iClone Handoff "+h["id"]+"]"

def handoff_create(part=None,story=None,kind="continue"):
    from prompt_handoff import build
    from sleep_session import state
    base=ROOT.parent.parent
    if state(base).get("enabled"):raise ValueError("Sleep is active")
    # No part selector or snapshot: bind to actual active story when the user posts.
    h=dict(id=uuid.uuid4().hex,state="pending",created=time.time(),mode="generic")
    prompt="[iClone Handoff "+h["id"]+"]\n"+build(kind,base)
    STATE.mkdir(exist_ok=True)
    p=STATE/"handoff.tmp";p.write_text(json.dumps(h,ensure_ascii=False),encoding="utf-8");p.replace(STATE/"handoff.json")
    return {"prompt":prompt}

def handoff_bind(id,url):
    h=handoff_pending()
    if not h or h["id"]!=id:raise ValueError("Unknown or expired handoff")
    n=current()
    if h.get("mode")!="generic" and (n["story"],str(n["part"]))!=(h["story"],h["part"]):raise ValueError("Target not selected yet")
    from sleep_session import state
    if state(ROOT.parent.parent).get("enabled"):raise ValueError("Sleep is active")
    raw=read(ROOT.parent.parent/"progress"/"now.json")
    if raw.get("state")=="running":raise ValueError("Production step running; wait")
    # A confirmed newer handoff may supersede a stranded, unsent old-chat draft.
    # Never touch an ambiguous sending/needs_review job, or an active same-chat job.
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc!='chatgpt.com' or not re.search(r'/c/[a-zA-Z0-9-]+/?$',u.path):
        raise ValueError("Invalid conversation URL")
    target='https://chatgpt.com'+u.path.rstrip('/')
    j=read(STATE/'job.json')
    if (h.get("mode")=="generic" and j.get("state")=="claimed"
        and j.get("phase")=="drafted" and j.get("diagnostic")=="waiting: bound chat not unique"
        and j.get("url")!=target and j.get("created",0)<h.get("created",0)
        and re.fullmatch(r"[a-f0-9]{32}",str(j.get("id","")))
        and j.get("url")==binding().get("url")):
        archive=STATE/"superseded"/j["id"]
        archive.mkdir(parents=True,exist_ok=True)
        import shutil
        shutil.copy2(STATE/'job.json',archive/'job.json')
        if (STATE/'preview.jpg').is_file():shutil.copy2(STATE/'preview.jpg',archive/'preview.jpg')
        j.update(state="superseded",result="New verified handoff; unsent old-chat draft archived, not delivered")
        p=STATE/'job.tmp';p.write_text(json.dumps(j,ensure_ascii=False),encoding="utf-8");p.replace(STATE/'job.json')
    b=bind(url)
    if h.get("mode")!="generic":b["part"]=h["part"]
    p=STATE/"authorization.tmp";p.write_text(json.dumps(b,ensure_ascii=False),encoding="utf-8");p.replace(STATE/"authorization.local.json")
    h.update(state="bound",url=b["url"])
    p=STATE/"handoff.tmp";p.write_text(json.dumps(h,ensure_ascii=False),encoding="utf-8");p.replace(STATE/"handoff.json")
    return b
