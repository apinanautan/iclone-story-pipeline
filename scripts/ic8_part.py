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
  cams    Cam_A/Cam_B, 2 keys per shot, switcher, 1 still per shot (quick; --shot 3,5 re-shoots only those, --full = ~1/s) -> ic8_jobs/part_cams.jpg (look at it!)
  cam_check ALL shots in ONE image (part_cams_all.jpg) + the AI fills progress/<story>_<N>_camcheck.json per shot; any fail = FAIL
  ready   Switch, playhead 0, play range 0..end, manual File-menu save/reopen -> STOP: user presses Play
  render  ONLY with --approved (user said ผ่าน): 1080p60 + clean wav + checks + publish
`<step> --from` runs that step and every later one up to ready (fix a number in the spec, re-run from there).

Spec (parts/<story>_<N>.json):
{
 "story": "รักลำเอียง", "part": "11",
 "wav": "C:/.../ท่อน11.wav",
 "from": "{SAVE}/รักลำเอียง/ท่อน10.iProject",   # scene to continue from
 "project": "{SAVE}/รักลำเอียง/ท่อน11.iProject",
 "video": "{VIDEO}/รักลำเอียง/11.mp4",
 "publish": "{DRIVE}/รักลำเอียง (นิทาน 3D)/วีดีโอ/บีม",         # optional
 "scene": "โรงพยาบาล",                                                # name in the story file -> spots/cams/room
 "lines": [ {"who": "สุดา", "t": [0.53, 19.18], "text": "..."},        # who = avatar name or "บรรยาย"
            {"who": "บรรยาย", "t": [19.6, 30.0]} ],
 "cast": { "นายสมหวัง": {"spot": "เตียง_นั่งพิงหัวเตียง", "lookfront": true},   # spot = numbers from the story file
           "สุดา": {"pos": [-342,733,0], "yaw": 140, "motions": ["{MOTION}/.../X.iMotion"], "speed": 0.8,
                    "lookfront": true, "lookat": "นายสมหวัง", "face": {"Mouth_Smile_L": 0.3}} },
 "hide": ["วารี"],
 "shots": [ {"t": [0, 9.0], "cam": "two_สุดา_แม่"},                     # cam = numbers from the story file
            {"t": [9.0, 15], "pos": [x,y,z], "target": [x,y,z], "focal": 40, "move": 15}, ... ]
}
"""
import time
import json, os, re, subprocess, sys, math
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import expand, root   # {MOTION} / {DRIVE} placeholders: never hardcode a drive letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(ROOT, "scripts")
GUI = os.path.join(SCR, "ic8_gui.ps1")
J = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs")
from paths import ffmpeg as _ff
FF, FFP = _ff("ffmpeg"), _ff("ffprobe")   # found on any PC (no one-PC path)
os.environ["IC8_FF"], os.environ["IC8_FFP"] = FF, FFP   # ic8_gui.ps1 uses the same ones
NARR = ("บรรยาย", "narrator")
# "all" stops after switch: the user checks the stills; ready (save) and render come only after ผ่าน
ORDER = ["check", "motion_plan", "open", "cast", "sound", "pose", "lip", "scene_review", "prop_review", "camera_replan", "cams", "cam_check", "motion_check", "light_check", "face_check", "editorial_review", "switch"]


import ailog   # real % + timing + fail report for GPT (user 2026-11-23)
def say(s): ailog.log(s)   # also progress/now_log.txt (clock, +seconds in the step) for the Preview program
def fail(s):
    say("FAIL: " + s)
    print(ailog.fail_report(s), flush=True)   # step, time, iClone dialogs' text, screenshot, last log -> progress/last_fail.txt
    sys.exit(1)


def ensure_watch():
    """Start scripts/ic8_watch.ps1 once (answers iClone popups by rule from scripts/ic8_dialogs.json; user 2026-11-21)."""
    pf = os.path.join(J, "dialogs", "watch.pid")
    try:
        pid = int(open(pf).read().strip())
        if str(pid) in subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True, text=True).stdout: return
    except Exception: pass
    os.makedirs(os.path.dirname(pf), exist_ok=True)
    p = subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File",
                          os.path.join(os.path.dirname(os.path.abspath(__file__)), "ic8_watch.ps1")],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0))
    open(pf, "w").write(str(p.pid))


def gui(*a):
    ensure_watch()
    # Hard time limit (user 2026-11-21: 13 min stuck behind a Yes/No/Cancel box). Save ~20 s, open of a 4 GB
    # project ~2 min: anything longer is a dialog nobody answered -> stop at once and say which one.
    # render runs as long as the video needs (the ps1 itself waits for the output file), so it gets 1 h
    limits = {"render": 3600, "open": 300, "reopen": 300, "saveas": 300, "sound": 300, "lip": 300,
              "job": 320}  # The PowerShell job helper waits up to 300 s for the iClone watcher.
    lim = limits.get(a[0], 120)
    what = "%s %s" % (a[0], os.path.basename(str(a[1])) if len(a) > 1 else "")
    if "iClone.exe" not in subprocess.run(["tasklist", "/FI", "IMAGENAME eq iClone.exe", "/NH"], capture_output=True, text=True).stdout:
        fail("iClone is not running (open iClone 8 first, then run again): %s not started" % what)
    ailog.log("รอ iClone: %s (หยุดเองถ้าเกิน %d วินาที)" % (what, lim), count=False)
    p = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUI] + [str(x) for x in a])
    t0 = time.time(); nxt = 10
    try:
        while p.poll() is None:
            el = time.time() - t0
            if el > lim: raise subprocess.TimeoutExpired(GUI, lim)
            try: lv = json.load(open(os.path.join(J, "live.json"), encoding="utf-8"))
            except Exception: lv = {}
            if time.time() - lv.get("time", 0) > 5 and a[0] != "render":   # no real % from the job itself: say what we wait for
                ailog.wait(ailog.T0["step"] or a[0], "รอ iClone %s %.0f/%d วินาที" % (what, el, lim))
            if el >= nxt:
                wt = ailog.screen(); nxt += 10   # fresh read every 10 s (loading % on screen), picture deleted at once
                ailog.log("ยังรอ iClone: %s %.0f วินาที (สูงสุด %d) | หน้าจอ: %s" % (what, el, lim, wt[:300]), count=False)
                m = re.findall(r"(\d{1,3})\s*%", wt)
                if m: live(ailog.T0["step"] or a[0], int(m[-1]), "iClone บอก %s%% (%s)" % (m[-1], what))
            time.sleep(1)
        r = p
        ailog.op("iClone %s" % what); ailog.log("iClone เสร็จ: %s ใน %.0f วินาที" % (what, time.time() - t0), count=False)
    except subprocess.TimeoutExpired:
        p.kill()
        fail("iClone did not finish %s in %d s: stopped (see the iClone windows' text below)" % (what, lim))
    if r.returncode: fail("ic8_gui.ps1 %s failed (exit %d) after %.0f s" % (what, r.returncode, time.time() - t0))


def job(code, name):
    # Stage source outside watched run/: otherwise the iClone timer may rename it before GUI reads it.
    os.makedirs(os.path.join(J, "staging"), exist_ok=True)
    p = os.path.join(J, "staging", name + ".py")
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
    story = expand(json.load(open(st, encoding="utf-8")))
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
def story_gate(S):
    """User 2026-11-22: stage 1 (story setup, once per story) MUST be finished before ANY per-part step.
    Same 8 checks as Preview tab 1 (progress_app.story_states): central sheet in git, script + master audio,
    teacher's range confirmed by the USER (never guessed), parts cover exactly that range, characters, scenes,
    every part planned, user approved the story plan. Any step of any part refuses to run until all are green."""
    from progress_app import story_states, STORY_STEPS
    ss = story_states(S["story"])
    bad = ["%s (%s)" % (label, ss[k][1] or ss[k][0]) for k, label in STORY_STEPS if ss[k][0] != "done"]
    if bad:
        fail("story setup (Preview tab 1) is not finished - do it first, parts come after:" + "".join(chr(10) + "  - " + b for b in bad))
    st = json.load(open(os.path.join(ROOT, "stories", S["story"] + ".json"), encoding="utf-8"))
    tr = st.get("teacher_range") or [0, 0]
    p = next((p for p in st.get("parts", []) if str(p.get("n")) == str(S["part"])), None)
    if not p: fail("story setup: part %s is not in the central sheet stories/%s.json" % (S["part"], S["story"]))
    if p.get("master") and p["master"][0] >= tr[1] - 0.5:
        fail("story setup: part %s starts at %.1fs, after the teacher's range end %.1fs" % (S["part"], p["master"][0], tr[1]))


def step_check(S, base):
    errs, warns = [], []
    for k in ("wav", "from", "project", "video", "lines", "cast", "shots"):
        if k not in S: errs.append("missing key: " + k)
    if errs: fail("; ".join(errs))
    if not os.path.exists(S["wav"]): errs.append("wav not found: " + S["wav"])
    for k in ("project", "video"):
        if os.path.normcase(os.path.abspath(S[k])).startswith(os.path.normcase(root("DRIVE"))):
            errs.append("%s inside the shared Drive {DRIVE} (never write there except publish)" % k)
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
    if S.get("lines") and S.get("shots"):   # editor rules (user 2026-11-19): no new shot in the silent tail, no tiny shots
        last = max(L["t"][1] for L in S["lines"])
        for i, sh in enumerate(S["shots"]):
            a, b = sh["t"]
            if a >= last - 0.2: errs.append("shot %d starts at %.1f after the last line (%.1f): hold the previous shot to the end" % (i + 1, a, last))
            if b - a < 2.5: errs.append("shot %d only %.1f s long" % (i + 1, b - a))
        if len(S["shots"]) > 1:   # user 2026-11-19: last shot < 6 s -> don't cut, hold the previous shot to the end
            a, b = S["shots"][-1]["t"]
            if b - a < 6: errs.append("last shot only %.1f s (< 6): delete it and hold shot %d to the part end" % (b - a, len(S["shots"]) - 1))
    for n, c in S["cast"].items():
        sp = c.get("speed")
        if sp is not None and not (0.65 <= sp <= 1.0): errs.append("%s speed %.2f not 0.65-1.0 (slower = judder)" % (n, sp))
        for m in c.get("motions", []) + ([c["motion"]] if c.get("motion") else []):
            if not os.path.exists(m): errs.append("%s motion not found: %s" % (n, m))
        if isinstance(c.get("lookfront"), str) and not os.path.exists(c["lookfront"]): errs.append("%s face clip not found: %s" % (n, c["lookfront"]))
        if c.get("lookat") and c["lookat"] not in names: errs.append("%s looks at %s (not in cast)" % (n, c["lookat"]))
        speaks = any(L["who"] == n for L in S["lines"])
        if not speaks and not c.get("lookat") and not c.get("work"): warns.append("%s listens: no lookat (rule 6: listeners Look At someone)" % n)
        if not (c.get("faces") or c.get("lookfront")): warns.append("%s: no face motion - set \"faces\": [Digital Soul .iTalk ...] (user 2026-11-22: every character)" % n)
        if face_desc(c).startswith("⚠"): warns.append("%s: blank face - set smile (0-1) or an emotion .iTalk in lookfront (user 2026-11-21)" % n)
        if str(c.get("blink", "Normal")) == "None": warns.append("%s: blink None - every character blinks (user 2026-11-22)" % n)
        if (c.get("motions") or c.get("motion")) and c.get("speed", 1.0) > 0.8: warns.append("%s: speed %.2f - folk tale = slow, use 0.65-0.7 (user 2026-11-21)" % (n, c.get("speed", 1.0)))
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
        if s.get("coverage") in ("establishing","action","two_shot","insert"):
            if not 24 <= s["focal"] <= 150 or not s.get("story_beat"): errs.append("shot %d: narrative coverage needs lens 24-150 and story_beat" % (i+1))
        elif s.get("wide"):   # establishing/view shot: any lens, no DOF
            if not 20 <= s["focal"] <= 200: errs.append("shot %d focal %s (20-200)" % (i + 1, s["focal"]))
        elif not 75 <= s["focal"] <= 150: errs.append("shot %d character focal must be 75-150 mm" % (i + 1))
        d = math.dist(s["pos"], s["target"]); h = d * 24 / s["focal"]   # cm of body visible top-to-bottom
        if s.get("coverage") in ("establishing","action","two_shot","insert"): pass
        elif s.get("wide"):   # user hates full bodies: a view shot must not frame any cast member
            hx = math.atan(18 / s["focal"])
            for n, c in S["cast"].items():
                if not c.get("pos"): continue
                # An establishing house-only shot may hide the cast until its end.
                # Check actual visibility at the mid-point, not the cast inventory.
                shown = True
                for visible_t, visible_flag in c.get("visible", []):
                    if float(visible_t) <= (float(s["t"][0]) + float(s["t"][1])) / 2:
                        shown = bool(visible_flag)
                    else:
                        break
                if not shown:
                    continue
                v = [c["pos"][k] + (150 if k == 2 else 0) - s["pos"][k] for k in range(3)]
                f = [s["target"][k] - s["pos"][k] for k in range(3)]
                cos = sum(a * b for a, b in zip(v, f)) / (math.hypot(*v) * math.hypot(*f) or 1)
                if cos > math.cos(hx * 1.1):
                    errs.append("shot %d is wide and shows %s full body: aim view shots away from the cast (rules: no full body)" % (i + 1, n)); break
        elif h > 100:
            errs.append("shot %d frames %d cm of body (> 100 = knees/full body). Chest-up: distance <= %d cm at %d mm" % (i + 1, h, 100 * s["focal"] / 24, s["focal"]))
        # user 2026-11-21: every shot drifts slowly start->end (in or out), never static, never a fast whoosh
        # user 2026-11-22: move is TIME based (ic8_cams.move_cm): rate %/s of distance, total 6-20%
        rate = 100.0 * s.get("move_rate", 0.015)
        if s.get("move_fixed"):
            rate = 100.0 * abs(s.get("move", 15)) / max(1.0, math.dist(s["pos"], s["target"])) / max(0.1, b - a)
        if rate < 1.0: errs.append("shot %d camera moves %.2f%%/s of distance: looks static (want ~1.5%%/s)" % (i + 1, rate))
        elif rate > 2.5: warns.append("shot %d camera moves %.2f%%/s of distance: may look fast (want ~1.5%%/s)" % (i + 1, rate))
        if math.dist(s["pos"], s["target"]) < 60: errs.append("shot %d camera closer than 60 cm to target" % (i + 1))
        talk = [L["who"] for L in S["lines"] if L["who"] not in NARR and L["t"][0] + 0.2 < a < L["t"][1] - 0.2]
        if i and talk and not any(x - 0.3 <= a <= (y or end) + 0.3 for x, y in sil):
            warns.append("shot %d cut at %.2f is in the middle of %s's line (rule 9: cut in pauses)" % (i + 1, a, talk[0]))
    if sum(1 for s in sh if s.get("wide")) > 1: errs.append("more than 1 wide shot in a part")
    for i in range(1, len(sh)):
        if sh[i]["pos"] == sh[i - 1]["pos"] and sh[i]["target"] == sh[i - 1]["target"]:
            errs.append("shot %d repeats shot %d" % (i + 1, i))
    scene_checks(S, errs, warns)
    motion_variety(S, errs, warns)
    warns += think_warns(S)
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
    if os.path.isfile(proj) and t.rstrip(" *").endswith(os.path.basename(proj)): say("OK already open: " + t); return
    # Saving is deliberately a live menu action, never a script/helper action.
    if os.path.exists(proj): gui("open", proj)
    else:
        gui("open", os.path.normpath(S["from"]))
        say("AI WORK: create the new project through iClone File > Save Project As manually, then run Ai-iclone do again: " + proj)
        sys.exit(3)
    say("OK open " + proj)

def step_cast(S, base):
    """Load missing story avatars in iClone via watcher, one avatar per job, then verify names."""
    st = os.path.join(ROOT, "stories", S["story"] + ".json")
    story = expand(json.load(open(st, encoding="utf-8")))
    job(pyjob("open(os.path.join(J,'part_cast.txt'),'w',encoding='utf-8').write('\\n'.join(a.GetName() for a in RLPy.RScene.GetAvatars()))"), "zz_part_cast")
    have = set(open(os.path.join(J, "part_cast.txt"), encoding="utf-8").read().split("\n"))
    need = set(S["cast"]) | set(S.get("hide", []))
    todo = sorted(need - have)
    for i, n in enumerate(todo):
        live("cast", 100.0 * i / len(todo), "โหลด %s (%d/%d)" % (n, i + 1, len(todo)))
        path = story.get("characters", {}).get(n, {}).get("avatar")
        if not path or not os.path.exists(path): fail("avatar source missing for " + n)
        body = ("RLPy.RScene.ClearSelectObjects()\n"
                "before={a.GetID() for a in RLPy.RScene.GetAvatars()}\n"
                "res=RLPy.RFileIO.LoadFile(%r)\n" % path +
                "new=[a for a in RLPy.RScene.GetAvatars() if a.GetID() not in before]\n"
                "assert len(new)==1, 'load avatar count='+str(len(new))\n"
                "new[0].SetName(%r)\n" % n +
                "open(os.path.join(J,'cast_loaded.txt'),'w',encoding='utf-8').write(new[0].GetName())")
        job(pyjob(body), "zz_cast_load")
        if rlog("cast_loaded.txt") != n: fail("cast load not verified for " + n)
        have.add(n); say("OK loaded " + n)
    extra = have - need
    if extra: say("WARN unexpected avatars: " + ", ".join(sorted(extra)))
    say("OK cast " + ", ".join(sorted(need)))
    step_props(S)


def step_props(S):
    """spec "props": {name: {"fbx": path (glb2fbx.py output), "pos": [x,y,z], "yaw": deg}} (user 2026-11-22, TV in
    part 4). Loads a prop once (Import Settings -> watcher presses Convert All), then always re-keys its place."""
    P = S.get("props") or {}
    if not P: return
    for n, c in P.items():
        if not os.path.exists(c["fbx"]): fail("prop file missing: " + c["fbx"])
        x, y, z = c["pos"]; yaw = float(c.get("yaw", 0))
        body = ("import math\nhave=[p for p in RLPy.RScene.GetProps() if p.GetName()==%r]\n" % n +
                "if not have:\n"
                " before={p.GetID() for p in RLPy.RScene.GetProps()}\n"
                " RLPy.RFileIO.LoadFile(%r)\n" % c["fbx"] +
                " new=[p for p in RLPy.RScene.GetProps() if p.GetID() not in before]\n"
                " assert new, 'prop load gave nothing'\n"
                " for i,p in enumerate(new): p.SetName(%r if i==0 else %r+'_'+str(i))\n" % (n, n) +
                " have=new\n"
                "for p in have:\n"
                " ctl=p.GetControl('Transform'); ctl.ClearKeys(); tr=RLPy.RTransform(); ctl.GetValue(T(0),tr)\n"
                " tr.T().x=%r; tr.T().y=%r; tr.T().z=%r\n" % (float(x), float(y), float(z)) +
                " q=RLPy.RQuaternion(); q.FromAxisAngle(RLPy.RVector3(0,0,1), math.radians(%r))\n" % yaw +
                " tr.R().x,tr.R().y,tr.R().z,tr.R().w=q.x,q.y,q.z,q.w\n"
                # glb2fbx.py writes metres; iClone reads them as cm -> 1/100 size without this
                " tr.S().x=tr.S().y=tr.S().z=%r; ctl.SetValue(T(0),tr)\n" % float(c.get("scale", 100)) +
                "open(os.path.join(J,'prop_loaded.txt'),'w',encoding='utf-8').write(','.join(p.GetName() for p in have))")
        job(pyjob(body), "zz_prop_" + str(abs(hash(n)) % 10000))
        got = rlog("prop_loaded.txt")
        if n not in got.split(","): fail("prop not verified: %s (%s)" % (n, got))
        say("OK prop %s at %s yaw %s" % (got, c["pos"], yaw))


def live(step, pct, text): ailog.live(step, pct, text)
def count(step, i, n, text): ailog.count(step, i, n, text)   # live.json (Preview %) + a log line every 10 %


def face_desc(c):
    """Preview line "หน้า" (user 2026-11-22): the 3-part face flow of one character, in order:
    1 auto blink, 2 face motion (.iTalk clips, chained, 65-75%), 3 feeling (smile / think / face keys)."""
    fl = c.get("faces") or ([c["lookfront"]] if isinstance(c.get("lookfront"), str) else ["Look front"] if c.get("lookfront") else [])
    mot = " → ".join(os.path.splitext(os.path.basename(f))[0] for f in fl)
    feel = []
    if c.get("smile"): feel.append("ยิ้มค่อยๆขึ้น 10→%d%%" % round(100 * min(0.8, c["smile"])))
    if c.get("think"): feel.append("หน้าคิด" + ("" if c["think"] is True else " " + ", ".join("%.0f-%.0fs" % tuple(r) for r in think_rng(c["think"], 0))))
    if c.get("face"): feel.append("face keys")
    warn = ("" if fl else "⚠ ไม่มีท่าหน้า ") + ("" if feel else "⚠ ไม่มีความรู้สึก ")
    return "%s① กระพริบ %s ② ท่าหน้า %s (%.0f%%) ③ ความรู้สึก %s" % (
        warn, c.get("blink", "Normal"), mot or "-", 100 * max(0.65, min(0.75, float(c.get("face_speed", 0.7)))), " + ".join(feel) or "-")


STANDY = re.compile(r"stand|idle|tki|breath|listen|response|talk", re.I)   # standing / idle clips (not work motions)
CROSSED = re.compile(r"arms[ _]?crossed|mographmotion[\/]02_female[\/](stand03|standtki)\.imotion$", re.I)   # arms folded


def clip_key(m):   # same clip whatever the drive / placeholder: last folder + file name
    return "/".join(m.replace("\\", "/").split("/")[-2:]).lower()


def motions_of(c):
    return c.get("motions", []) + ([c["motion"]] if c.get("motion") else [])


def on_screen(c, end):   # seconds this character is visible in the part
    vis = sorted(c.get("visible") or [[0, 1]]); tot = 0.0
    for i, (t0, on) in enumerate(vis):
        if on: tot += max(0.0, (vis[i + 1][0] if i + 1 < len(vis) else end) - t0)
    return tot


def motion_variety(S, errs, warns):
    """User 2026-11-22: "ยืนกอดอกเกือบทั้งเรื่อง น่าเบื่อ เหมือนคนไม่มีสมองทำ". The same calm standing clip
    (MographMotion 02_Female/Stand03) was used 7 times over 4 parts. Standing clips must vary:
    - 2 characters in one part never share a standing clip;
    - one standing clip in at most 2 parts of the whole story (`Ai-iclone motions --write` picks from the whole library);
    - arms folded: at most 1 character per part, only when the line calls for it;
    - a character standing the whole part (> 40 s) on 1 clip gets a WARN: chain 2-3 different calm clips."""
    import glob
    end = S["lines"][-1]["t"][1] if S.get("lines") else 0
    used = {}
    for n, c in S["cast"].items():
        st = [m for m in motions_of(c) if STANDY.search(os.path.basename(m))]
        for k in {clip_key(m) for m in st}:
            used.setdefault(k, []).append(n)
        if st and len({clip_key(m) for m in motions_of(c)}) < 2 and on_screen(c, end) > 20:
            errs.append("%s is on screen %.0f s with one motion (%s): list 2-3 DIFFERENT clips - the pose changes at camera cuts, max 20 s each (user 2026-11-22)" % (n, on_screen(c, end), os.path.basename(st[0])))
    for k, who in used.items():
        if len(who) > 1: errs.append("%s share the standing clip %s: give each a different one (user 2026-11-22)" % (", ".join(who), k))
    crossed = [n for n, c in S["cast"].items() if any(CROSSED.search(m.replace("\\", "/")) for m in motions_of(c))]
    if len(crossed) > 1: errs.append("arms folded on %s: at most 1 character per part (user 2026-11-22)" % ", ".join(crossed))
    other = {}
    for f in glob.glob(os.path.join(ROOT, "parts", "%s_*.json" % S["story"])):
        part = os.path.basename(f)[len(S["story"]) + 1:-5]
        if part == str(S["part"]) or not part.isdigit(): continue
        try: spec = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError): continue
        for c in spec.get("cast", {}).values():
            for m in motions_of(c):
                if STANDY.search(os.path.basename(m)): other.setdefault(clip_key(m), set()).add(part)
    for k in used:
        if len(other.get(k, ())) >= 2:
            errs.append("standing clip %s already in parts %s of this story: run `Ai-iclone motions --write` (picks from the whole library, user 2026-11-23)" % (k, ", ".join(sorted(other[k], key=int))))


WALKY = re.compile(r"walk|run|jog|chore|pick|weed|wander|turn|step|enter|exit|leave|approach", re.I)


def step_motion_plan(S, base):
    """Who gets which motion, at what speed (user 2026-11-21: show it before pose). Missing file = FAIL;
    names that sound like root motion (walking) = WARN (they walk forward then snap back)."""
    plan = []; bad = []
    for n, c in S["cast"].items():
        fd = face_desc(c)
        ms = c.get("motions") or ([c["motion"]] if c.get("motion") else [])
        for m in ms:
            nm = os.path.splitext(os.path.basename(m))[0]
            ok = os.path.exists(expand(m))
            warn = bool(WALKY.search(nm))
            plan.append({"who": n, "motion": nm, "speed": c.get("speed", 1.0), "ok": ok, "warn": warn or fd.startswith("⚠"), "face": fd})
            say("  %s <- %s x%.2f  face: %s%s%s" % (n, nm, c.get("speed", 1.0), fd, "" if ok else "  MISSING FILE", "  WARN walking motion?" if warn else ""))
            if not ok: bad.append("%s (%s)" % (n, nm))
        if not ms: plan.append({"who": n, "motion": "(ไม่มีท่า)", "speed": 0, "ok": True, "warn": True}); say("  %s <- no motion" % n)
    with open(os.path.join(ROOT, "progress", "%s_%s_motions.json" % (S["story"], S["part"])), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    if bad: fail("motion_plan: motion file missing for " + ", ".join(bad))
    say("OK motion_plan: %d cast, %d motions" % (len(S["cast"]), len(plan)))


def wait_textures(limit=300):
    """User 2026-11-21: motions put on (or a render started) while textures are still loading hang iClone or
    render white, untextured people. Read the viewport label "Texture Loading: N" with OCR
    (ic8_watch.ps1 -Textures) until it is gone 3 reads in a row; fail after `limit` s (never render blind)."""
    W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ic8_watch.ps1")
    t0 = time.time(); zero = 0; n = "?"
    while time.time() - t0 < limit and zero < 3:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUI, "shot"], capture_output=True, timeout=60)  # iClone in front, so OCR sees it
        out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", W, "-Textures"], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"TEXLOAD (\d+)", out or ""); n = m.group(1) if m else "?"
        zero = zero + 1 if n == "0" else 0
        if zero < 3: time.sleep(2)
    if zero < 3: fail("textures still loading after %d s (Texture Loading: %s) - look at the screen" % (limit, n))
    say("textures loaded (OCR: no 'Texture Loading') after %d s" % (time.time() - t0))


def step_pose(S, base):
    live("pose", 0, "รอเท็กซ์เจอร์โหลดเสร็จ")
    wait_textures()
    end = duration(S["wav"]); av = {}
    for n, c in S["cast"].items():
        av[n] = dict(c); av[n].setdefault("visible", [[0, 1]])
        if av[n].get("lookfront") is True: av[n]["lookfront"] = expand(os.path.join("{MOTION}", "Digital Soul 100+", "1.Watch", "Look front.iTalk"))
    for n in S.get("hide", []): av[n] = {"visible": [[0, 0]]}
    wjson("pose_place.json", {"end": end, "avatars": av, "cuts": [sh["t"][0] for sh in S["shots"][1:]]})
    job(open(os.path.join(SCR, "ic8_pose_place.py"), encoding="utf-8").read(), "zz_part_pose")
    open(os.path.join(J, "pose.done"), "w").write(time.strftime("%H:%M:%S"))   # lip must run AFTER this (face clips cover the mouth)
    log = rlog("pose_place.log.txt"); say(log)
    if "ERROR" in log or "DONE" not in log: fail("pose")
    noblink = [n for n in S["cast"] if not re.search(r"^%s blink " % re.escape(n), log, re.M)]
    if noblink: fail("pose: no auto blink for " + ", ".join(noblink))   # user 2026-11-22: blink went missing
    # user 2026-11-22 (said many times): clips APART with a small gap, the transition fills the gap - never butted
    bad_gap = [l for l in re.findall(r"^.* gap (-?[\d.]+).*$", log, re.M) if not 0.3 <= float(l) <= 2.0]
    if bad_gap: fail("pose: clip gap not 0.3-2.0 s (clips touching/overlapping): " + ", ".join(bad_gap[:5]))
    if not re.search(r" gap [\d.]+", log): fail("pose: no clip gap logged - clips are butted together")
    noface = [n for n in S["cast"] if not re.search(r"^%s face .* speed 0\.(6[5-9]|7[0-5])" % re.escape(n), log, re.M)]
    if noface: fail("pose: no face motion clips (65-75%) for " + ", ".join(noface))
    say("OK pose (look: gui shot)")


def step_sound(S, base):
    live("sound", 0, "ใส่เสียง"); gui("sound", os.path.normpath(S["wav"]), "-Replace")
    live("sound", 100, "เสร็จ")
    say("OK sound (check ic8_jobs/gui_tl.png: Sound row at frame 0). Keep Project Sound unchanged; save only at the ready gate.")

def windows(S):
    w = {n: [] for n in S["cast"]}
    for L in S["lines"]:
        if L["who"] in w: w[L["who"]].append(list(L["t"]))
    return w


def step_lip(S, base):
    w = windows(S); wav = os.path.normpath(S["wav"])
    talk = [n for n, ws in w.items() if ws]; tot = len(talk) + 2   # each talker + trim + check
    for i, n in enumerate(talk):
        count("lip", i, tot, "ปาก %s" % n); gui("lip", n, wav, w[n][0][0], w[n][-1][1])
    count("lip", len(talk), tot, "ตัดปากให้ตรงช่วงพูด")
    job(pyjob("os.environ['LIPWIN']=%r\nexec(open(r'%s',encoding='utf-8').read())" % (json.dumps(w, ensure_ascii=False), os.path.join(SCR, "ic8_lip_trim.py"))), "zz_part_lip")
    say(rlog("lip_trim.txt"))
    job(open(os.path.join(SCR, "ic8_lip_check.py"), encoding="utf-8").read(), "zz_part_lipcheck")
    count("lip", len(talk) + 1, tot, "ตรวจปาก"); chk = rlog("lip_check.txt"); say(chk)
    for n, ws in w.items():
        m = re.search(r"^%s visemes (\d+)" % re.escape(n), chk, re.M)
        if ws and (not m or int(m.group(1)) == 0): fail("%s speaks but has no visemes" % n)
    open(os.path.join(J, "lip.done"), "w").write(time.strftime("%H:%M:%S"))
    count("lip", tot, tot, "เสร็จ")
    say("OK lip. Save only at the ready gate.")

def cams_args():
    """cams [--shot 3,5] [--full]: default quick pass = 1 still (middle) per shot; --shot re-shoots only those
    shots (user 2026-11-21: fix one camera at a time, shots already OK stay done); --full = ~1 still/s."""
    only = []
    if "--shot" in sys.argv:
        only = [int(x) for x in sys.argv[sys.argv.index("--shot") + 1].split(",") if x.strip()]
    return only, ("--full" in sys.argv)


def step_cams(S, base):
    from cinematic_qa import require_replan,capture_cams
    if not require_replan(S,Path(ROOT)): fail("camera replan missing or stale; repair camera_replan")
    end = duration(S["wav"])
    only, full = cams_args()
    rate = max(1,S.get("review_per_sec", 1)) # both modes: actual samples across each shot
    wjson("cams.json", {"end": end, "per_sec": rate, "only": only, "shots": S["shots"],
                        "face_light_multiplier": S.get("face_light_multiplier", 0.04),
                        "face_light_overrides": S.get("face_light_overrides", {}),
                        "face_light_source": S.get("face_light_source")})
    job(open(os.path.join(SCR, "ic8_cams.py"), encoding="utf-8").read(), "zz_part_cams")
    log = rlog("cams.log.txt"); say(log)
    if "ERROR" in log or "DONE" not in log: fail("cams")
    if "STILL_MISMATCH" in log: fail("cams: some stills were taken before the camera reached its planned position (see STILL_MISMATCH lines). Re-run cams; do not show these stills")
    if rate:   # full pass: check stills inside each shot do not jump
        expected_counts = [max(3, min(8, int(round((s["t"][1] - s["t"][0]) * rate)) + 1))
                           for s in S["shots"]]
        r = subprocess.run([sys.executable, os.path.join(SCR, "still_check.py"),
                            os.path.join(J, "cam_*.png"),
                            "--expected-counts", ",".join(str(n) for n in expected_counts)],
                           capture_output=True, text=True)
        say(r.stdout)
        if r.returncode: fail("cams: stills jump/flip inside a shot = bad capture, not the real camera. Re-run cams --full; do not show these stills")
    sheet = os.path.join(J, "part_cams.jpg")
    prior = os.stat(sheet).st_mtime_ns if os.path.isfile(sheet) else None
    result = subprocess.run([sys.executable, os.path.join(SCR, "contact_sheet.py"), os.path.join(J, "cam_*.png"), sheet])
    if result.returncode or not os.path.isfile(sheet) or (prior is not None and os.stat(sheet).st_mtime_ns == prior):
        fail("cams: fresh contact sheet not verified; do not send old preview")
    capture_cams(S,Path(ROOT),Path(J))
    bridge = os.path.join(ROOT, "tools", "chrome_preview_bridge", "queue_preview.py")
    if os.path.isfile(bridge):
        br = subprocess.run([sys.executable, "-B", bridge, sheet, str(S.get("story","")), str(S.get("part",""))], capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        say("Preview bridge: " + (br.stdout.strip() if not br.returncode else "queue failed"))
    say("OK cams -> %s (LOOK: faces 3/4, speaker visible, no bed/clipping, nobody cut by the frame edge)" % sheet)


MOTION_JOB = r'''
import RLPy, os, json
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
P = json.load(open(os.path.join(J, 'motion_check.json'), encoding='utf-8'))
out = {}
for a in RLPy.RScene.GetAvatars():
    n = a.GetName()
    if n not in P['cast']: continue
    pts = []
    for k in range(int(P['end'] * 2) + 1):
        RLPy.RGlobal.SetTime(T(k * 0.5))
        if not a.IsVisible(T(k * 0.5)): pts.append(None); continue
        mx, c, mn = RLPy.RVector3(), RLPy.RVector3(), RLPy.RVector3(); a.GetBounds(mx, c, mn); pts.append((c.x, c.y))
    v = [p for p in pts if p]
    big = [(k * 0.5, round(((pts[k][0] - pts[k-1][0])**2 + (pts[k][1] - pts[k-1][1])**2)**0.5))
           for k in range(1, len(pts)) if pts[k] and pts[k-1]]
    out[n] = {'range': [round(max(p[0] for p in v) - min(p[0] for p in v)), round(max(p[1] for p in v) - min(p[1] for p in v))] if v else [0, 0],
              'big': [b for b in big if b[1] > 15]}
RLPy.RGlobal.SetTime(T(0))
open(os.path.join(J, 'drift.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
open(os.path.join(J, 'motion_check.log.txt'), 'w', encoding='utf-8').write('DONE')
'''


def step_motion_check(S, base):
    """No walking forward then snapping back, no jerks (user 2026-11-21): body centre every 0.5 s."""
    wjson("motion_check.json", {"end": duration(S["wav"]), "cast": list(S.get("cast", {}))})
    job(MOTION_JOB, "zz_part_motion")
    if "DONE" not in rlog("motion_check.log.txt"): fail("motion_check job")
    d = json.load(open(os.path.join(J, "drift.json"), encoding="utf-8")); bad = []
    for n, r in d.items():
        say("  %s drift %s cm, jumps %s" % (n, r["range"], r["big"][:4]))
        if max(r["range"]) > S.get("max_drift", 60) or r["big"]: bad.append(n)
    if bad: fail("motion_check: %s walk away/snap back or jerk. Use an in-place motion or lower speed, re-run pose" % ", ".join(bad))
    say("OK motion_check: everyone stays in place")


THINKY = re.compile("คิด|เห็นว่า|สงสัย|ตัดสินใจ|ไตร่ตรอง|วางแผน|นึก")


def think_rng(th, end):
    """spec "think": true | [t0, t1] | [[t0, t1], ...] -> list of [t0, t1]"""
    if not th: return []
    if th is True: return [[0, end]]
    return [th] if not isinstance(th[0], list) else th


def think_warns(S):
    """User 2026-11-22: a line about thinking must show a thinking face on the person in that shot."""
    out = []
    for ln in S.get("lines", []):
        if not THINKY.search(ln.get("text", "")): continue
        mid = (ln["t"][0] + ln["t"][1]) / 2
        sh = next((s for s in S["shots"] if s["t"][0] <= mid < s["t"][1]), None)
        who = sh and sh.get("subject")
        c = S["cast"].get(who or "", {})
        th = c.get("think")
        ok = any(a <= mid <= b for a, b in think_rng(th, 1e9))
        if who and not ok:
            out.append("%.1fs \"%s\": %s needs \"think\" (thinking face)" % (ln["t"][0], ln["text"][:30], who))
    return out


FACE_JOB = r'''
import RLPy, os, json
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
F = lambda x: x.ToFloat() / 6000.0
P = json.load(open(os.path.join(J, 'face_check.json'), encoding='utf-8'))
out = {}
for a in RLPy.RScene.GetAvatars():
    n = a.GetName()
    if n not in P['cast']: continue
    fc = a.GetFaceComponent(); q = P['cast'][n]
    ends = []
    for i in range(fc.GetClipCount()):
        c = fc.GetClip(i); ends.append(F(c.ClipTimeToSceneTime(T(0))) + F(c.GetClipLength()))   # GetClipLength = scene length already
    joins = []   # user 2026-11-22: every join = gap + crossing X (back fade-in AND front fade-out), read from iClone
    for comp, kind in ((a.GetSkeletonComponent(), 'body'), (fc, 'face')):
        cl = sorted([comp.GetClip(i) for i in range(comp.GetClipCount())], key=lambda c: F(c.ClipTimeToSceneTime(T(0))))
        for p, c in zip(cl, cl[1:]):
            st = F(c.ClipTimeToSceneTime(T(0))); g = st - (F(p.ClipTimeToSceneTime(T(0))) + F(p.GetClipLength()))
            d = [F(x) for x in p.GetTransitionData()]
            joins.append([kind, round(st, 2), round(g, 2), round(F(c.GetTransitionRange()), 2), round(d[2], 2), round(d[3], 2)])
    w = {}
    for t, names in q['probe']:
        w[str(t)] = [round(v, 3) for v in fc.GetExpressionWeights(T(t), names)]
    out[n] = {'blink': fc.GetAutoBlinkName(), 'clips': fc.GetClipCount(), 'end': round(max(ends or [0]), 1), 'w': w, 'joins': joins}
open(os.path.join(J, 'face_check.out.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
'''

SMILE_K, THINK_K = "Mouth_Corner_Pull_L", "Brow_Raise_In_L"


def vis_mids(c, end):
    """middle of every visible window of a cast member"""
    v = sorted(c.get("visible") or [[0, 1]]); out = []
    for i, (t, on) in enumerate(v):
        if on:
            t1 = v[i + 1][0] if i + 1 < len(v) else end
            if t1 - t > 0.5: out.append(round(t + 0.85 * (t1 - t), 2))   # late in the window: the smile ramps up
    return out


def step_face_check(S, base):
    """Read back from iClone (not our own log) the 3-part face flow of EVERY cast member (user 2026-11-22):
    1 auto blink on, 2 face motion clips present and covering the part, 3 feeling really visible
    (smile / think weights at the middle of each visible window - a clip loaded after the keys erases them)."""
    end = duration(S["wav"])
    try: os.remove(os.path.join(J, "face_check.out.json"))
    except OSError: pass
    q = {}
    for n, c in S["cast"].items():
        pr = [[t, [SMILE_K]] for t in vis_mids(c, end)] if c.get("smile") else []
        for tw in think_rng(c.get("think"), end): pr.append([round((tw[0] + tw[1]) / 2, 2), [THINK_K]])
        q[n] = {"probe": pr}
    wjson("face_check.json", {"cast": q})
    job(FACE_JOB, "zz_face_check")
    got = json.loads(rlog("face_check.out.json") or "{}")
    bad = []
    for n, c in S["cast"].items():
        g = got.get(n)
        if not g: bad.append("%s: not found in iClone" % n); continue
        want = str(c.get("blink", "Normal"))
        say("  %s: ① กระพริบ %s ② ท่าหน้า %d คลิป ถึง %.1fs ③ %s" % (n, g["blink"], g["clips"], g["end"],
            ", ".join("%ss=%s" % (t, v) for t, v in g["w"].items()) or "-"))
        if g["blink"] != want: bad.append("%s: blink %s (want %s)" % (n, g["blink"], want))
        if g["clips"] < 1: bad.append("%s: no face motion clip" % n)
        else:   # clips only cover the on-screen windows (user 2026-11-22) - must reach the last visible moment
            vis = sorted(c.get("visible") or [[0, 1]]); last = end if vis[-1][1] else vis[-1][0]
            if g["end"] < last - 0.5: bad.append("%s: face clips stop at %.1fs < %.1fs (last on screen)" % (n, g["end"], last))
        if not (c.get("smile") or c.get("think") or c.get("face")): bad.append("%s: no feeling (smile/think/face)" % n)
        for t, v in g["w"].items():
            need = 0.25 * min(0.8, float(c["smile"])) if c.get("smile") and [t2 for t2, k in q[n]["probe"] if str(t2) == t and k == [SMILE_K]] else 0.25
            if v and v[0] < need: bad.append("%s: feeling lost at %ss (%.2f < %.2f) - keys erased by a face clip?" % (n, t, v[0], need))
        for kind, st, gp, fin, fout, foff in g.get("joins", []):   # joins: [kind, start, gap, fade-in, front fade-out, out offset]
            if gp > 3.0: continue                                  # different on-screen windows: not a join
            if not 0.3 <= gp <= 2.0: bad.append("%s %s join at %.1fs: gap %.2fs (want 0.3-2.0, never touching)" % (n, kind, st, gp))
            elif fin < gp + 0.5 or fout < gp + 0.5 or foff >= -0.3:
                bad.append("%s %s join at %.1fs: no crossing X (fade-in %.2f, front fade-out %.2f @ %.2f)" % (n, kind, st, fin, fout, foff))
        nj = len([j for j in g.get("joins", []) if j[2] <= 3.0])
        say("     รอยต่อคลิป %d จุด: ห่าง + ไขว้ X" % nj)
    bad += ["thinking line without thinking face: " + w for w in think_warns(S)]
    # 2026-11-22 user: mouths did not move on some lines after pose was re-run AFTER lip (face .iTalk clips
    # loaded later cover the AccuLips mouth). Re-running pose means lip must run again: use `pose --from`.
    pd, ld = (os.path.join(J, x) for x in ("pose.done", "lip.done"))
    if any(c.get("who") not in NARR for c in S.get("lines", [])) and os.path.exists(pd) and (not os.path.exists(ld) or os.path.getmtime(ld) < os.path.getmtime(pd)):
        bad.append("pose ran after lip: run `pose --from` so lip sync is redone on top of the face clips")
    if bad: fail("face_check:" + "".join(chr(10) + "  - " + b for b in bad))
    say("OK face_check: blink + face motion + feeling on all %d characters (read from iClone)" % len(got))


def step_light_check(S, base):
    """No half white / half black faces on the stills (user 2026-11-21)."""
    r = subprocess.run([sys.executable, os.path.join(SCR, "light_check.py"), S["_spec"], J], capture_output=True, text=True)
    for line in r.stdout.splitlines(): say("  " + line)
    if r.returncode: fail("light_check: faces half white/black. Lower face_light_multiplier or move the fill in front, re-run cams")
    say("OK light_check")


def step_switch(S, base):
    gui("switch")   # user 2026-11-21: viewport on the Switch camera before the user checks
    from sleep_session import active
    say("OK viewport = Switch camera. "+("Sleep Mode: verify evidence and use sleep-approve." if active(Path(ROOT),S["story"],str(S["part"])) else "STOP: user reviews and approves."))


def step_video_check(S, base):
    v = expand(S["video"])
    if not os.path.exists(v): fail("video_check: no video at %s" % v)
    from media_qa import probe_video
    want=duration(S["wav"])
    try: got=probe_video(FFP,v,want)
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as e:fail("video_check: "+str(e))
    say("OK video_check: %s video %.2fs audio %.2fs" % (os.path.basename(v),got["video"],got["audio"]))



def step_cam_check(S, base):
    """ALL shots in one image + the AI's answer for every shot (scripts/cam_check.py). user 2026-11-23."""
    import cam_check
    code, msg = cam_check.check(S, J)
    say(msg)
    if code: sys.exit(code)   # 3 = AI must fill the check file, 1 = shots fail


def step_ready(S, base):
    # Flow guard (user 2026-11-21 "ทำไมไม่ทำตามโฟว์งาน"): every earlier step must be done (green) and the
    # user must have approved the stills (Preview "ผู้ใช้ตรวจ"), otherwise no save/render.
    g = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "progress", "%s_%s.json" % (S.get("story"), S.get("part")))
    d = json.load(open(g, encoding="utf-8")) if os.path.exists(g) else {}
    sd = d.get("steps_done", {})
    miss = [k for k in ORDER if k not in sd and not (k == "lip" and not any(l.get("who") not in NARR for l in S.get("lines", [])))]
    if miss: fail("ready: run these steps first, in order: " + ", ".join(miss))
    from cinematic_qa import editorial_valid
    if not editorial_valid(S,Path(ROOT)):fail("ready: editorial evidence stale; repair and review")
    from sleep_session import approval_valid
    if not (d.get("ok", {}).get("step5") or approval_valid(Path(ROOT),S["story"],str(S["part"]),d)): fail("ready: the user has not approved the stills (Preview: ผู้ใช้ตรวจ)")
    proj = os.path.normpath(S["project"])
    proof = d.get("ready_menu_save")
    if not proof:
        for i, gate in enumerate(("switch", "tozero")): count("ready", i, 2, gate); gui(gate)
        if not os.path.isfile(proj): fail("ready: project file is missing: " + proj)
        d["ready_menu_save"] = {"baseline_mtime_ns": os.stat(proj).st_mtime_ns, "started": time.time()}
        with open(g, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=1)
        say("AI WORK: now click iClone File > Save Project manually, reopen the same file with File > Open, confirm it loads, then run Ai-iclone do again. No script or shortcut may save.")
        sys.exit(3)
    if not os.path.isfile(proj): fail("ready: project file is missing after the menu save: " + proj)
    if os.stat(proj).st_mtime_ns <= int(proof.get("baseline_mtime_ns", 0)):
        fail("ready: file timestamp did not advance after the manual File > Save Project; save and reopen it, then retry")
    live_title = title()
    if os.path.basename(proj) not in live_title or "*" in live_title:
        fail("ready: reopen the saved project in iClone and confirm its title has the expected filename and no '*': " + live_title)
    d.pop("ready_menu_save", None)
    with open(g, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=1)
    count("ready", 2, 2, "ตรวจเซฟเมนูและเปิดซ้ำ")
    say("OK ready: manual File-menu save and reopen verified. Render next only after the current mode's authorization and actual review gates.")

def step_render(S, base, approved):
    from cinematic_qa import editorial_valid
    if not editorial_valid(S,Path(ROOT)):fail("render: editorial evidence stale")
    from sleep_session import approval_valid
    d=json.load(open(os.path.join(ROOT,"progress",f'{S["story"]}_{S["part"]}.json'),encoding="utf-8"))
    if not approved or not (d.get("ok",{}).get("step5") or approval_valid(Path(ROOT),S["story"],str(S["part"]),d)) or not all(k in d.get("steps_done",{}) for k in ORDER+["ready"] if k!="lip" or any(l["who"] not in NARR for l in S["lines"])): fail("render requires actual QA, ready and authorization")
    if Path(S["video"]).exists():
        import shutil
        backup=Path(ROOT)/"progress"/"render_backups"/S["story"]/str(S["part"]);backup.mkdir(parents=True,exist_ok=True)
        dest=backup/(str(time.time_ns())+".mp4");shutil.copy2(S["video"],dest)
        say("Existing video preserved in "+str(dest))
    wait_textures()   # 2026-11-21: a render started during Texture Loading came out with white, untextured people
    end = duration(S["wav"]); mids = ",".join("%.2f" % ((s["t"][0] + s["t"][1]) / 2) for s in S["shots"])
    a = ["render", os.path.normpath(S["video"]), end, os.path.normpath(S["wav"]), "-Shots", mids]
    # Publication is a separate user action after final review; never publish unreviewed output.
    gui(*a)


def step_scene_review(S,base):
    from cinematic_qa import scene_review
    scene_review(S,Path(ROOT),Path(J),job,fail,say)

def step_prop_review(S,base):
    from cinematic_qa import prop_review
    prop_review(S,Path(ROOT),Path(J),job,step_props,fail,say)

def step_camera_replan(S,base):
    from cinematic_qa import check_replan
    check_replan(S,Path(ROOT),Path(J),fail,say)

def step_editorial_review(S,base):
    from cinematic_qa import check_editorial
    check_editorial(S,Path(ROOT),Path(J),fail,say)

def step_final_review(S,base):
    from cinematic_qa import check_final
    check_final(S,Path(ROOT),fail,say)

STEPS = {"scene_review":step_scene_review,"prop_review":step_prop_review,"camera_replan":step_camera_replan,"editorial_review":step_editorial_review,"final_review":step_final_review,"audio": step_audio, "check": step_check, "motion_plan": step_motion_plan, "open": step_open, "cast": step_cast, "pose": step_pose,
         "sound": step_sound, "lip": step_lip, "cams": step_cams, "cam_check": step_cam_check, "motion_check": step_motion_check,
         "light_check": step_light_check, "face_check": step_face_check, "switch": step_switch, "ready": step_ready, "video_check": step_video_check}

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    spec, step = sys.argv[1], sys.argv[2]
    from preview_gate import require, Blocked
    try: require(spec,step,sys.argv[3:])
    except Blocked as e: print("STOP: "+str(e)); sys.exit(2)
    S = expand(json.load(open(spec, encoding="utf-8"))); base = os.path.splitext(spec)[0]
    resolve(S, spec); S["_spec"] = spec
    if step == "render": run = ["render"]   # the render is always followed by the video check
    elif step == "all": run = ORDER
    elif step in STEPS: run = ORDER[ORDER.index(step):] if "--from" in sys.argv and step in ORDER else [step]
    else: fail("unknown step " + step)
    if run: story_gate(S)   # user 2026-11-22: stage 1 first, for every step of every part
    if run and run[0] not in ("check", "render") and step != "audio": step_check(S, base)   # never act on a broken spec
    FULL = ORDER + ["ready", "render", "video_check","final_review"]   # every pipeline step the Preview shows, in order
    def _now(st, state):   # live status for the Preview program (scripts/progress_app.py)
        try:
            f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "progress", "now.json")
            os.makedirs(os.path.dirname(f), exist_ok=True)
            old = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
            if (old.get("story"), str(old.get("part"))) != (S.get("story"), str(S.get("part"))):
                open(os.path.join(os.path.dirname(f), "now_log.txt"), "w", encoding="utf-8").close()   # new part: clean log
            json.dump({"story": S.get("story"), "part": str(S.get("part")), "step": st, "state": state,
                       "time": time.time()}, open(f, "w", encoding="utf-8"), ensure_ascii=False)
            # per-part record of finished steps (Preview dots). Re-running a step = it and the steps built
            # on it are not done any more (grey again) until they finish again.
            g = os.path.join(os.path.dirname(f), "%s_%s.json" % (S.get("story"), S.get("part")))
            d = json.load(open(g, encoding="utf-8")) if os.path.exists(g) else {"ok": {}, "orders": []}
            sd = d.setdefault("steps_done", {})
            if state == "running":
                # every later step must run again (sound/lip only touch the save/render steps)
                # check / motion_check / light_check / video_check only READ: they never grey out other steps
                from workflow_state import invalidated_steps
                invalidate = invalidated_steps(st, FULL)
                try: os.remove(os.path.join(J, "live.json"))   # no stale % from the previous step
                except OSError: pass
                for k in invalidate: sd.pop(k, None)
                if st in ("cast", "pose", "cams", "open", "sound", "lip", "motion_plan","scene_review","prop_review","camera_replan","editorial_review","cam_check","motion_check","light_check","face_check"):
                    d.get("ok", {}).pop("step5", None); d.pop("sleep_approval",None)
                if st != "ready" and "ready" in invalidate: d.pop("ready_menu_save", None)
                if "sound" in invalidate: d.pop("sound_source", None)
            elif state == "done":
                sd[st] = time.time()
                if st == "sound":
                    from workflow_state import sound_source
                    d["sound_source"] = sound_source(S["wav"])
            json.dump(d, open(g, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        except Exception:
            pass
    import time
    for s in run:
        _now(s, "running"); ailog.start(s)
        say("===== %s (ข้อ %d/%d ของคำสั่งนี้ = %d%%) =====" % (s, run.index(s) + 1, len(run), 100 * run.index(s) // len(run)))
        try:
            if s == "render": step_render(S, base, "--approved" in sys.argv)
            else: STEPS[s](S, base)
        except BaseException:
            _now(s, "failed"); raise
        _now(s, "done"); ailog.done(); ailog.clean_fails()
