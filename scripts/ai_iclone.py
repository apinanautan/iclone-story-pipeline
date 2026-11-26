# -*- coding: utf-8 -*-
"""Ai-iclone: the ONE entry point an AI needs. Run it with no arguments: it prints what this program is,
where the work stands (the same state the Ai-iclone window shows) and the single next command.

  Ai-iclone                         manual + status + what to do now
  Ai-iclone status                  status only
  Ai-iclone use <story> [part]      work on this story (and part)
  Ai-iclone new-story <story>       new story sheet stories/<story>.json from the template
  Ai-iclone range <m:ss-m:ss>       the working range, ONLY when the user typed it in chat
  Ai-iclone do [--dry]              do the next step (one step per call)
  Ai-iclone rules <step>            the rules card of one step
  Ai-iclone approve --said "<text>" user approval typed in chat (story plan / part stills)
  Ai-iclone steps                   every step, numbered, with who does it
  Ai-iclone version                 program version (file VERSION)
  Ai-iclone update                  get the newest release from GitHub now (every command also checks, at most once per 10 min)
  Ai-iclone clean                   delete iClone temp files older than 2 days (also automatic after each part)
  Ai-iclone log                     what runs now (real %), log with clock + seconds, last FAIL report (screen text, picture)
  Ai-iclone doctor                  check this PC's tools (ffmpeg, ffprobe, Python, Blender, iClone jobs folder)
  Ai-iclone motions [story] [part] [--write]
                                    body motions per line from the WHOLE library (talk / listen / mood, never the same clip all story)
  Ai-iclone video2motion <clip.mp4> [name] [--allow-install]
                                    a video of one person -> iClone motion FBX on CC3_Base_Plus (local, CPU, no iClone)

State lives in files only (stories/, parts/, progress/), read by the same functions as the window
(scripts/progress_app.py), so the AI and the window always agree. No screenshots needed.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import progress_app as P  # noqa: E402  (state functions only; no window is opened)
from paths import expand  # noqa: E402

ROOT = P.ROOT
SCR = ROOT / "scripts"
SKILLS = ROOT / ".agents" / "skills"
SEL = P.PROG / "ai_iclone.json"
PY = sys.executable
CMD = "Ai-iclone"   # short name in the text; the full path is printed once in the manual
FULL = os.environ.get("AI_ICLONE_EXE") or (str(ROOT / "Ai-iclone.exe") if (ROOT / "Ai-iclone.exe").exists() else str(ROOT / "Ai-iclone.cmd"))
try: VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
except OSError: VERSION = "?"

# who does each step: script = the program runs it; ai = the AI thinks and fills a file; user = STOP, the user decides
PART_KIND = {"plan": "ai", "audio": "script", "check": "script", "motion_plan": "script", "open": "script",
             "cast": "script", "sound": "script", "pose": "script", "lip": "script", "scene_review": "script", "prop_review":"script", "camera_replan": "script", "cams": "script", "cam_check": "script",
             "motion_check": "script", "light_check": "script", "face_check": "script", "editorial_review": "script", "switch": "script",
             "user_ok": "user", "ready": "script", "render": "script", "video_check": "script", "final_review": "script"}
STORY_KIND = {"sheet": "ai", "source": "ai", "range": "user", "split": "ai", "chars": "ai", "scenes": "ai",
              "partplans": "ai", "output": "ai", "story_ok": "user"}
# rules card of a step = these skill files (short, already written for AI) + the notes below
SKILL_OF = {"prop_review":["blender-prop-production","cinematic-direction"],"scene_review":["cinematic-direction"],"camera_replan":["cinematic-direction"],"editorial_review":["cinematic-direction"],"final_review":["cinematic-direction"],"plan": ["plan-part", "acting"], "audio": ["cut-audio"], "check": ["plan-part"], "motion_plan": ["acting","pose-bones","script-catalog","motion-analysis"],
            "open": ["build-part"], "cast": ["build-part"], "pose": ["build-part", "pose-bones","script-catalog"], "sound": ["build-part"],
            "lip": ["lip-sync"], "cams": ["review-stills"], "cam_check": ["review-stills"], "motion_check": ["review-stills","motion-analysis"],
            "light_check": ["review-stills"], "face_check": ["review-stills", "acting"], "switch": ["iclone-control"],
            "ready": ["save-render"], "render": ["save-render"], "video_check": ["save-render"],
            "split": ["cut-audio"]}
NOTES = {
    "sheet": "สร้างใบงาน: {cmd} new-story <ชื่อเรื่อง> แล้วเติม name/folder ใน stories/<เรื่อง>.json (ภาพรวมเท่านั้น รายละเอียดอยู่ในแต่ละท่อน)",
    "source": "เติม script_docx (บท .docx) และ master_audio (เสียงเต็ม) ใน stories/<เรื่อง>.json ใช้ {DRIVE} ไม่เขียนชื่อไดรฟ์ ไฟล์ต้องมีจริง ห้ามเขียนลง {DRIVE}",
    "range": "STOP: เวลาที่ทำงานมาจากผู้ใช้เท่านั้น ห้ามเดา ให้ผู้ใช้คลิก 'เวลาที่ทำงาน' ในหน้าต่าง Ai-iclone หรือพิมพ์ในแชท แล้วรัน {cmd} range <m:ss-m:ss>",
    "split": "แบ่งท่อนในช่วงเวลาที่ทำงาน (~1 นาที/ท่อน ตัดที่เงียบ) ใส่ parts[].master [s,e] ให้ต่อกันพอดีถึงปลายช่วง แล้วตัดเสียงทุกท่อนด้วย cut_audio.py ไปที่ audio_dir/ท่อนN.wav ใส่ --script <script_docx> ทุกครั้ง (คำจากบทจริง เวลาเดิม) ห้ามทดสอบการ์ดจอ/ลง Whisper เอง และใส่ parts[].transcript ทุกบรรทัดต้องมี who (บรรยาย หรือชื่อตัวละคร)",
    "chars": "เติม characters {ชื่อ avatar ใน iClone: {role, voice, avatar}} ทุกตัวในเรื่อง ไฟล์ avatar ต้องมีจริง",
    "scenes": "เติม scenes {ชื่อ: {type, file, room/area, spots, cams}} ไฟล์ฉากต้องมีจริง วัดฉากด้วย ic8_scene_scan.py ครั้งเดียว",
    "partplans": "เติม parts[].content (เนื้อเรื่อง) และ parts[].plan (แผนสั้นๆ) ทุกท่อน",
    "output": "เติม save_dir และ video_dir ใน stories/<เรื่อง>.json โฟลเดอร์ต้องมีจริง",
    "story_ok": "STOP: ส่งแผนทั้งเรื่องให้ผู้ใช้ดู (เรื่อง ช่วงเวลา ท่อน ตัวละคร ฉาก) รอผู้ใช้คลิกอนุมัติในหน้าต่าง หรือพิมพ์ในแชทว่าผ่าน แล้วรัน {cmd} approve --said \"<คำที่ผู้ใช้พิมพ์>\"",
    "plan": "เขียนสเปกท่อน parts/<เรื่อง>_<N>.json: lines.who ทุกบรรทัด, cast (spot หรือ pos/yaw, motions, lookat), shots จนจบเสียง ห้ามมี who เป็น \"?\" และ shots ห้ามว่าง เสร็จแล้วรัน {cmd} do (ข้อถัดไปคือ check จะตรวจตามกฎ)",
    "cams": "ภาพนิ่งเสร็จแล้ว ข้อต่อไปคือ cam_check: รัน {cmd} do",
    "cam_check": "เปิดดูรูป ic8_jobs/part_cams_all.jpg (ทุกช็อตในรูปเดียว) แล้วเติมไฟล์ progress/<เรื่อง>_<N>_camcheck.json ทุกช็อต: see = เห็นอะไรจริงในภาพ, ตอบ true/false ทุกคำถาม ห้ามเดาจากแผน ช็อตไหน false เขียน fix แล้วแก้ shots ในสเปก รัน {cmd} repair camera_replan แล้ว {cmd} do เพื่อสร้างและตรวจหลักฐานใหม่",
    "user_ok": "STOP: ส่งภาพรวมกล้อง (part_cams_all.jpg) ให้ผู้ใช้ดู รอผู้ใช้คลิก 'ผู้ใช้ตรวจ (ผ่าน)' ในหน้าต่าง หรือพิมพ์ในแชทว่าผ่าน แล้วรัน {cmd} approve --said \"<คำที่ผู้ใช้พิมพ์>\"",
    "render": "เรนเดอร์ได้เพราะผู้ใช้ผ่านแล้ว ใช้เวลานาน (~40 นาที) อย่าแตะ iClone ระหว่างนั้น",
}
HARD = """กฎเหล็ก (ห้ามผิด):
- ทำตามที่โปรแกรมนี้บอกเท่านั้น ไม่ต้องอ่าน AGENTS.md / rules.md / docs อื่น เว้นแต่การ์ดกฎของข้อนั้นบอก
- ห้ามข้ามข้อหรือปลอมหลักฐาน โหมดปกติรอผู้ใช้อนุมัติ; Sleep Mode เปิดผ่านส่วนขยายโดยผู้ใช้เท่านั้นและใช้ sleep-approve หลัง QA จริง ห้ามใช้ approve --said แทนผู้ใช้
- ห้ามเขียนลง {DRIVE} (Google Drive) ยกเว้นคัดลอกวิดีโอเสร็จไปที่ publish
- เซฟและเปิดไฟล์ซ้ำผ่านเมนู File ใน iClone เท่านั้น ห้ามใช้สคริปต์/CLI/คีย์ลัดเซฟ ข้อ ready ตรวจหลักฐาน; ห้าม RFileIO.SaveProject / RGlobal.RenderAudio
- ข้อไหน FAIL: อ่านข้อความ แก้ที่สเปก/ไฟล์ แล้ว do ใหม่ได้ 1 ครั้ง ถ้า FAIL ซ้ำ หยุดแล้วบอกผู้ใช้เป็นภาษาไทย
- ตอบผู้ใช้เป็นภาษาไทยง่ายๆ คำสั่งใหม่ของผู้ใช้ทุกข้อ เขียนต่อท้าย docs/rules.md ทันที
- Cast -> Sound ครั้งเดียว -> Pose -> Lip -> Scene Review -> Prop Review -> Camera Replan -> Cams -> Editorial Review; แก้ Pose, Motion, กล้อง หรือเพิ่มตัวละครในโปรเจกต์เดิม ไม่ต้องใส่ Project Sound ซ้ำ. เซฟ/เปิดซ้ำด้วยเมนู File ของ iClone เท่านั้น.
"""
CHAT = """ผู้ใช้พูดในแชท -> คำสั่ง:
  "วันนี้ทำเรื่อง X"            -> {cmd} use X   (ยังไม่มีเรื่อง -> {cmd} new-story X)
  "ทำช่วง 0:00 ถึง 7:14"         -> {cmd} range 0:00-7:14
  "ทำท่อน 2"                    -> {cmd} use X 2  แล้ว {cmd} do ซ้ำจนเจอ STOP
  "ผ่าน" / "อนุมัติ"              -> {cmd} approve --said "ผ่าน"
  "ต่อเลย" / ไม่ได้บอกอะไร        -> {cmd} do
  "แปลงคลิปเป็นท่า <ไฟล์>"         -> {cmd} video2motion <ไฟล์.mp4>  (ครั้งแรกขึ้น STOP: ถามผู้ใช้ก่อนติดตั้ง แล้วเติม --allow-install)"""


def out(s=""):
    try:
        print(s, flush=True)
    except OSError:   # reader closed the pipe (e.g. `| head`): stop quietly, no traceback
        os._exit(0)


def sel():
    return P.load(SEL, {})


def save_sel(d):
    SEL.parent.mkdir(parents=True, exist_ok=True)
    SEL.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def story_now():
    s = sel().get("story")
    if s in P.stories(): return s
    ss = P.stories()
    return ss[0] if len(ss) == 1 else None


def part_now(story):
    from sleep_session import state
    session=state(ROOT)
    if session.get("enabled") and session.get("story")==story and session.get("part"):return session["part"]
    d = sel()
    return str(d["part"]) if d.get("story") == story and d.get("part") else P.current_part(story)


def where(story):
    """(stage, n, rows, next_key). rows = [(no, key, label, state, info)]"""
    ss = P.story_states(story)
    rows = [(i, k, l, ss[k][0], ss[k][1]) for i, (k, l) in enumerate(P.STORY_STEPS, 1)]
    nxt = next((k for _, k, _, s, _ in rows if s != "done"), None)
    if nxt: return "story", None, rows, nxt
    n = part_now(story)
    st, _ = P.step_states(story, n)
    rows = [(i, k, l, st[k], "") for i, (k, l) in enumerate(P.STEPS, 1)]
    nxt = next((k for _, k, _, s, _ in rows if s not in ("done", "skip")), None)
    return "part", n, rows, nxt


MARK = {"done": "✓", "skip": "-", "todo": " ", "warn": "!", "bad": "✗", "run": "…", "fail": "✗"}


def show_status():
    story = story_now()
    if not story:
        out("ยังไม่ได้เลือกเรื่อง. เรื่องที่มี: %s" % (", ".join(P.stories()) or "(ไม่มี)"))
        out("-> %s use <เรื่อง>   หรือ   %s new-story <เรื่อง>" % (CMD, CMD)); return None
    stage, n, rows, nxt = where(story)
    st = P.load(ROOT / "stories" / f"{story}.json", {})
    tr = st.get("teacher_range") or [0, 0]
    out("เรื่อง: %s   เวลาที่ทำงาน %s–%s" % (story, P.mm(tr[0]), P.mm(tr[1])))
    out("① เตรียมเรื่อง" if stage == "story" else "② ทำทีละท่อน  ท่อน %s  (เตรียมเรื่องครบแล้ว)" % n)
    for no, k, label, s, info in rows:
        who = (STORY_KIND if stage == "story" else PART_KIND)[k]
        arrow = "  <- ตอนนี้" if k == nxt else ""
        line = " [%s] %2d %-12s %s %s" % (MARK.get(s, "?"), no, k, label, ("(" + info + ")") if info and info != "✓" else "")
        if s not in ("done", "skip"): line = line.rstrip() + "   [%s]" % {"ai": "AI คิด", "script": "โปรแกรมทำ", "user": "รอผู้ใช้"}[who]
        out(line.rstrip() + arrow)
    if not nxt:
        out("ท่อน %s เสร็จครบแล้ว -> ท่อนถัดไป: %s use %s %s" % (n, CMD, story, next((p for p in P.parts_of(story) if tuple(map(int,p.split("."))) > tuple(map(int,n.split(".")))), "END")))
    b, files = P.jobs_usage()
    out("ไฟล์ชั่วคราว iClone: %s (%d ไฟล์) ที่ %s%s" % (P.gb(b), files, P.J, "  ⚠ เกิน 5 GB -> " + CMD + " clean" if b > 5e9 else ""))
    return story, stage, n, nxt


def card(step):
    txt = []
    if step in NOTES: txt.append(NOTES[step].replace("{cmd}", CMD))
    for sk in SKILL_OF.get(step, []):
        f = SKILLS / sk / "SKILL.md"
        if f.exists():
            body = f.read_text(encoding="utf-8").split("---", 2)[-1].strip()
            txt.append("--- การ์ดกฎ: %s ---\n%s" % (sk, body))
    return "\n\n".join(txt) or "(ไม่มีกฎเพิ่มสำหรับข้อนี้)"


def fails(step, add=None):
    d = sel(); f = d.setdefault("fails", {})
    if add is True: f[step] = f.get(step, 0) + 1
    elif add is False: f.pop(step, None)
    if add is not None: save_sel(d)
    return f.get(step, 0)


def script_cmd(story, n, step):
    spec = ROOT / "parts" / f"{story}_{n}.json"
    if step == "audio":
        st = P.load(ROOT / "stories" / f"{story}.json", {})
        p = next((x for x in st.get("parts", []) if str(x.get("n")) == str(n)), None)
        if not p or not p.get("master"): return None
        S = P.load(spec, {}) or {}
        wav = S.get("wav") or os.path.join(st.get("audio_dir", ""), f"ท่อน{n}.wav")
        c = [PY, str(SCR / "cut_audio.py"), expand(st["master_audio"]), str(p["master"][0]), str(p["master"][1]), expand(wav)]
        return c + ["--script", expand(st["script_docx"])] if st.get("script_docx") else c   # exact words, same times
    c = [PY, str(SCR / "ic8_part.py"), str(spec), step]
    return c + ["--approved"] if step == "render" else c


def PROG_NOW(story, n, step, state):
    """progress/now.json so the window shows this step running with its % (steps that are not ic8_part.py)."""
    try: (P.PROG / "now.json").write_text(json.dumps({"story": story, "part": str(n), "step": step, "state": state,
                                                       "time": time.time()}, ensure_ascii=False), encoding="utf-8")
    except Exception: pass


def do(dry=False, force=False):
    from preview_gate import dispatch, Blocked
    if dry:
        return _do(dry, force)
    try:
        with dispatch():
            return _do(dry, force)
    except Blocked as e:
        out("STOP: " + str(e)); return 2


def _do(dry=False, force=False):
    r = show_status()
    if not r: return 1
    story, stage, n, nxt = r
    out("")
    from sleep_session import state,active
    session=state(ROOT)
    if session.get("phase")=="paused":out("STOP: Sleep paused. Select manual mode explicitly or resume Sleep.");return 2
    if session.get("enabled") and (stage!="part" or not active(ROOT,story,n)):
        out("STOP: Sleep handoff or scope changed");return 2
    if not nxt: return 0
    kind = (STORY_KIND if stage == "story" else PART_KIND)[nxt]
    if fails(nxt) >= 2 and not force:
        out("STOP: ข้อ %s FAIL มาแล้ว %d ครั้ง. บอกผู้ใช้ว่าติดตรงไหน (ภาษาไทย) แล้วรอคำสั่ง. ผู้ใช้ให้ลองใหม่ -> %s do --force" % (nxt, fails(nxt), CMD))
        return 2
    if kind == "user":
        if stage=="part" and nxt=="user_ok":
            from sleep_session import active
            if active(ROOT,story,n):
                out("Sleep Mode: ตรวจหลักฐานสองรอบแล้วใช้ Ai-iclone sleep-approve (ไม่ใช้ approve --said)"); return 3
        out("STOP: รอผู้ใช้  (ข้อ %s)\n%s" % (nxt, card(nxt))); return 2
    if stage == "part" and nxt == "plan" and not P.spec_of(story, n):
        c = [PY, str(SCR / "ic8_story.py"), story, "new", n]
        out("> " + " ".join(c))
        if not dry: subprocess.run(c, cwd=ROOT)
    if kind == "ai":
        out("งานของ AI ข้อ %s (ไม่มีสคริปต์ให้รัน ต้องคิดแล้วเติมไฟล์):\n" % nxt)
        if stage == "part": out(f"ดูข้อมูลท่อน: {PY} scripts/ic8_story.py {story} brief {n}\nสเปก: parts/{story}_{n}.json\n")
        out(card(nxt)); out("\nเติมเสร็จแล้ว -> %s do" % CMD); return 3
    c = script_cmd(story, n, nxt)
    if not c:
        out("FAIL: ท่อน %s ไม่มีเวลา master ในใบงานเรื่อง (กลับไปทำ ① split)" % n); return 1
    order = list(STORY_KIND if stage == "story" else PART_KIND)
    out("ข้อ %s (%d/%d = %d%%): โปรแกรมทำเอง\n> %s" % (nxt, order.index(nxt) + 1, len(order), 100 * order.index(nxt) // len(order), " ".join('"%s"' % x if " " in x else x for x in c)))
    if dry: out("(--dry: ไม่ได้รันจริง)"); return 0
    t0 = time.time()
    if "ic8_part.py" in c[1]:
        from preview_gate import permit
        with permit(story, n, nxt, c[2]) as env:
            rc = subprocess.run(c, cwd=ROOT, env=env).returncode
    else:   # e.g. audio (cut_audio.py): % = its output lines / the lines it printed last time it passed
        import ailog
        ailog.start(nxt); now = PROG_NOW(story, n, nxt, "running")
        p = subprocess.Popen(c, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                             errors="replace", env=dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8"))
        for l in p.stdout: ailog.log(l.rstrip())
        rc = p.wait()
        if rc == 0: ailog.done(); ailog.clean_fails()
        else: out(ailog.fail_report("%s exit %d" % (os.path.basename(c[1]), rc), iclone=False))
        PROG_NOW(story, n, nxt, "done" if rc == 0 else "failed")
    out("")
    if rc == 3:   # the step needs the AI (e.g. cam_check: look at the image, fill the check file)
        out("งานของ AI ข้อ %s: ทำตามข้อความด้านบน แล้ว %s do" % (nxt, CMD)); return 3
    if rc != 0:
        k = fails(nxt, True)
        out("FAIL ข้อ %s (ครั้งที่ %d, %.0f วินาที). อ่าน FAIL REPORT ด้านบน (ข้อไหน กี่วินาที หน้าจอเขียนอะไร) แก้ที่สาเหตุจริง ห้ามเดา%s" % (nxt, k, time.time() - t0,
            " แก้ที่สเปก/ไฟล์ แล้ว %s do อีก 1 ครั้ง" % CMD if k < 2 else " -> หยุด บอกผู้ใช้"))
        out("\n" + card(nxt)); return 1
    fails(nxt, False)
    out("OK ข้อ %s (%.0f วินาที)" % (nxt, time.time() - t0))
    if nxt == "final_review":   # clean only after final editorial review
        fb, fn = P.clean_jobs(); out("ลบไฟล์ชั่วคราวเก่า: %s (%d ไฟล์)" % (P.gb(fb), fn))
    if nxt in NOTES: out(NOTES[nxt].replace("{cmd}", CMD))
    out("ต่อ -> %s do" % CMD); return 0


def repair_cams():
    """Return to the camera stage only from a failed camera review."""
    from preview_gate import dispatch, Blocked
    try:
        with dispatch():
            r = show_status()
            if not r or r[1] != "part" or r[3] != "cam_check" or fails("cam_check") < 1:
                out("STOP: repair-cams requires a failed camera review"); return 2
            story, _, n, _ = r
            f = P.PROG / f"{story}_{n}.json"
            d = P.load(f, {})
            from workflow_state import invalidated_steps
            for key in invalidated_steps("camera_replan",[k for k,_ in P.STEPS]): d.get("steps_done", {}).pop(key,None)
            d.pop("sleep_approval",None);d.pop("ready_menu_save",None)
            d.get("ok", {}).pop("step5", None)
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            out("OK: camera stage reopened; run Ai-iclone do"); return 0
    except Blocked as e:
        out("STOP: " + str(e)); return 2


def repair_pose(said=""):
    """Reopen pose and dependent checks only from a failed camera, motion or face review."""
    from preview_gate import dispatch, Blocked
    try:
        with dispatch():
            r = show_status()
            if not r or r[1] != "part" or not ((r[3] in ("cam_check", "motion_check", "face_check") and fails(r[3]) >= 1) or (r[3] == "user_ok" and said.strip())):
                out("STOP: repair-pose requires a failed review or explicit user rejection at user_ok"); return 2
            story, _, n, _ = r
            f = P.PROG / f"{story}_{n}.json"
            d = P.load(f, {})
            for key in ("pose","lip","scene_review","prop_review","camera_replan","cams","cam_check","motion_check","light_check","face_check","editorial_review","switch","ready","render","video_check","final_review"):
                  d.get("steps_done", {}).pop(key, None)
            d.get("ok", {}).pop("step5", None)
            d.pop("sleep_approval",None);d.pop("ready_menu_save",None)
            if said.strip(): d.setdefault("orders", []).append({"user_rejection": said})
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            out("OK: pose stage reopened; downstream reviews invalidated; run Ai-iclone do"); return 0
    except Blocked as e:
        out("STOP: " + str(e)); return 2


def approve(said):
    if not said.strip(): out("FAIL: ต้องใส่คำที่ผู้ใช้พิมพ์จริง --said \"...\""); return 1
    r = show_status()
    if not r: return 1
    story, stage, n, nxt = r
    stamp = time.strftime("%Y-%m-%d %H:%M") + " chat: " + said.strip()[:80]
    if stage == "story" and nxt == "story_ok":
        f = ROOT / "stories" / f"{story}.json"; st = P.load(f, {}); st["story_plan_ok"] = stamp
        f.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    elif stage == "part" and nxt == "user_ok":
        f = P.PROG / f"{story}_{n}.json"; d = P.load(f, {"ok": {}, "orders": []})
        d.setdefault("ok", {})["step5"] = True; d["step5_said"] = stamp
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        out("FAIL: ตอนนี้ไม่มีข้อที่รออนุมัติ (ข้อปัจจุบัน: %s)" % nxt); return 1
    out("OK บันทึกการอนุมัติของผู้ใช้: " + stamp + "\nต่อ -> %s do" % CMD); return 0


def set_range(v):
    story = story_now()
    if not story: out("FAIL: เลือกเรื่องก่อน (%s use <เรื่อง>)" % CMD); return 1
    try:
        a, b = (P.parse_mmss(x) for x in v.replace("–", "-").split("-", 1)); assert 0 <= a < b
    except Exception:
        out("FAIL: อ่านไม่ออก: %s (แบบ 0:00-7:14)" % v); return 1
    f = ROOT / "stories" / f"{story}.json"; st = P.load(f, {})
    st["teacher_range"] = [round(a, 2), round(b, 2)]; st["teacher_range_confirmed"] = time.strftime("%Y-%m-%d %H:%M chat")
    f.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    out("OK เวลาที่ทำงาน %s–%s" % (P.mm(a), P.mm(b))); return 0


def manual():
    out("Ai-iclone " + VERSION + " (" + str(ROOT) + ") — โปรแกรมทำวิดีโอนิทาน 3D จากเสียง ใน iClone 8 ทีละท่อน (ตัวละครจาก Character Creator 5)")
    out("ทำงานเป็นข้อๆ ตามลำดับ: ① เตรียมเรื่อง 9 ข้อ (ครั้งเดียวต่อเรื่อง) -> ② ทำทีละท่อน %d ข้อ" % len(P.STEPS))
    out("Ai-iclone = \"%s\"   (PowerShell: & \"%s\" do   /  bash: \"%s\" do)" % (FULL, FULL, FULL.replace("\\", "/")))
    out("วิธีทำงาน: รัน %s do ทีละครั้ง ทำตามที่มันบอก จนเจอ STOP แล้วรายงานผู้ใช้\n" % CMD)
    out(CHAT.replace("{cmd}", CMD)); out(""); out(HARD); out("")
    out("ก่อนข้อที่ใช้ iClone: iClone ต้องเปิดอยู่และโหลด Script > Load Python > scripts/ic8_watch.py แล้ว (ถ้าไม่แน่ใจ ถามผู้ใช้)\n")
    out("=== สถานะตอนนี้ ===")
    r = show_status()
    if r and r[3]:
        kind = (STORY_KIND if r[1] == "story" else PART_KIND)[r[3]]
        out("\nข้อต่อไป: %s -> %s" % (r[3], {"user": "STOP รอผู้ใช้ (ดู %s do)" % CMD}.get(kind, "%s do" % CMD)))


def steps():
    out("① เตรียมเรื่อง (ครั้งเดียวต่อเรื่อง)")
    for i, (k, l) in enumerate(P.STORY_STEPS, 1): out("  %2d %-12s %-8s %s" % (i, k, STORY_KIND[k], l))
    out("② ทำทีละท่อน")
    for i, (k, l) in enumerate(P.STEPS, 1): out("  %2d %-12s %-8s %s" % (i, k, PART_KIND[k], l))
    out("ai = AI คิดแล้วเติมไฟล์, script = โปรแกรมทำเอง, user = รอผู้ใช้")


def doctor():
    """user 2026-11-23: other PCs broke on ffmpeg/ffprobe. One command that says what this PC has; no installs."""
    import glob, shutil
    sys.path.insert(0, str(SCR)); import paths
    bad = 0
    for t in ("ffmpeg", "ffprobe"):
        try:
            exe = paths.ffmpeg(t)
            r = subprocess.run([exe, "-version"], capture_output=True, text=True, timeout=30)
            out("%s %s  %s" % ("OK  " if r.returncode == 0 else "FAIL", t, exe)); bad += r.returncode != 0
        except SystemExit as e:
            out("FAIL %s  %s" % (t, e)); bad += 1
    out("OK   python  %s %s" % (sys.executable, sys.version.split()[0]))
    bl = sorted(glob.glob(os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Blender Foundation", "Blender*", "blender.exe")))
    out(("OK   blender %s" % bl[-1]) if bl else "--   blender not installed (only video2motion needs it)")
    out(("OK   " if os.path.isdir(P.J) else "FAIL ") + "iClone jobs folder " + str(P.J)); bad += not os.path.isdir(P.J)
    out("doctor: %s" % ("all OK" if not bad else "%d problem(s). Fix = Ai-iclone update (newest version finds the tools by itself). "
                         "Do NOT hardcode paths or install other ffmpeg copies." % bad))
    return 1 if bad else 0


def main(a):
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding="utf-8")
        except Exception: pass
    c = a[0] if a else ""
    # self-update on EVERY start (exe, Ai-iclone.cmd, GPT/MCP): only the exe used to update (user 2026-11-23)
    if c == "update" or (c not in ("", "help", "-h", "--help", "version", "--version") and os.environ.get("AIICLONE_NO_UPDATE") != "1"):
        import selfupdate
        new = selfupdate.check(force=(c == "update"))
        if c == "update": return 0
        if new:   # run the command with the NEW code
            return subprocess.run([PY, str(SCR / "ai_iclone.py")] + list(a), cwd=ROOT,
                                  env=dict(os.environ, AIICLONE_NO_UPDATE="1")).returncode
    try:
        import paths; paths.mirror() if c not in ("steps","version","--version","status","rules") else None   # <jobs>/paths.json: iClone-side scripts, OpenPlugin and .ps1 read this PC's folders there
    except Exception: pass
    if c in ("", "help", "-h", "--help"): manual(); return 0
    if c in ("version", "--version"): out("Ai-iclone " + VERSION); return 0
    if c == "status": return 0 if show_status() else 1
    if c == "steps": steps(); return 0
    if c == "clean":
        b0, _ = P.jobs_usage(0); fb, fn = P.clean_jobs(); b1, _ = P.jobs_usage(0)
        out("ลบไฟล์ชั่วคราวเก่ากว่า 2 วัน: %s (%d ไฟล์)  เหลือ %s ที่ %s" % (P.gb(fb), fn, P.gb(b1), P.J)); return 0
    if c == "rules" and len(a) > 1: out(card(a[1])); return 0
    if c == "do": return do("--dry" in a, "--force" in a)
    if c == "repair-cams": return repair_cams()
    if c == "repair-pose": return repair_pose(a[a.index("--said")+1] if "--said" in a and a.index("--said")+1<len(a) else "")
    if c == "repair" and len(a)==2:
        from preview_gate import dispatch,Blocked
        from workflow_state import invalidated_steps
        from cinematic_qa import read,write
        step=a[1];story=story_now();n=part_now(story)
        if step not in ("cast","pose","lip","scene_review","prop_review","camera_replan","cams","cam_check","editorial_review","video_check","final_review"):out("invalid repair step");return 2
        try:
            with dispatch():
                p=P.PROG/f"{story}_{n}.json";d=read(p);order=[k for k,_ in P.STEPS]
                for k in invalidated_steps(step,order):d.get("steps_done",{}).pop(k,None)
                d.get("ok",{}).pop("step5",None);d.pop("sleep_approval",None);d.pop("ready_menu_save",None);write(p,d);fails(step,False)
                PROG_NOW(story,n,step,"todo");out("OK invalidated repair; next do");return 0
        except Blocked as e:out(str(e));return 2
    if c == "sleep-status":
        from sleep_session import state
        out(json.dumps(state(ROOT),ensure_ascii=False,indent=2));return 0
    if c == "sleep-approve":
        from sleep_session import approve, SleepError
        from preview_gate import dispatch, Blocked
        try:
            with dispatch():
                approve(ROOT,story_now(),part_now(story_now())); out("OK: Sleep Mode QA authorization recorded separately"); return 0
        except (SleepError,Blocked) as e: out("STOP: "+str(e)); return 2
    if c == "range" and len(a) > 1: return set_range(a[1])
    if c == "approve":
        from sleep_session import state
        if state(ROOT).get("enabled"):out("Sleep Mode: use sleep-approve, or pause for manual approval");return 2
        said = a[a.index("--said") + 1] if "--said" in a and a.index("--said") + 1 < len(a) else ""
        return approve(said)
    if c == "use" and len(a) > 1:
        from sleep_session import state,save
        if state(ROOT).get("phase")=="paused":save(ROOT,{"enabled":False,"phase":"manual"})
        if state(ROOT).get("enabled"):out("Pause Sleep Mode before manual selection");return 2
        if a[1] not in P.stories(): out("FAIL: ไม่มีเรื่อง %s (มี: %s) -> %s new-story %s" % (a[1], ", ".join(P.stories()), CMD, a[1])); return 1
        save_sel({"story": a[1], "part": a[2] if len(a) > 2 else None}); show_status(); return 0
    if c == "new-story" and len(a) > 1:
        from sleep_session import state,save
        if state(ROOT).get("phase")=="paused":save(ROOT,{"enabled":False,"phase":"manual"})
        if state(ROOT).get("enabled"):out("Pause Sleep Mode before changing story");return 2
        rc = subprocess.run([PY, str(SCR / "ic8_story.py"), a[1], "init"], cwd=ROOT).returncode
        if rc == 0: save_sel({"story": a[1]})
        return rc
    if c == "doctor": return doctor()
    if c == "log":
        import ailog; out(ailog.show()); return 0
    if c == "motions":   # pick body motions per line from the whole library (scripts/motion_pool.py)
        pos = [x for x in a[1:] if not x.startswith('--')]
        st = pos[0] if len(pos) >= 2 else story_now(); pt = pos[1] if len(pos) >= 2 else (pos[0] if pos else part_now(st))
        return subprocess.run([PY, str(SCR / "motion_pool.py"), "pick", st, str(pt)] + [x for x in a if x == "--write"], cwd=ROOT).returncode
    if c == "video2motion" and len(a) > 1:
        return subprocess.run([PY, str(SCR / "video2motion.py")] + a[1:], cwd=ROOT).returncode
    out(__doc__); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
