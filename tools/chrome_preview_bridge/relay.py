from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os,hmac,json,threading,sys,re
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import sleep_session as sleep
from preview_gate import dispatch,Blocked,reconcile_orphaned_run
from workflow_state import active_context
BASE=Path(__file__).resolve().parents[2]
from prompt_handoff import build
import goal_signal
from bridge_binding import bind,binding,handoff_options,handoff_create,handoff_bind,handoff_pending
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent/'preview_bridge_local'
KEY=(ROOT/'relay.key').read_text().strip()
IMAGE=Path(os.environ['LOCALAPPDATA'])/'Tidmunz Studio'/'snapgen_data'/'ic8_jobs'/'part_cams.jpg'
LOCK=threading.Lock()
import hashlib
CODE=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]   # which relay.py this process runs
def read_state():
    try:return json.loads((STATE/'job.json').read_text(encoding='utf-8'))
    except (OSError,ValueError):return {}
def save_state(j):
    p=STATE/'job.tmp';p.write_text(json.dumps(j,ensure_ascii=False),encoding='utf-8');p.replace(STATE/'job.json')
def sleep_readiness():
    # UI and prompt availability must reflect the actual runtime, not a released candidate.
    try:
        v=(BASE/"VERSION").read_text(encoding="utf-8").strip()
        ctrl=(BASE/"scripts"/"ai_iclone.py").read_text(encoding="utf-8")
        part=(BASE/"scripts"/"ic8_part.py").read_text(encoding="utf-8")
        if not all(x in ctrl for x in ("sleep-approve","final_review","prop_review","camera_replan")) or not all(x in part for x in ("editorial_valid","approval_valid","step_final_review")):
            return False,"Sleep Mode requires the integrated cinematic runtime; installed version "+v
        return True,"ready"
    except (OSError,ValueError):
        return False,"Cannot verify the installed runtime"

def goal_checkpoint():
    # Ignore time/retry counters: only verified work or file changes count as progress.
    n=active_context(BASE)
    story=n.get("story");part=str(n.get("part",""))
    if not story or not part:return None
    d=sleep.read(BASE/"progress"/f"{story}_{part}.json")
    spec=sleep.read(BASE/"parts"/f"{story}_{part}.json")
    media={}
    try:
        from paths import expand
        for k in ("project","video"):
            if spec.get(k):
                f=Path(expand(spec[k]))
                if f.is_file():
                    st=f.stat();media[k]=[st.st_size,st.st_mtime_ns]
    except (OSError,ValueError,SystemExit):pass
    return sleep.hashobj({"story":story,"part":part,
                          "done":sorted(d.get("steps_done",{})),
                          "approval":bool(d.get("ok",{}).get("step5")),
                          "files":media})

def goal_control():
    return sleep.read(STATE/"goal_stop.json")

def local_goal_block(url=None):
    c=goal_control()
    if not c.get("stopped"):return None
    # Legacy unbound retry limit was not a real production blocker.
    if c.get("checkpoint")=="unbound":return None
    # A message count alone is not proof that work is blocked.
    if c.get("reason","").startswith("Preview unchanged after two follow-ups;"):return None
    if c.get("url") and url and c["url"]!=url:return None
    if c.get("checkpoint") and c["checkpoint"]!=goal_checkpoint():return None
    return {"stop":True,"reason":c.get("reason","paused by local control")}

def goal_resume(url):
    # Explicit click starts a new tracking session, not a Preview binding.
    sleep.write(STATE/"goal_stop.json",{"stopped":False})
    return goal_gate(url)

def goal_attempt(url,session,marker):
    g=goal_gate(url)
    if g.get("stop") or g.get("wait"):return g
    auth=binding();ss=sleep.state(BASE);n=active_context(BASE)
    scoped=(auth.get("url")==url and auth.get("story")==n.get("story")) or (ss.get("enabled") and ss.get("url")==url)
    if not scoped:
        # Generic chats have no Preview receipt. Browser delivery/achievement/pause
        # control them; never treat missing iClone binding as failure.
        return {"stop":False,"mode":"generic"}
    # The current gate, not the number of prompts, decides whether work can continue.
    # No retry budget is reset by fake progress; no receipt is changed here.
    if n.get("state")=="running":return {"stop":False,"wait":True,"reason":"Preview step running"}
    return g



def goal_gate(url):
    blocked=local_goal_block(url)
    if blocked:return blocked
    auth=binding()
    # An unbound chat in the same ChatGPT project as the bound one works on the same story (user 2026-11-28:
    # the tracker kept nudging an unbound chat after the work had stopped).
    proj=lambda u:(re.match(r"https://chatgpt\.com/g/[^/]+/",u or "") or [None])[0]
    if not url or (auth.get("url")!=url and not (proj(url) and proj(url)==proj(auth.get("url")))):return {"stop":False}
    ss=sleep.state(BASE)
    n=active_context(BASE)
    if auth.get("story")!=n.get("story"):return {"stop":False}
    if auth.get("part") and auth["part"]!=str(n.get("part")):return {"stop":True,"reason":"Handoff target changed; use the new part chat"}
    if n.get("state")=="running":return {"stop":False,"wait":True,"reason":"Preview step running"}
    if ss.get("enabled"):return {"stop":False}
    try:
        import progress_app as P
        story=n["story"];part=str(n["part"])
        st=P.story_states(story)
        nxt=next((k for k,_ in P.STORY_STEPS if st[k][0]!="done"),None)
        if nxt in ("range","story_ok"):return {"stop":True,"reason":"waiting for user: "+nxt}
        if nxt:return {"stop":False,"mode":"repair" if st[nxt][0] in ("bad","warn","fail") else "work","step":nxt}
        ps,_=P.step_states(story,part)
        nxt=next((k for k,_ in P.STEPS if ps[k] not in ("done","skip")),None)
        if nxt=="user_ok":return {"stop":True,"reason":"waiting for user approval"}
        if nxt is None:return {"stop":True,"reason":"Preview part complete"}
        import ai_iclone
        why=ai_iclone.program_stop(story,part,nxt)
        if why:return {"stop":True,"reason":why}
        repair=ps[nxt] in ("bad","warn","fail","failed") or (n.get("state")=="failed" and n.get("step")==nxt)
        return {"stop":False,"mode":"repair" if repair else "work","step":nxt}
    except Exception:return {"stop":False,"wait":True,"reason":"Preview status unavailable"}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def authorized(self):
        if hmac.compare_digest(self.headers.get('X-Preview-Key',''),KEY):return True
        self.send_error(403);return False
    def reply(self,data,typ='application/json',status=200):
        self.send_response(status);self.send_header('Content-Type',typ);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.authorized():return
        if self.path=='/ext/version':
            try:sync_installed()
            except OSError:pass
            self.reply(json.dumps({"version":ext_version(),"code":CODE}).encode());return
        if self.path=='/goal/status':
            self.reply(json.dumps(goal_control()).encode());return
        if self.path=='/sleep/status':
            ready,reason=sleep_readiness(); current=active_context(BASE); self.reply(json.dumps(dict(sleep.state(BASE),ready=ready,reason=reason,current_part=current.get("part")),ensure_ascii=False).encode());return
        if self.path=='/sleep/prompt':
            try:
                ready,reason=sleep_readiness()
                if not ready:raise ValueError(reason)
                ss=sleep.state(BASE)
                if not ss.get('enabled') or ss.get('phase') not in ('work','handoff'):raise ValueError()
                self.reply(json.dumps({'prompt':build('sleep',BASE)},ensure_ascii=False).encode())
            except (OSError,ValueError):self.send_error(409,'Sleep prompt unavailable')
            return
        if self.path=='/handoff/options':
            try:self.reply(json.dumps(handoff_options(),ensure_ascii=False).encode())
            except (OSError,ValueError):self.send_error(409,'No valid handoff target')
            return
        if self.path in ('/prompt/new','/prompt/continue'):
            try:self.reply(json.dumps({'prompt':build(self.path.rsplit('/',1)[-1])},ensure_ascii=False).encode())
            except (OSError,ValueError):self.send_error(409,'Prompt data unavailable')
            return
        if self.path=='/status':
            with LOCK:j=read_state()
            try:
                run=reconcile_orphaned_run(BASE)
            except (OSError,ValueError):run={}
            self.reply(json.dumps({'job':{k:j.get(k) for k in ('id','url','state','phase','result','kind','sleep')},'bound':binding(),'generating':run.get('step')=='cams' and run.get('state')=='running','now':{k:active_context(BASE).get(k) for k in ('story','part','step','state')}},ensure_ascii=False,default=str).encode());return
        if self.path=='/pending':
            with LOCK:j=read_state()
            self.reply(json.dumps(j if j.get('state')=='pending' or (j.get('state')=='claimed' and j.get('phase') in ('recover','attached','drafted')) else {},ensure_ascii=False).encode());return
        if self.path=='/preview':
            p=IMAGE
        elif self.path.startswith('/image/'):
            with LOCK:j=read_state()
            if self.path!='/image/'+str(j.get('id','')) or j.get('state')!='claimed':self.send_error(404);return
            p=STATE/'preview.jpg'
        else:self.send_error(403);return
        try:
            b=p.read_bytes()
            if not b.startswith(b'\xff\xd8') or len(b)>8_000_000:raise ValueError()
        except (OSError,ValueError):self.send_error(404);return
        self.reply(b,'image/jpeg')
    def do_POST(self):
        if not self.authorized():return
        if self.path not in ('/claim','/receipt','/diagnostic','/stage','/bind','/sleep/start','/sleep/pause','/sleep/advance','/sleep/bind','/goal/check','/goal/resume','/goal/attempt','/goal/signal','/goal/signal-ack','/handoff/create','/handoff/bind'):self.send_error(403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<4096:raise ValueError()
            q=json.loads(self.rfile.read(n))
            if self.path in ("/goal/signal","/goal/signal-ack"):
                # Do not acquire production/Preview lock; this is only a stop mailbox.
                code=goal_signal.code_key(q.get("code",""))
                if self.path=="/goal/signal":result=goal_signal.read(code)
                else:result=goal_signal.acknowledge(code,q.get("id"),q.get("session"))
                self.reply(json.dumps(result).encode());return
            if self.path in ("/goal/check","/goal/resume","/goal/attempt"):
                url=str(q.get("url",""))
                from urllib.parse import urlsplit
                u=urlsplit(url)
                if u.scheme!="https" or u.netloc!="chatgpt.com" or "/c/" not in u.path:self.send_error(400);return
                with LOCK:
                    if self.path=="/goal/resume":
                        self.reply(json.dumps(goal_resume(url)).encode());return
                    if self.path=="/goal/attempt":
                        session=q.get("session");marker=q.get("marker")
                        if not isinstance(session,str) or not 1<=len(session)<=100 or not isinstance(marker,str) or not 1<=len(marker)<=100:self.send_error(400);return
                        result=goal_attempt(url,session,marker)
                    else:result=goal_gate(url)
                self.reply(json.dumps(result).encode());return
            if self.path.startswith("/sleep/"):
                try:
                    with LOCK,dispatch():
                        a=self.path.rsplit("/",1)[-1];ss=sleep.state(BASE)
                        if a=="pause":result=sleep.pause(BASE)
                        else:
                            ready,reason=sleep_readiness()
                            if not ready:raise sleep.SleepError(reason)
                            j=read_state()
                            if j.get("state") in ("pending","claimed","needs_review"):raise sleep.SleepError("preview delivery unresolved")
                            now=sleep.read(BASE/"progress"/"now.json")
                            if now.get("state")=="running":raise sleep.SleepError("production step running")
                            if a=="start":
                                auth=binding()
                                if auth.get("url")!=q.get("url") or auth.get("story")!=now.get("story"):raise sleep.SleepError("bind exact story chat first")
                                blocked=local_goal_block()
                                if blocked and goal_control().get("checkpoint"):raise sleep.SleepError(blocked["reason"])
                                scope=q.get("scope","all")
                                if scope not in ("all","current"):raise sleep.SleepError("invalid scope")
                                result=sleep.start(BASE,now["story"],q["url"],q.get("confirmed"),from_part=str(now["part"]) if scope=="current" else None,protect_part=str(now["part"]))
                                sleep.write(STATE/"goal_stop.json",{"stopped":False})
                            elif a=="advance":
                                if ss.get("url")!=q.get("url") or ss.get("session")!=q.get("session"):raise sleep.SleepError("wrong session/chat")
                                result=sleep.advance(BASE)
                            elif a=="bind":
                                if ss.get("session")!=q.get("session"):raise sleep.SleepError("wrong session")
                                result=sleep.bind_next(BASE,q["url"])
                                # bind to selected story rather than stale progress/now part
                                sleep.write(STATE/"authorization.local.json",{"story":result["story"],"url":result["url"]})
                            else:raise sleep.SleepError("unknown action")
                            if result.get("part") and result.get("enabled"):
                                sleep.write(BASE/"progress"/"ai_iclone.json",{"story":result["story"],"part":result["part"]})
                        self.reply(json.dumps(result,ensure_ascii=False).encode());return
                except (sleep.SleepError,Blocked,ValueError,KeyError,OSError) as e:
                    self.reply(json.dumps({"error":str(e)},ensure_ascii=False).encode(),status=409);return
            if self.path in ("/handoff/create","/handoff/bind"):
                try:
                    with LOCK:
                        if self.path=="/handoff/create":result=handoff_create()
                        else:result=handoff_bind(str(q.get("id","")),str(q.get("url","")))
                    self.reply(json.dumps(result,ensure_ascii=False).encode())
                except (ValueError,OSError) as e:self.reply(json.dumps({"error":str(e)}).encode(),status=409)
                return
            if self.path=="/bind":
                with LOCK:
                    b=bind(str(q.get("url","")))
                    h=handoff_pending()
                    if h and (h.get("mode")=="generic" or h.get("story")==b.get("story")):
                        sleep.write(STATE/"handoff.json",dict(h,state="cancelled"))
                self.reply(json.dumps(b,ensure_ascii=False).encode());return
            with LOCK:
                j=read_state()
                if q.get('id')!=j.get('id'):self.send_error(409);return
                if self.path=='/diagnostic' and j.get('state') in ('pending','claimed'):j['diagnostic']=str(q.get('result',''))[:200]
                elif self.path=='/claim' and j.get('state')=='pending':
                    j['state']='claimed';j['phase']='attach'
                elif self.path=='/stage' and j.get('state')=='claimed':
                    target=q.get('phase')
                    allowed={'attach':('attached','pending'),'recover':('attached','drafted','pending'),'attached':('drafted',),'drafted':('sending',),'sending':('drafted',)}
                    if target not in allowed.get(j.get('phase'),()):self.send_error(409);return
                    j['phase']=target
                    if target=='pending':j['state']='pending'
                elif self.path=='/receipt' and (j.get('state')=='claimed' or (j.get('state')=='needs_review' and q.get('state')=='sent')):
                    j['state']='sent' if q.get('state')=='sent' else 'needs_review'
                    j['result']=str(q.get('result',''))[:300]
                else:self.send_error(409);return
                save_state(j)
            self.reply(b'{"ok":true}')
        except (ValueError,OSError):self.send_error(400)
EXT_FILES=("manifest.json","background.js","popup.html","popup.js","sleep_popup.js","sleep_mode.js","goal_tracker.js","goal_panel.js","achievement_observer.js","README.txt")
def ext_version(d=ROOT):
    try:return json.loads((Path(d)/"manifest.json").read_text(encoding="utf-8")).get("version","")
    except (OSError,ValueError):return ""
def chrome_installs():
    # Chrome loads this extension unpacked from whatever folder the user picked (often a copy in Downloads).
    out=set()
    for f in (Path(os.environ.get("LOCALAPPDATA",""))/"Google"/"Chrome"/"User Data").glob("*/*Preferences"):
        try:d=json.loads(f.read_text(encoding="utf-8"))
        except (OSError,ValueError):continue
        for v in d.get("extensions",{}).get("settings",{}).values():
            p=Path(v.get("path","")) if isinstance(v,dict) and v.get("location")==4 else None
            if p and p.is_dir() and p.resolve()!=ROOT.resolve() and (p/"manifest.json").is_file():
                try:
                    if json.loads((p/"manifest.json").read_text(encoding="utf-8")).get("name")=="iClone Preview to Chat":out.add(p)
                except (OSError,ValueError):pass
    return sorted(out)
def sync_installed(targets=None):
    # user 2026-11-28: no manual reloading. Copy new files into the loaded folder; the extension reloads itself.
    done=[]
    for t in (chrome_installs() if targets is None else targets):
        for n in EXT_FILES:
            src,dst=ROOT/n,Path(t)/n
            if src.is_file() and (not dst.is_file() or dst.read_bytes()!=src.read_bytes()):
                tmp=dst.with_suffix(dst.suffix+".tmp");tmp.write_bytes(src.read_bytes());tmp.replace(dst);done.append(str(dst))
        for b in Path(t).glob("*.bak"):b.unlink(missing_ok=True)
    return done
if __name__=='__main__':
    STATE.mkdir(exist_ok=True)
    try:sync_installed()
    except OSError:pass
    ThreadingHTTPServer(('127.0.0.1',18764),Handler).serve_forever()
