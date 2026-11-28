"""Queue exactly one fresh, successful camera contact sheet for the authorized chat.

2026-11-28 (user: images sometimes never arrive, it stops by itself, no error shown):
- the relay is started here when it is not running, and a dead relay is reported, never "queued"
- a delivery stuck > STALE seconds no longer blocks every later image: the fresh image replaces it
- status_line() is the one-line send state the Preview window shows
"""
from pathlib import Path
import sys,json,uuid,os,re,time,subprocess,urllib.request
from urllib.parse import urlsplit
from bridge_binding import current,binding,handoff_pending
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent/'preview_bridge_local'
PORT=18764
STALE=600   # a claimed/needs_review job older than this is stuck, not "in progress"

def relay_up(timeout=0.5):
    try:
        key=(ROOT/'relay.key').read_text().strip()
        req=urllib.request.Request(f'http://127.0.0.1:{PORT}/goal/status',headers={'X-Preview-Key':key})
        with urllib.request.urlopen(req,timeout=timeout) as r:return r.status==200
    except Exception:return False

def ensure_relay(wait=8):
    """True when the relay answers. Starts it (hidden, detached, outlives this script) if needed."""
    if relay_up():return True
    exe=Path(sys.executable);w=exe.with_name('pythonw.exe')
    STATE.mkdir(exist_ok=True)
    log=open(STATE/'relay.log','a',encoding='utf-8')
    flags=getattr(subprocess,'DETACHED_PROCESS',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0)
    try:subprocess.Popen([str(w if w.exists() else exe),'-B',str(ROOT/'relay.py')],cwd=str(ROOT),stdout=log,stderr=log,stdin=subprocess.DEVNULL,creationflags=flags,close_fds=True)
    except OSError:return False
    end=time.time()+wait
    while time.time()<end:
        time.sleep(0.5)
        if relay_up():return True
    return False

def read_job():
    try:return json.loads((STATE/'job.json').read_text(encoding='utf-8'))
    except (OSError,ValueError):return {}

def stuck(old,now=None):
    """Why an unresolved job may be replaced by a fresh image, or None while it is really in flight."""
    st=old.get('state')
    if st not in ('pending','claimed','needs_review'):return None
    age=(now or time.time())-float(old.get('created',0) or 0)
    if st=='pending':return 'never picked up (%d s)'%age   # nothing attached yet: a newer image is always better
    if age>STALE:return '%s/%s for %d s'%(st,old.get('phase'),age)
    return None

def queue(image,story,part,kind="review"):
    n=current();auth=binding();h=handoff_pending()
    if h and (h.get('mode')=='generic' or (h.get('story'),h.get('part'))==(story,str(part))):return 'skipped: waiting for new handoff chat to bind; queue fresh image after binding'
    if auth.get('part') and auth['part']!=str(part):return 'skipped: bound chat belongs to a different part'
    if story!=n.get('story') or str(part)!=str(n.get('part')) or story!=auth.get('story'):return 'skipped: bind current story/chat and verify active part'
    old=read_job();replaced=None
    if old.get('state') in ('pending','claimed','needs_review'):
        why=stuck(old)
        if not why:return 'skipped: previous delivery still in progress (%s/%s)'%(old.get('state'),old.get('phase'))
        replaced={'id':old.get('id'),'state':old.get('state'),'phase':old.get('phase'),'diagnostic':old.get('diagnostic'),'result':old.get('result'),'why':why}
    url=auth.get('url','')
    if not url.startswith('https://'):url='https://'+url
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc!='chatgpt.com' or not re.search(r'/c/[a-zA-Z0-9-]+$',u.path):raise ValueError('invalid bound chat')
    b=Path(image).read_bytes()
    if not b.startswith(b'\xff\xd8') or len(b)>8_000_000:raise ValueError('invalid preview')
    session_path=Path(__file__).resolve().parents[2]/'progress'/'sleep_session.json'
    session=json.loads(session_path.read_text(encoding='utf-8')) if session_path.exists() else {}
    j={'sleep':bool(session.get('enabled') and session.get('phase')=='work' and session.get('story')==story and session.get('part')==str(part)), 'id':uuid.uuid4().hex,'url':'https://chatgpt.com'+u.path,'state':'pending','created':time.time(),'kind':kind}
    if replaced:j['replaced']=replaced
    STATE.mkdir(exist_ok=True)
    tmp=STATE/'preview.tmp';tmp.write_bytes(b);tmp.replace(STATE/'preview.jpg')
    tmp=STATE/'job.tmp';tmp.write_text(json.dumps(j,ensure_ascii=False),encoding='utf-8');tmp.replace(STATE/'job.json')
    msg='queued one preview'+(' (replaced stuck delivery: %s)'%replaced['why'] if replaced else '')
    if not ensure_relay():msg+='; WARNING relay not running and could not start: run tools/chrome_preview_bridge/start-relay.cmd (see preview_bridge_local/relay.log)'
    return msg

WAIT_TH={'mouse or keyboard active':'รอให้หยุดใช้เมาส์/คีย์บอร์ด 15 วินาที','bound chat not unique':'เปิดแชตที่ผูกไว้ใน Chrome ให้มีแท็บเดียว',
         'user active':'รอให้หยุดใช้เมาส์/คีย์บอร์ด','user_draft':'ช่องพิมพ์มีข้อความค้าง','other_attachment':'มีไฟล์อื่นแนบค้างในช่องพิมพ์',
         'busy':'รอ GPT ตอบจบ','composer_missing':'หาช่องพิมพ์ไม่เจอ','wrong_chat':'แท็บไม่ได้อยู่ที่แชตที่ผูกไว้'}

def status_line():
    """One Thai line for the Preview window: is the image on its way, and if not, what it waits for."""
    j=read_job()
    if not j.get('id'):return ''
    st=j.get('state');age=time.time()-float(j.get('created',0) or 0)
    if st=='sent':return 'ส่งรูป: ✓ ถึงแชตแล้ว' if age<3600 else ''
    up=relay_up(0.3)
    if not up:return 'ส่งรูป: ⚠ relay ไม่ทำงาน — เปิด start-relay.cmd'
    d=str(j.get('diagnostic') or j.get('result') or '').replace('waiting: ','')
    why=next((v for k,v in WAIT_TH.items() if k in d),d[:40])
    if st=='needs_review':return 'ส่งรูป: ⚠ ไม่แน่ใจว่าส่งถึง (%s) — ตรวจแชต'%why
    tail=' · ค้าง %d นาที'%(age//60) if age>120 else ''
    return 'ส่งรูป: %s%s%s'%('รอส่ง' if st=='pending' else 'กำลังส่ง',(' — '+why) if why else '',tail)

if __name__=='__main__':print(queue(*sys.argv[1:5]))
