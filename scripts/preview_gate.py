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
def dispatch():
    # OS releases byte-range lock when process exits, even after crash.
    import msvcrt
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "a+b") as f:
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
