from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os,hmac,json,threading,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import sleep_session as sleep
from preview_gate import dispatch,Blocked
BASE=Path(__file__).resolve().parents[2]
from prompt_handoff import build
from bridge_binding import bind,binding
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent/'preview_bridge_local'
KEY=(ROOT/'relay.key').read_text().strip()
IMAGE=Path(os.environ['LOCALAPPDATA'])/'Tidmunz Studio'/'snapgen_data'/'ic8_jobs'/'part_cams.jpg'
LOCK=threading.Lock()
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

def goal_control():
    # Explicit stop applies even if no Preview chat is bound.
    return sleep.read(STATE/"goal_stop.json")

def goal_gate(url):
    if goal_control().get("stopped"):
        return {"stop":True,"reason":"paused by local control"}
    auth=binding()
    if not url or auth.get("url")!=url:return {"stop":False}
    ss=sleep.state(BASE)
    if ss.get("enabled"):return {"stop":False}
    n=sleep.read(BASE/"progress"/"now.json")
    if auth.get("story")!=n.get("story") or n.get("state")=="running":return {"stop":False}
    try:
        import progress_app as P
        story=n["story"];part=str(n["part"])
        st=P.story_states(story)
        nxt=next((k for k,_ in P.STORY_STEPS if st[k][0]!="done"),None)
        if nxt in ("range","story_ok"):return {"stop":True,"reason":"waiting for user: "+nxt}
        if nxt:return {"stop":False}
        ps,_=P.step_states(story,part)
        nxt=next((k for k,_ in P.STEPS if ps[k] not in ("done","skip")),None)
        if nxt=="user_ok":return {"stop":True,"reason":"waiting for user approval"}
        if nxt is None:return {"stop":True,"reason":"Preview part complete"}
        return {"stop":False}
    except Exception:return {"stop":False}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def authorized(self):
        if hmac.compare_digest(self.headers.get('X-Preview-Key',''),KEY):return True
        self.send_error(403);return False
    def reply(self,data,typ='application/json',status=200):
        self.send_response(status);self.send_header('Content-Type',typ);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.authorized():return
        if self.path=='/goal/status':
            self.reply(json.dumps(goal_control()).encode());return
        if self.path=='/sleep/status':
            ready,reason=sleep_readiness(); current=sleep.read(BASE/"progress"/"now.json"); self.reply(json.dumps(dict(sleep.state(BASE),ready=ready,reason=reason,current_part=current.get("part")),ensure_ascii=False).encode());return
        if self.path=='/sleep/prompt':
            try:
                ready,reason=sleep_readiness()
                if not ready:raise ValueError(reason)
                ss=sleep.state(BASE)
                if not ss.get('enabled') or ss.get('phase') not in ('work','handoff'):raise ValueError()
                self.reply(json.dumps({'prompt':build('sleep',BASE)},ensure_ascii=False).encode())
            except (OSError,ValueError):self.send_error(409,'Sleep prompt unavailable')
            return
        if self.path in ('/prompt/new','/prompt/continue'):
            try:self.reply(json.dumps({'prompt':build(self.path.rsplit('/',1)[-1])},ensure_ascii=False).encode())
            except (OSError,ValueError):self.send_error(409,'Prompt data unavailable')
            return
        if self.path=='/status':
            with LOCK:j=read_state()
            try:
                run=json.loads((ROOT.parent.parent/'progress'/'now.json').read_text(encoding='utf-8'))
            except (OSError,ValueError):run={}
            self.reply(json.dumps({'job':{k:j.get(k) for k in ('id','url','state','phase','result','kind','sleep')},'bound':binding(),'generating':run.get('step')=='cams' and run.get('state')=='running'},ensure_ascii=False).encode());return
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
        if self.path not in ('/claim','/receipt','/diagnostic','/stage','/bind','/sleep/start','/sleep/pause','/sleep/advance','/sleep/bind','/goal/check','/goal/resume'):self.send_error(403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<4096:raise ValueError()
            q=json.loads(self.rfile.read(n))
            if self.path in ("/goal/check","/goal/resume"):
                url=str(q.get("url",""))
                from urllib.parse import urlsplit
                u=urlsplit(url)
                if u.scheme!="https" or u.netloc!="chatgpt.com" or "/c/" not in u.path:self.send_error(400);return
                with LOCK:
                    if self.path=="/goal/resume":sleep.write(STATE/"goal_stop.json",{"stopped":False})
                    result=goal_gate(url)
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
            if self.path=="/bind":
                with LOCK:b=bind(str(q.get("url","")))
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
if __name__=='__main__':
    STATE.mkdir(exist_ok=True)
    ThreadingHTTPServer(('127.0.0.1',18764),Handler).serve_forever()
