"""Explicit local preview binding; never infer a new chat from browser history."""
from pathlib import Path
from urllib.parse import urlsplit
import json,re
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent/'preview_bridge_local'
def read(p):
    try:return json.loads(p.read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return {}
def current():
    n=read(ROOT.parent.parent/'progress'/'now.json')
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
