"""Preview dispatch guard. Prevent accidental out-of-flow calls; not an OS sandbox."""
import contextlib
import ctypes
import json
import os
import secrets
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEASE = ROOT / "progress" / "preview_lease.json"
LOCK = ROOT / "progress" / "preview_dispatch.lock"

class Blocked(RuntimeError):
    pass

@contextlib.contextmanager
def dispatch(lock=None):
    # OS releases byte-range lock when process exits, even after crash.
    import msvcrt
    lock=Path(lock) if lock is not None else LOCK
    lock.parent.mkdir(parents=True, exist_ok=True)
    with open(lock, "a+b") as f:
        f.seek(0, 2)
        if f.tell() == 0:
            f.write(b"0"); f.flush()
        f.seek(0)
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as e:
            raise Blocked("Preview is already running a step") from e
        try:
            yield
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)

@contextlib.contextmanager
def permit(story, part, step, spec):
    token = secrets.token_hex(32)
    d = dict(token=token, pid=os.getpid(), story=story, part=str(part),
             step=step, spec=str(Path(spec).resolve()), time=time.time())
    tmp = LEASE.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, LEASE)
    try:
        yield dict(os.environ, AIICLONE_PREVIEW_TOKEN=token)
    finally:
        try:
            if json.loads(LEASE.read_text(encoding="utf-8")).get("token") == token:
                LEASE.unlink()
        except (OSError, ValueError):
            pass

def require(spec, step, args):
    try:
        d = json.loads(LEASE.read_text(encoding="utf-8"))
        token = os.environ.get("AIICLONE_PREVIEW_TOKEN", "")
        if not token or not secrets.compare_digest(token, d["token"]):
            raise Blocked("no Preview dispatch permit")
        if d["pid"] != os.getppid():
            raise Blocked("not launched by Preview controller")
        if d["spec"] != str(Path(spec).resolve()) or d["step"] != step:
            raise Blocked("wrong part or step")
        if any(x not in ("--approved",) for x in args) or ("--approved" in args) != (step == "render"):
            raise Blocked("step override is not allowed")
        return d
    except (OSError, ValueError, KeyError) as e:
        raise Blocked("no active Preview dispatch") from e


def process_alive(pid):
    """True/False/None; unknown is never permission to release a running job."""
    if not isinstance(pid,int) or pid<=0:return None
    from ctypes import wintypes
    k=ctypes.WinDLL("kernel32",use_last_error=True)
    k.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD)
    k.OpenProcess.restype=wintypes.HANDLE
    k.GetExitCodeProcess.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD))
    k.CloseHandle.argtypes=(wintypes.HANDLE,)
    h=k.OpenProcess(0x1000,False,pid)
    if not h:return False if ctypes.get_last_error()==87 else None
    try:
        code=wintypes.DWORD()
        if not k.GetExitCodeProcess(h,ctypes.byref(code)):return None
        return code.value==259
    finally:k.CloseHandle(h)


def worker_absent(owner):
    """Conservative check: orphaned child or native watcher queue means wait."""
    import subprocess
    run=Path(os.environ["LOCALAPPDATA"])/"Tidmunz Studio"/"snapgen_data"/"ic8_jobs"/"run"
    if not run.is_dir() or any(run.glob("*.py")):return False
    cmd=(
        "$ErrorActionPreference='Stop';"
        "$p=@(Get-CimInstance Win32_Process | Where-Object {"
        "$_.ProcessId -ne $PID -and ($_.ParentProcessId -eq "+str(int(owner))+
        " -or ($_.Name -match '^(python|py|powershell|Ai-iclone).*\\.exe$' -and "
        "$_.CommandLine -match 'ic8_part\\.py|ic8_gui\\.ps1|ai_iclone\\.py'))});"
        "if($p.Count){'BUSY'}else{'IDLE'}"
    )
    try:
        p=subprocess.run(["powershell","-NoProfile","-NonInteractive","-Command",cmd],
                         capture_output=True,text=True,timeout=8)
        return p.returncode==0 and p.stdout.strip()=="IDLE"
    except (OSError,subprocess.SubprocessError):return False


def reconcile_orphaned_run(root=ROOT):
    """Recover only a dead-owner running record under the existing dispatch lock.
    Never infer completion, change step receipts, delete jobs, or alter the scene.
    """
    root=Path(root);progress=root/"progress";now=progress/"now.json";lease=progress/"preview_lease.json"
    def read(p):
        try:return json.loads(p.read_text(encoding="utf-8-sig"))
        except (OSError,ValueError):return {}
    n=read(now)
    if n.get("state")!="running":return n
    try:
        with dispatch(progress/"preview_dispatch.lock"):
            n=read(now);l=read(lease)
            if n.get("state")!="running":return n
            owner=n.get("pid")
            if l:
                if any(str(l.get(k))!=str(n.get(k)) for k in ("story","part","step")):return n
                owner=l.get("pid")
            if process_alive(owner) is not False or not worker_absent(owner):return n
            # Preserve the evidence; atomically publish failed, not done.
            out=dict(n,state="failed",interrupted=True,reason="Preview owner exited; no active worker or native job",time=time.time())
            tmp=now.with_suffix(".recover.tmp");tmp.write_text(json.dumps(out,ensure_ascii=False),encoding="utf-8");os.replace(tmp,now)
            if l and read(lease)==l:
                # The stale lease has no authority; archive without exposing its token.
                lease.unlink()
            try:
                with open(progress/"now_log.txt","a",encoding="utf-8") as f:
                    f.write(time.strftime("%H:%M:%S")+" RECOVERY: dead Preview owner; step marked failed; completed steps preserved\\n")
            except OSError:pass
            return out
    except (Blocked,OSError,ValueError):return read(now)
