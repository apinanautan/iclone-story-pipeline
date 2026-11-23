r"""video2motion.py - a video clip of ONE person -> an iClone motion FBX on the CC3_Base_Plus body. Local, light (CPU).
(user 2026-11-23: "AI video to motion that is not heavy on the PC")

  Ai-iclone video2motion <clip.mp4> [name] [--allow-install]

Steps (no iClone): MediaPipe Pose (CPU) -> .bvh (scripts/video_to_bvh.py) -> Blender (background) -> CC_Base skeleton
(tools/motion_ai/bvh2blend.py + retarget.py NOSWING_SPINE=1) -> <clip folder>\<name>_motion\:
  <name>_CC.fbx + .fbxkey + .3dxProfile (keep the 3 together) = drag into iClone, Convert All
  <name>.bvh, <name>_check.mp4 (clip + skeleton | the BVH replayed: LOOK at it)
Best clips: whole body with space below the feet, angled 20 deg (not side view), plain background, 16:9, static camera.
One-time setup: a Python 3.9-3.12 venv with mediapipe in %LOCALAPPDATA%\Ai-iclone-tools\mocap (~150 MB download):
only with --allow-install (ask the user once).
"""
import glob, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.environ.get("AI_ICLONE_MOCAP") or os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ai-iclone-tools", "mocap")
VPY = os.path.join(TOOLS, "Scripts", "python.exe")
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def say(s): print(s, flush=True)


def base_python():
    """a Python 3.9-3.12 that really runs (mediapipe 0.10.21 has no wheels for 3.13+)."""
    try: lines = subprocess.run(["py", "-0p"], capture_output=True, text=True, timeout=30).stdout.splitlines()
    except Exception: lines = []
    exes = [l.split()[-1] for l in lines if l.strip().lower().endswith("python.exe")]
    for exe in exes:
        if not os.path.isfile(exe): continue
        try:
            v = subprocess.run([exe, "-c", "import sys;print(sys.version_info[1])"], capture_output=True, text=True, timeout=30)
            if v.returncode == 0 and 9 <= int(v.stdout.strip()) <= 12: return exe
        except Exception: pass
    return None


def ensure_venv():
    ok = os.path.isfile(VPY) and subprocess.run([VPY, "-c", "import mediapipe"], capture_output=True, timeout=120).returncode == 0
    if ok: return
    if "--allow-install" not in sys.argv:
        say("STOP: video2motion needs a one-time setup (MediaPipe, ~150 MB download into %s).\n"
            "Ask the user once, then run again with --allow-install." % TOOLS); sys.exit(2)
    py = base_python()
    if not py: sys.exit("FAIL: needs Python 3.9-3.12 on this PC (3.13+ has no MediaPipe). Tell the user: install Python 3.11 from python.org.")
    say("SETUP venv with %s -> %s" % (py, TOOLS))
    subprocess.run([py, "-m", "venv", TOOLS], check=True, timeout=600)
    subprocess.run([VPY, "-m", "pip", "install", "-q", "mediapipe==0.10.21"], check=True, timeout=1800)


def blender():
    c = []
    for pf in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", "")):
        c += glob.glob(os.path.join(pf, "Blender Foundation", "Blender*", "blender.exe"))
    c += glob.glob(os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Steam", "steamapps", "common", "Blender", "blender.exe"))
    ver = lambda p: [int(x) for x in re.findall(r"\d+", os.path.basename(os.path.dirname(p)))] or [0]
    return max(c, key=ver) if c else None


def cc_base():
    """CC3_Base_Plus.fbx exported from Character Creator (with .fbxkey + .3dxProfile next to it)."""
    if os.environ.get("CC_BASE_FBX") and os.path.isfile(os.environ["CC_BASE_FBX"]): return os.environ["CC_BASE_FBX"]
    docs = os.path.join(os.environ.get("USERPROFILE", ""), "Documents")
    for f in glob.glob(os.path.join(docs, "Reallusion", "**", "CC3_Base_Plus.fbx"), recursive=True):
        if os.path.isfile(f[:-4] + ".3dxProfile") and os.path.isfile(f[:-4] + ".fbxkey"): return f
    return None


def run(cmd, env=None, limit=900):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", env=env, timeout=limit, creationflags=NOWIN)
    keep = [l for l in (r.stdout + r.stderr).splitlines() if re.match(r"(BVH|CHECK|arm |BONES|BAKED|EXPORTED)", l)
            or "Error" in l or "Traceback" in l]
    for l in keep: say("  " + l)
    if r.returncode: sys.exit("FAIL: %s (exit %d)" % (os.path.basename(cmd[-3] if len(cmd) > 3 else cmd[0]), r.returncode))
    return r.stdout


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a: print(__doc__); return 1
    clip = os.path.abspath(a[0])
    if not os.path.isfile(clip): sys.exit("FAIL: no clip " + clip)
    name = a[1] if len(a) > 1 else os.path.splitext(os.path.basename(clip))[0]
    B, CC = blender(), cc_base()
    if not B: sys.exit("FAIL: Blender is not installed (needs Blender 4+ from blender.org).")
    if not CC: sys.exit("FAIL: no CC3_Base_Plus.fbx (+ .fbxkey + .3dxProfile) under Documents\\Reallusion. Tell the user: in Character "
                        "Creator export the CC3_Base_Plus character to FBX once (or set CC_BASE_FBX).")
    ensure_venv()
    out = os.path.join(os.path.dirname(clip), name + "_motion"); os.makedirs(out, exist_ok=True)
    bvh, chk, fbx = os.path.join(out, name + ".bvh"), os.path.join(out, name + "_check.mp4"), os.path.join(out, name + "_CC.fbx")
    import tempfile
    blend = os.path.join(tempfile.mkdtemp(), "src.blend")
    say("1/3 pose from the clip (CPU) ...")
    run([VPY, os.path.join(ROOT, "scripts", "video_to_bvh.py"), clip, bvh, chk])
    frames = int(re.search(r"Frames:\s*(\d+)", open(bvh).read()).group(1))
    say("2/3 BVH -> Blender ...")
    run([B, "-b", "--factory-startup", "--python", os.path.join(ROOT, "tools", "motion_ai", "bvh2blend.py"), "--", bvh, blend])
    say("3/3 onto the CC3_Base_Plus skeleton ...")
    env = dict(os.environ, NOSWING_SPINE="1", LAST=str(frames), CC_BASE_FBX=CC)
    run([B, "-b", "--factory-startup", "--python", os.path.join(ROOT, "tools", "motion_ai", "retarget.py"), "--", blend, fbx], env=env)
    say("OK video2motion: %s\n  iClone: drag %s in (keep its .fbxkey + .3dxProfile next to it), Convert All, save as iMotion.\n"
        "  LOOK at %s first (left = clip + skeleton, right = the motion)." % (out, os.path.basename(fbx), os.path.basename(chk)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
