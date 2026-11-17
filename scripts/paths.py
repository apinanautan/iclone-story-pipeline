r"""paths.py - never hardcode a drive letter (user 2026-11-17: drives differ per PC).

Write library/story paths in specs and skills with placeholders:
  {MOTION}  = the motion library folder (has motions.csv + "Digital Soul 100+")
  {DRIVE}   = the Google Drive "My Drive" folder (ไดรฟ์ของฉัน / My Drive) with the story folders (READ ONLY)
  {SAVE}    = where .iProject parts are saved (here E:\ไฟล์งาน\ไฟล์ Save\นิทาน; new PC: Documents\iClone Story Save)
  {VIDEO}   = rendered videos (here E:\Video; new PC: Videos\iClone Story)
  {DESKTOP} = this user's Desktop (cut audio: {DESKTOP}\<story>\เสียงที่ตัดแล้ว)
Resolution order per name: env var IC_<NAME>  ->  paths.local.json (repo root, not in git)  ->  auto-search
all drive letters once, then saved to paths.local.json.

  python scripts/paths.py              # print/find all roots
  python scripts/paths.py "{MOTION}\\Stand00.iMotion"   # expand one path
In code:  from paths import expand, root;  expand(spec_dict_or_str)
"""
import json, os, string, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL = os.path.join(HERE, "paths.local.json")
REL = {   # likely places under a drive root; checked first, then a shallow search
    "MOTION": [r"คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น", r"Other computers\My Computer\โมชั่น", "โมชั่น", "Motion"],
    "DRIVE": ["ไดรฟ์ของฉัน", "My Drive"],
    "SAVE": [r"ไฟล์งาน\ไฟล์ Save\นิทาน"],     # where .iProject files are saved
    "VIDEO": ["Video"],                           # rendered mp4 per story
    "DESKTOP": [],                                # this user's Desktop (cut audio goes here)
}
FALLBACK = {   # output folders that may not exist on a new PC: created under the user's profile
    "SAVE": os.path.join(os.path.expanduser("~"), "Documents", "iClone Story Save"),
    "VIDEO": os.path.join(os.path.expanduser("~"), "Videos", "iClone Story"),
    "DESKTOP": os.path.join(os.path.expanduser("~"), "Desktop"),
}
def _ok(name, p):
    if name == "MOTION": return os.path.isdir(os.path.join(p, "Digital Soul 100+"))
    if name in ("SAVE", "VIDEO", "DESKTOP"): return os.path.isdir(p)
    if name == "DRIVE": return os.path.isdir(p) and os.path.basename(p.rstrip("\\/")) in ("ไดรฟ์ของฉัน", "My Drive")
    return os.path.isdir(p)

def _drives():
    return [d + ":\\" for d in string.ascii_uppercase if os.path.isdir(d + ":\\")]

def _search(name):
    for d in _drives():
        for r in REL.get(name, []):
            p = os.path.join(d, r)
            if _ok(name, p): return p
    for d in _drives():                       # shallow search (2 levels) for the marker
        try:
            for a in os.scandir(d):
                if not a.is_dir(): continue
                if _ok(name, a.path): return a.path
                try:
                    for b in os.scandir(a.path):
                        if b.is_dir() and _ok(name, b.path): return b.path
                except OSError: pass
        except OSError: pass
    return None

_cache = None
def root(name):
    global _cache
    if os.environ.get("IC_" + name): return os.environ["IC_" + name]
    if _cache is None:
        try: _cache = json.load(open(LOCAL, encoding="utf-8"))
        except (OSError, ValueError): _cache = {}
    p = _cache.get(name)
    if p and _ok(name, p): return p
    p = FALLBACK["DESKTOP"] if name == "DESKTOP" else _search(name)
    if not p and name in FALLBACK: p = FALLBACK[name]; os.makedirs(p, exist_ok=True)
    if not p: raise SystemExit("paths.py: cannot find {%s} on any drive. Set env IC_%s or put it in %s" % (name, name, LOCAL))
    _cache[name] = p
    json.dump(_cache, open(LOCAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return p

def expand(x):
    """Replace {MOTION}/{DRIVE} in a str, or in every str inside dicts/lists."""
    if isinstance(x, str):
        for n in REL:
            if "{%s}" % n in x: x = x.replace("{%s}" % n, root(n))
        return os.path.normpath(x) if "{" not in x and (":" in x[:3]) else x
    if isinstance(x, list): return [expand(v) for v in x]
    if isinstance(x, dict): return {k: expand(v) for k, v in x.items()}
    return x

if __name__ == "__main__":
    if len(sys.argv) > 1: print(expand(sys.argv[1]))
    else:
        for n in REL: print("{%s} = %s" % (n, root(n)))
