"""Persistent repair counts: evidence, never pretend a failure is a pass."""
import json,time
from pathlib import Path

def record(prog, story, part, stage, items):
    """items = {stable_id: {"state": "pass|fail|pending", "detail": ...}}."""
    path=Path(prog)/f"{story}_{part}_repair_queue.json"
    try: doc=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError): doc={}
    stages=doc.setdefault("stages",{})
    old=stages.get(stage,{})
    total=len(items)
    passed=sum(v["state"]=="pass" for v in items.values())
    failed=sum(v["state"]=="fail" for v in items.values())
    row=dict(total=total,passed=passed,remaining=total-passed,failed=failed,pending=total-passed-failed,items=items)
    history=old.get("history",[])
    snap={k:row[k] for k in ("total","passed","remaining","failed","pending")}
    if not history or any(history[-1].get(k)!=v for k,v in snap.items()):
        history=(history+[dict(snap,time=time.time())])[-100:]
    row["history"]=history
    stages[stage]=row
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(path)
    return row

def line(stage,row):
    return f"{stage}: เหลือ {row['remaining']}/{row['total']} | ผ่าน {row['passed']} | ต้องแก้ {row['failed']} | รอตรวจ {row['pending']}"

def lines(prog,story,part):
    try: doc=json.loads((Path(prog)/f"{story}_{part}_repair_queue.json").read_text(encoding="utf-8"))
    except (OSError,ValueError): return []
    return [line(k,v) for k,v in doc.get("stages",{}).items()]


# --- no-progress guard (user 2026-11-28: a repair must count down 5,4,3,2,1, never loop) ---
def _doc(prog, story, part):
    path=Path(prog)/f"{story}_{part}_repair_queue.json"
    try: return path,json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError): return path,{}

def _save(path, doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(path)

def method_sig(spec, scripts):
    """What the next try would run: the spec text + every pipeline script (name, size, mtime)."""
    import hashlib
    h=hashlib.sha1()
    try: h.update(Path(spec).read_bytes())
    except OSError: pass
    for f in sorted(Path(scripts).glob("*")):
        if f.suffix in (".py",".ps1") and f.is_file():
            st=f.stat(); h.update(f"{f.name}{st.st_size}{st.st_mtime_ns}".encode())
    return h.hexdigest()[:12]

def remaining(prog, story, part, stage):
    _,doc=_doc(prog,story,part)
    row=doc.get("stages",{}).get(stage)
    return row.get("remaining") if row else None

def note_fail(prog, story, part, stage, method, reason):
    path,doc=_doc(prog,story,part)
    att=doc.setdefault("attempts",{}).setdefault(stage,[])
    att.append(dict(remaining=remaining(prog,story,part,stage),method=method,reason=(reason or "")[:200],time=time.time()))
    doc["attempts"][stage]=att[-20:]
    _save(path,doc)

def clear_attempts(prog, story, part, stage):
    path,doc=_doc(prog,story,part)
    if doc.get("attempts",{}).pop(stage,None) is not None: _save(path,doc)

def stuck(prog, story, part, stage, method, limit=2):
    """Why another try would only loop, or None. Stuck = the last `limit` failed tries had this same
    method and the same failure, and what is left did not go down. A changed spec/script or a
    smaller remaining count lets the next try run."""
    _,doc=_doc(prog,story,part)
    att=doc.get("attempts",{}).get(stage,[])[-limit:]
    if len(att)<limit or any(a.get("method")!=method for a in att): return None
    if len({a.get("reason") for a in att})>1: return None
    left=[a.get("remaining") for a in att]
    if None not in left and left[-1]<left[0]: return None
    now=remaining(prog,story,part,stage)
    if now is not None and left[-1] is not None and now<left[-1]: return None
    return "%s ไม่ลดลง %d รอบติด (เหลือ %s) วิธีเดิม อาการเดิม: %s" % (stage,limit,left[-1] if left[-1] is not None else "ทั้งขั้น",att[-1].get("reason") or "?")

def clear_stage(prog, story, part, stage):
    """A dependency was redone (e.g. new sound/pose): old passes of this stage are no longer evidence."""
    path,doc=_doc(prog,story,part)
    if doc.get("stages",{}).pop(stage,None) is not None: _save(path,doc)
