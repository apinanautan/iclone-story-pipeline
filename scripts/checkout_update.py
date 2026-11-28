"""Opt-in managed release updates inside a working Git checkout.

Git metadata, work data and local-only edits are not replaced. Merge changed
upstream files only when clean; a conflict stops the whole installation.
"""
import datetime,io,json,os,re,shutil,subprocess,tempfile,time,zipfile
from pathlib import Path,PurePosixPath
TAG=re.compile(r"v(\d+)\.(\d+)\.(\d+)")
PROTECTED={"stories","parts","progress",".git"}
LOCAL={"paths.local.json","docs/prompt_release.local.json","tools/chrome_preview_bridge/relay.key","tools/chrome_preview_bridge/config.local.js"}
def version(tag):
    m=TAG.fullmatch(tag)
    if not m:raise ValueError("Expected stable release tag, got "+str(tag))
    return tuple(map(int,m.groups()))
def read(p):
    try:return json.loads(p.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:return {}
def archive(blob):
    result={};seen=set();top=None
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for f in z.infolist():
            if f.is_dir():continue
            p=PurePosixPath(f.filename)
            if p.is_absolute() or len(p.parts)<2 or any(x in ("..",".") or ":" in x or "\\" in x for x in p.parts):raise ValueError("unsafe release path")
            if top is None:top=p.parts[0]
            if top!=p.parts[0]:raise ValueError("multiple archive roots")
            rel="/".join(p.parts[1:])
            if rel.lower() in seen:raise ValueError("duplicate release path")
            seen.add(rel.lower())
            if p.parts[1].lower() in PROTECTED or rel.lower() in LOCAL or rel.startswith("tools/preview_bridge_local/"):continue
            result[rel]=z.read(f)
    if "VERSION" not in result or "scripts/ai_iclone.py" not in result:raise ValueError("invalid release archive")
    return result
def eq(a,b):
    if a==b:return True
    if a is None or b is None:return False
    try:return a.decode("utf-8").replace("\r\n","\n")==b.decode("utf-8").replace("\r\n","\n")
    except UnicodeDecodeError:return False
def merge(local,old,new):
    if eq(local,new):return local
    if eq(local,old):return new
    if eq(old,new):return local
    if any(x is None for x in (local,old,new)):raise ValueError("added/deleted file conflicts")
    try:local.decode("utf-8");old.decode("utf-8");new.decode("utf-8")
    except UnicodeDecodeError:raise ValueError("binary conflict")
    git=shutil.which("git") or str(Path(os.environ.get("ProgramFiles","C:/Program Files"))/"Git/cmd/git.exe")
    with tempfile.TemporaryDirectory() as td:
        paths=[Path(td)/n for n in ("local","base","new")]
        for p,b in zip(paths,(local,old,new)):p.write_bytes(b.replace(b"\r\n",b"\n"))
        a=subprocess.run([git,"merge-file","-p",*map(str,paths)],capture_output=True)
        if a.returncode:raise ValueError("merge conflict")
        return a.stdout
def plan(root,old,new):
    changes={};conflicts=[]
    for n in sorted(set(old)|set(new)):
        if n=="VERSION" or eq(old.get(n),new.get(n)):continue
        p=root/n
        if not p.resolve().is_relative_to(root.resolve()):raise ValueError("path outside installation: "+n)
        a=p.read_bytes() if p.is_file() else None
        try:b=merge(a,old.get(n),new.get(n))
        except (ValueError,OSError) as e:conflicts.append(n+" ("+str(e)+")");continue
        if a!=b:changes[n]=b
    if conflicts:raise ValueError("local changes conflict; no files installed: "+"; ".join(conflicts[:12]))
    changes["VERSION"]=new["VERSION"]
    return changes
def busy(root):
    n=read(root/"progress/now.json")
    j=read(root/"tools/preview_bridge_local/job.json")
    return n.get("state")=="running" or j.get("state") in ("pending","claimed","needs_review")
def apply(root,changes,tag):
    marker="progress/managed_release.json"
    # Version last. Back up every changed or removed program file.
    v=changes.pop("VERSION");changes[marker]=json.dumps({"tag":tag}).encode();changes["VERSION"]=v
    backup=root/"progress/release_backups"/datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup.mkdir(parents=True,exist_ok=False)
    applied=[]
    try:
        for n,b in changes.items():
            p=root/n;old=backup/n;had=p.exists()
            if had:old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,old)
            applied.append((p,old,had))
            p.parent.mkdir(parents=True,exist_ok=True)
            if b is None:p.unlink();continue
            tmp=p.with_name(p.name+".release-tmp");tmp.write_bytes(b)
            try:os.replace(tmp,p)
            except PermissionError:
                if p.suffix.lower()!=".exe":raise
                os.replace(p,p.with_name(p.name+".old"));os.replace(tmp,p)
    except BaseException:
        for p,old,had in reversed(applied):
            if had:shutil.copy2(old,p)
            else:p.unlink(missing_ok=True)
            p.with_name(p.name+".release-tmp").unlink(missing_ok=True)
        raise
    return backup
def check_managed(root,get,repo,force,say):
    stamp=root/"progress/update_check.txt"
    try:
        if busy(root):
            if force:say("Ai-iclone: active Preview; update deferred, no work changed")
            return None
        if not force and stamp.exists() and time.time()-stamp.stat().st_mtime<600:return None
        state=read(root/"progress/managed_release.json");oldtag=state["tag"]
        cur=(root/"VERSION").read_text(encoding="utf-8").strip()
        if version(oldtag)!=version("v"+cur):raise ValueError("managed release baseline does not match VERSION")
        tag=json.loads(get("https://api.github.com/repos/"+repo+"/releases/latest"))["tag_name"]
        stamp.write_text("latest "+tag,encoding="utf-8")
        if version(tag)<=version(oldtag):
            if force:say("Ai-iclone: managed checkout up to date ("+cur+")")
            return None
        url="https://codeload.github.com/"+repo+"/zip/refs/tags/"
        old=archive(get(url+oldtag,120));new=archive(get(url+tag,120))
        if old["VERSION"].decode().strip()!=cur or version("v"+new["VERSION"].decode().strip())!=version(tag):raise ValueError("release VERSION mismatch")
        from preview_gate import dispatch
        with dispatch():
            if busy(root) or read(root/"progress/managed_release.json")!=state:raise RuntimeError("Preview or release state changed")
            changes=plan(root,old,new);backup=apply(root,changes,tag)
        say("Ai-iclone: installed "+tag+"; local edits retained; backup "+str(backup))
        return tag
    except Exception as e:
        say("Ai-iclone: managed update deferred: "+str(e))
        return None
