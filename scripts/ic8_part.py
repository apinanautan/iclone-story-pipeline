"""ic8_part.py - build ONE part (ท่อน) from ONE spec file, in a fixed order. The AI only fills the spec.

  python scripts/ic8_part.py parts/<spec>.json <step> [--from] [--approved]

Steps (in order; `all` = check..ready, never render):
  audio   wav length + silences (cut points / speech windows) -> parts/<spec>.audio.txt   (no iClone)
  check   validate the spec against the rules (no iClone). Must say OK before anything else runs.
  open    open `project` if it exists, else open `from` and Save As `project` (GUI)
  cast    every name in cast/hide exists in the scene
  pose    place + motion + Look front/Look At + face + hide  (ic8_pose_place.py)
  sound   delete old Project Sound, import wav at frame 0 (GUI)
  lip     AccuLips per speaker (GUI), keep only that speaker's line windows; non-speakers' mouths cleared
  cams    Cam_A/Cam_B, 2 keys per shot, switcher, still per shot -> ic8_jobs/part_cams.jpg (look at it!)
  ready   Switch, playhead 0, play range 0..end, GUI save, reopen  -> STOP: user presses Play
  render  ONLY with --approved (user said ผ่าน): 1080p60 + clean wav + checks + publish
`<step> --from` runs that step and every later one up to ready (fix a number in the spec, re-run from there).

Spec (parts/<story>_<N>.json):
{
 "story": "รักลำเอียง", "part": "11",
 "wav": "C:/.../ท่อน11.wav",
 "from": "E:/ไฟล์งาน/ไฟล์ Save/นิทาน/รักลำเอียง/ท่อน10.iProject",   # scene to continue from
 "project": "E:/ไฟล์งาน/ไฟล์ Save/นิทาน/รักลำเอียง/ท่อน11.iProject",
 "video": "E:/Video/รักลำเอียง/11.mp4",
 "publish": "G:/ไดรฟ์ของฉัน/รักลำเอียง (นิทาน 3D)/วีดีโอ/บีม",         # optional
 "scene": "โรงพยาบาล",                                                # name in the story file -> spots/cams/room
 "lines": [ {"who": "สุดา", "t": [0.53, 19.18], "text": "..."},        # who = avatar name or "บรรยาย"
            {"who": "บรรยาย", "t": [19.6, 30.0]} ],
 "cast": { "นายสมหวัง": {"spot": "เตียง_นั่งพิงหัวเตียง", "lookfront": true},   # spot = numbers from the story file
           "สุดา": {"pos": [-342,733,0], "yaw": 140, "motions": ["G:/.../X.iMotion"], "speed": 0.25,
                    "lookfront": true, "lookat": "นายสมหวัง", "face": {"Mouth_Smile_L": 0.3}} },
 "hide": ["วารี"],
 "shots": [ {"t": [0, 9.0], "cam": "two_สุดา_แม่"},                     # cam = numbers from the story file
            {"t": [9.0, 15], "pos": [x,y,z], "target": [x,y,z], "focal": 40, "move": 15}, ... ]
}
"""
import json, os, re, subprocess, sys, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(ROOT, "scripts")
GUI = os.path.join(SCR, "ic8_gui.ps1")
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
FF = r"C:\Users\Apinan\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin\ffmpeg.exe"
FFP = FF.replace("ffmpeg.exe", "ffprobe.exe")
NARR = ("บรรยาย", "narrator")
ORDER = ["check", "open", "cast", "pose", "sound", "lip", "cams", "ready"]


def say(s): print(s, flush=True)
def fail(s): say("FAIL: " + s); sys.exit(1)


def gui(*a):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUI] + [str(x) for x in a])
    if r.returncode: fail("ic8_gui.ps1 %s" % a[0])


def job(code, name):
    p = os.path.join(J, "run", name + ".py")
    with open(p, "w", encoding="utf-8") as f: f.write(code)
    gui("job", p)


def pyjob(body):
    return ("import RLPy,os,json\nJ=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')\n"
            "T=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))\n" + body + "\n")


def wjson(name, obj):
    with open(os.path.join(J, name), "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False)


def rlog(name):
    p = os.path.join(J, name)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


# ---------- audio ----------
def duration(wav):
    out = subprocess.run([FFP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 2)


def silences(wav, db=-35, d=0.3):
    err = subprocess.run([FF, "-hide_banner", "-i", wav, "-af", "silencedetect=noise=%ddB:d=%s" % (db, d), "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return [(round(a, 2), round(en[i], 2) if i < len(en) else None) for i, a in enumerate(st)]


def step_audio(S, base):
    end = duration(S["wav"]); sil = silences(S["wav"])
    rows = ["wav %s" % S["wav"], "length %.2f s" % end, "silences (cut shots / start+end of speech here):"]
    rows += ["  %6.2f - %s" % (a, "%6.2f" % b if b else "end") for a, b in sil]
    speech, cur = [], 0.0
    for a, b in sil:
        if a - cur > 0.15: speech.append((cur, a))
        cur = b or end
    if end - cur > 0.15: speech.append((cur, end))
    rows += ["speech chunks (give each one a `who` in lines):"] + ["  %6.2f - %6.2f" % x for x in speech]
    open(base + ".audio.txt", "w", encoding="utf-8").write("\n".join(rows))
    say("\n".join(rows)); say("OK audio -> " + base + ".audio.txt")


# ---------- names -> numbers from the story file (stories/<story>.json > scenes > <scene>) ----------
def resolve(S, spec):
    """cast {"spot": "<name>"} and shots {"cam": "<name>"} take their numbers from the scene in the story file.
    Numbers written in the part spec win (fine-tune per part)."""
    S["_scene"] = {}; S["_prev_cams"] = set()
    st = os.path.join(ROOT, "stories", "%s.json" % S.get("story", ""))
    if not os.path.exists(st) or not S.get("scene"): return
    story = json.load(open(st, encoding="utf-8"))
    sc = story.get("scenes", {}).get(S["scene"])
    if sc is None: fail("scene %s not in %s" % (S["scene"], st))
    S["_scene"] = sc
    for n, c in S["cast"].items():
        if c.get("spot"):
            sp = sc.get("spots", {}).get(c["spot"])
            if sp is None: fail("%s: spot %s not in scene %s (add it to the story file)" % (n, c["spot"], S["scene"]))
            for k, v in sp.items():
                if k not in ("notes", "approved") and k not in c: c[k] = v
    for i, s in enumerate(S["shots"]):
        if s.get("cam"):
            cp = sc.get("cams", {}).get(s["cam"])
            if cp is None: fail("shot %d: cam %s not in scene %s" % (i + 1, s["cam"], S["scene"]))
            for k, v in cp.items():
                if k not in ("notes", "approved") and k not in s: s[k] = v
    # previous part's camera names (rule: angles must not repeat the previous part)
    ns = [P["n"] for P in story.get("parts", [])]
    if str(S.get("part")) in ns and ns.index(str(S["part"])) > 0:
        prev = os.path.join(os.path.dirname(spec), "%s_%s.json" % (S["story"], ns[ns.index(str(S["part"])) - 1]))
        if os.path.exists(prev):
            S["_prev_cams"] = {x.get("cam") for x in json.load(open(prev, encoding="utf-8")).get("shots", []) if x.get("cam")}


def scene_checks(S, errs, warns):
    sc = S["_scene"]
    if not sc: return
    for n in sc.get("notes_list", []): say("SCENE RULE: " + n)
    room = sc.get("room") or sc.get("area")   # [xmin, ymin, xmax, ymax]: indoor = walls, outdoor = where the action is
    # solid things from the scan (houses, trees, cars, beds). Skip ground/sky/terrain (huge) and tiny props.
    solid = {n: o for n, o in sc.get("objects", {}).items()
             if 30 < o["max"][0] - o["min"][0] < 4000 and 30 < o["max"][1] - o["min"][1] < 4000 and o["max"][2] - o["min"][2] > 30}
    inside = lambda p, o: all(o["min"][k] <= p[k] <= o["max"][k] for k in range(3))
    for i, s in enumerate(S["shots"]):
        for n, o in solid.items():
            if inside(s["pos"], o): errs.append("shot %d camera is INSIDE %s" % (i + 1, n)); break
        else:
            for n, o in solid.items():   # line of sight camera -> target (target itself may sit in a bed/chair: stop at 85%)
                if any(inside([s["pos"][k] + (s["target"][k] - s["pos"][k]) * f / 20 for k in range(3)], o) for f in range(1, 18)):
                    warns.append("shot %d view may be blocked by %s (look at the still)" % (i + 1, n)); break
        x, y = s["pos"][:2]
        if room and not (room[0] + 10 <= x <= room[2] - 10 and room[1] + 10 <= y <= room[3] - 10):
            errs.append("shot %d camera (%d,%d) outside the room/area %s" % (i + 1, x, y, room))
        if s.get("cam") and s["cam"] in S["_prev_cams"]:
            warns.append("shot %d uses cam %s like the previous part (rule 8: new angles)" % (i + 1, s["cam"]))
        if s.get("cam") and not sc.get("cams", {}).get(s["cam"], {}).get("approved"):
            warns.append("shot %d cam %s not approved by the user yet (show a still first)" % (i + 1, s["cam"]))
    used = {}
    for n, c in S["cast"].items():
        if c.get("spot"):
            if c["spot"] in used: errs.append("%s and %s both on spot %s" % (used[c["spot"]], n, c["spot"]))
            used[c["spot"]] = n
            if not sc.get("spots", {}).get(c["spot"], {}).get("approved"):
                warns.append("%s spot %s not approved by the user yet (show a still first)" % (n, c["spot"]))
        if room and c.get("pos") and not (room[0] <= c["pos"][0] <= room[2] and room[1] <= c["pos"][1] <= room[3]):
            errs.append("%s at %s is outside the room/area" % (n, c["pos"][:2]))


# ---------- check (all rules that can be checked on paper) ----------
def step_check(S, base):
    errs, warns = [], []
    for k in ("wav", "from", "project", "video", "lines", "cast", "shots"):
        if k not in S: errs.append("missing key: " + k)
    if errs: fail("; ".join(errs))
    if not os.path.exists(S["wav"]): errs.append("wav not found: " + S["wav"])
    for k in ("project", "video"):
        if re.match(r"^[Gg]:", S[k]): errs.append("%s on G: (never write to G: except publish)" % k)
    if not os.path.exists(S["project"]) and not os.path.exists(S["from"]): errs.append("neither project nor from exists")
    if errs: fail("; ".join(errs))
    end = duration(S["wav"]); sil = silences(S["wav"])
    names = set(S["cast"])
    for n in S.get("hide", []):
        if n in names: errs.append("%s is both cast and hide" % n)
    for i, L in enumerate(S["lines"]):
        a, b = L["t"]
        if not (0 <= a < b <= end + 0.05): errs.append("line %d time %s outside 0..%.2f" % (i + 1, L["t"], end))
        if L["who"] not in NARR and L["who"] not in names: errs.append("line %d speaker %s not in cast" % (i + 1, L["who"]))
    for n, c in S["cast"].items():
        sp = c.get("speed")
        if sp is not None and not (0.15 <= sp <= 0.30): errs.append("%s speed %.2f not 0.15-0.30" % (n, sp))
        for m in c.get("motions", []) + ([c["motion"]] if c.get("motion") else []):
            if not os.path.exists(m): errs.append("%s motion not found: %s" % (n, m))
        if c.get("lookat") and c["lookat"] not in names: errs.append("%s looks at %s (not in cast)" % (n, c["lookat"]))
        speaks = any(L["who"] == n for L in S["lines"])
        if not speaks and not c.get("lookat"): warns.append("%s listens: no lookat (rule 6: listeners Look At someone)" % n)
        if not c.get("lookfront"): warns.append("%s: no lookfront (rule 6: head should move)" % n)
        if not (c.get("motions") or c.get("motion")): warns.append("%s: no motion (keeps the motion already in the scene)" % n)
    sh = S["shots"]
    if not sh: errs.append("no shots")
    else:
        if abs(sh[0]["t"][0]) > 0.01: errs.append("first shot must start at 0")
        if abs(sh[-1]["t"][1] - end) > 0.1: errs.append("last shot ends %.2f, wav is %.2f" % (sh[-1]["t"][1], end))
    for i, s in enumerate(sh):
        a, b = s["t"]
        if b - a < 2.0: errs.append("shot %d shorter than 2 s" % (i + 1))
        if i and abs(sh[i - 1]["t"][1] - a) > 0.01: errs.append("gap/overlap before shot %d" % (i + 1))
        if not 20 <= s["focal"] <= 200: errs.append("shot %d focal %s (20-200)" % (i + 1, s["focal"]))
        mv = abs(s.get("move", 15))
        if not 8 <= mv <= 25: warns.append("shot %d move %d cm (guide: 12-20)" % (i + 1, mv))
        if math.dist(s["pos"], s["target"]) < 60: errs.append("shot %d camera closer than 60 cm to target" % (i + 1))
        talk = [L["who"] for L in S["lines"] if L["who"] not in NARR and L["t"][0] + 0.2 < a < L["t"][1] - 0.2]
        if i and talk and not any(x - 0.3 <= a <= (y or end) + 0.3 for x, y in sil):
            warns.append("shot %d cut at %.2f is in the middle of %s's line (rule 9: cut in pauses)" % (i + 1, a, talk[0]))
    for i in range(1, len(sh)):
        if sh[i]["pos"] == sh[i - 1]["pos"] and sh[i]["target"] == sh[i - 1]["target"]:
            errs.append("shot %d repeats shot %d" % (i + 1, i))
    scene_checks(S, errs, warns)
    for w in warns: say("WARN: " + w)
    if errs: fail("\n  ".join([""] + errs))
    say("OK check: %.2f s, %d lines, %d cast, %d shots" % (end, len(S["lines"]), len(names), len(sh)))


# ---------- iClone steps ----------
def title():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "[Console]::OutputEncoding=[Text.Encoding]::UTF8;(Get-Process iClone -EA 0|select -First 1).MainWindowTitle"],
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip()


def step_open(S, base):
    proj = os.path.normpath(S["project"]); t = title()
    if not t: fail("iClone is not running")
    if t.endswith(os.path.basename(proj)): say("OK already open: " + t); return
    if t.endswith("*"): fail("current project has unsaved changes (%s): save or ask the user first" % t)
    if os.path.exists(proj): gui("open", proj)
    else:
        gui("open", os.path.normpath(S["from"])); gui("saveas", proj)
    say("OK open " + proj)


def step_cast(S, base):
    job(pyjob("open(os.path.join(J,'part_cast.txt'),'w',encoding='utf-8').write('\\n'.join(a.GetName() for a in RLPy.RScene.GetAvatars()))"), "zz_part_cast")
    have = set(open(os.path.join(J, "part_cast.txt"), encoding="utf-8").read().split("\n"))
    need = set(S["cast"]) | set(S.get("hide", []))
    say("scene avatars: " + ", ".join(sorted(have)))
    miss = need - have
    if miss: fail("not in scene: %s (load them: Tidmunz / ic8_cast.py, name them exactly)" % ", ".join(miss))
    extra = have - need
    if extra: say("WARN: in scene but not in spec (visible? add to hide): " + ", ".join(sorted(extra)))
    say("OK cast")


def step_pose(S, base):
    end = duration(S["wav"]); av = {}
    for n, c in S["cast"].items():
        av[n] = dict(c); av[n].setdefault("visible", [[0, 1]])
    for n in S.get("hide", []): av[n] = {"visible": [[0, 0]]}
    wjson("pose_place.json", {"end": end, "avatars": av})
    job(open(os.path.join(SCR, "ic8_pose_place.py"), encoding="utf-8").read(), "zz_part_pose")
    log = rlog("pose_place.log.txt"); say(log)
    if "ERROR" in log or "DONE" not in log: fail("pose")
    say("OK pose (look: gui shot)")


def step_sound(S, base):
    gui("sound", os.path.normpath(S["wav"]), "-Replace"); gui("save"); say("OK sound (check ic8_jobs/gui_tl.png: Sound row at frame 0)")


def windows(S):
    w = {n: [] for n in S["cast"]}
    for L in S["lines"]:
        if L["who"] in w: w[L["who"]].append(list(L["t"]))
    return w


def step_lip(S, base):
    w = windows(S); wav = os.path.normpath(S["wav"])
    for n, ws in w.items():
        if ws: gui("lip", n, wav, ws[0][0], ws[-1][1])
    job(pyjob("os.environ['LIPWIN']=%r\nexec(open(r'%s',encoding='utf-8').read())" % (json.dumps(w, ensure_ascii=False), os.path.join(SCR, "ic8_lip_trim.py"))), "zz_part_lip")
    say(rlog("lip_trim.txt"))
    job(open(os.path.join(SCR, "ic8_lip_check.py"), encoding="utf-8").read(), "zz_part_lipcheck")
    chk = rlog("lip_check.txt"); say(chk)
    for n, ws in w.items():
        m = re.search(r"^%s visemes (\d+)" % re.escape(n), chk, re.M)
        if ws and (not m or int(m.group(1)) == 0): fail("%s speaks but has no visemes" % n)
    gui("save"); say("OK lip")


def step_cams(S, base):
    end = duration(S["wav"])
    wjson("cams.json", {"end": end, "edges": True, "shots": S["shots"]})
    job(open(os.path.join(SCR, "ic8_cams.py"), encoding="utf-8").read(), "zz_part_cams")
    log = rlog("cams.log.txt"); say(log)
    if "ERROR" in log or "DONE" not in log: fail("cams")
    n = len(S["shots"]); cols = min(n, 4); rows = (n + cols - 1) // cols
    subprocess.run([FF, "-v", "error", "-y", "-start_number", "1", "-i", os.path.join(J, "cam_%02d_mid.png"), "-frames:v", "1",
                    "-vf", "scale=480:-1,tile=%dx%d" % (cols, rows), os.path.join(J, "part_cams.jpg")])
    say("OK cams -> %s (LOOK: faces 3/4, speaker visible, no bed/clipping, nobody cut by the frame edge)" % os.path.join(J, "part_cams.jpg"))


def step_ready(S, base):
    gui("switch"); gui("tozero"); gui("save"); gui("reopen")
    say("OK ready. STOP: tell the user to press Play in iClone (Switch, frame 0). Render only after they say ผ่าน.")


def step_render(S, base, approved):
    if not approved: fail("render needs --approved (the user must say ผ่าน first)")
    end = duration(S["wav"]); mids = ",".join("%.2f" % ((s["t"][0] + s["t"][1]) / 2) for s in S["shots"])
    a = ["render", os.path.normpath(S["video"]), end, os.path.normpath(S["wav"]), "-Shots", mids]
    if S.get("publish"): a += ["-Publish", os.path.normpath(S["publish"])]
    gui(*a)


STEPS = {"audio": step_audio, "check": step_check, "open": step_open, "cast": step_cast, "pose": step_pose,
         "sound": step_sound, "lip": step_lip, "cams": step_cams, "ready": step_ready}

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    spec, step = sys.argv[1], sys.argv[2]
    S = json.load(open(spec, encoding="utf-8")); base = os.path.splitext(spec)[0]
    resolve(S, spec)
    if step == "render": step_render(S, base, "--approved" in sys.argv); sys.exit(0)
    if step == "all": run = ORDER
    elif step in STEPS: run = ORDER[ORDER.index(step):] if "--from" in sys.argv and step in ORDER else [step]
    else: fail("unknown step " + step)
    if run and run[0] != "check" and step != "audio": step_check(S, base)   # never act on a broken spec
    for s in run:
        say("===== %s =====" % s); STEPS[s](S, base)
