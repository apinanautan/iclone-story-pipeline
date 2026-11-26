"""Queue exactly one fresh, successful camera contact sheet for the authorized chat."""
from pathlib import Path
import sys,json,uuid,os,re,time
from urllib.parse import urlsplit
from bridge_binding import current,binding
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent/'preview_bridge_local'
def queue(image,story,part,kind="review"):
    n=current();auth=binding()
    if story!=n.get('story') or str(part)!=str(n.get('part')) or story!=auth.get('story'):return 'skipped: bind current story/chat and verify active part'
    state=STATE/'job.json'
    if state.exists():
        old=json.loads(state.read_text(encoding='utf-8'))
        if old.get('state') in ('pending','claimed','needs_review'):return 'skipped: previous delivery unresolved'
    url=auth.get('url','')
    if not url.startswith('https://'):url='https://'+url
    u=urlsplit(url)
    if u.scheme!='https' or u.netloc!='chatgpt.com' or not re.search(r'/c/[a-zA-Z0-9-]+$',u.path):raise ValueError('invalid bound chat')
    b=Path(image).read_bytes()
    if not b.startswith(b'\xff\xd8') or len(b)>8_000_000:raise ValueError('invalid preview')
    ss=ROOT.parent.parent/"progress"/"sleep_session.json"
    session=json.loads(ss.read_text(encoding="utf-8")) if ss.exists() else {}
    j={"sleep":bool(session.get("enabled") and session.get("phase")=="work" and session.get("story")==story and session.get("part")==str(part)),'id':uuid.uuid4().hex,'url':'https://chatgpt.com'+u.path,'state':'pending','created':time.time(),'kind':kind}
    tmp=STATE/'preview.tmp';tmp.write_bytes(b);tmp.replace(STATE/'preview.jpg')
    tmp=STATE/'job.tmp';tmp.write_text(json.dumps(j),encoding='utf-8');tmp.replace(state)
    return 'queued one preview'
if __name__=='__main__':print(queue(*sys.argv[1:5]))
