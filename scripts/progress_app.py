# -*- coding: utf-8 -*-
"""Ai-iclone window (was "Preview"): the user's view of the same state `Ai-iclone.cmd` gives the AI as text
(scripts/ai_iclone.py imports the state functions below). Small white window, one dot per step of the current part, live.
Dots: green = done, blue spinning = running now, red = failed, grey = not yet.
Data: progress/now.json (running step), progress/<story>_<part>.json steps_done (written by ic8_part.py),
files on disk (spec, wav, project, video) and progress/now_log.txt (last lines the pipeline printed).
Click a grey "ผู้ใช้..." step to tick it.
Run: pythonw scripts/progress_app.py   (desktop shortcut: "Preview นิทาน")
"""
import json
import os
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from paths import expand

ROOT = Path(__file__).resolve().parent.parent
PROG = ROOT / "progress"
BG, TXT, SUB, LINE = "#ffffff", "#222222", "#888888", "#e6e6e6"
GREEN, BLUE, RED, GREY, AMBER = "#2ea043", "#1f6feb", "#d1242f", "#c8c8c8", "#bf8700"
F = ("Tahoma", 8)
SPIN = "◐◓◑◒"

# (key, Thai label). key = pipeline step name, or a check done here.
# Whole pipeline of one part, from the plan to a checked video (ic8_part.py writes every key except
# plan/audio/user_ok, which come from files / the user's click).
STEPS = [("plan", "วางแผนบท + กล้อง"), ("audio", "ตัดเสียงท่อน"), ("check", "ตรวจสเปกท่อน"),
         ("motion_plan", "วางแผนโมชั่น (ใครใช้ท่าอะไร)"),
         ("open", "โหลดฉาก (≤3 นาที)"), ("cast", "วางตัวละครรอบแลนด์มาร์ก (≤3 นาที)"),
         ("sound", "ใส่เสียงครั้งเดียว (≤3 นาที)"), ("pose", "รอเท็กซ์เจอร์ แล้วใส่ท่าทาง"), ("motion_check", "ตรวจโมชั่น (ไม่เดินถอย/ไม่กระตุก)"), ("lip", "ลิปซิงก์"),
         ("scene_review", "สำรวจฉากจริง + หลักฐานภาพ"), ("prop_review", "ตรวจ/สร้างพร็อพที่จำเป็น"), ("camera_replan", "วางแผนกล้องจากฉากจริง"),
         ("cams", "ตั้งกล้องตามบท + ไฟหน้า + ภาพนิ่ง"),
         ("cam_check", "AI ตรวจมุมกล้องทุกช็อต (รวมในรูปเดียว)"),
         ("light_check", "ตรวจแสงหน้า (ไม่ขาว/ดำครึ่งซีก)"),
         ("face_check", "ตรวจหน้าทุกตัว: ①กระพริบ ②ท่าหน้า 65-75% ③ความรู้สึก + รอยต่อคลิปห่างและไขว้ X (อ่านจาก iClone)"),
         ("editorial_review", "ตรวจจังหวะภาพรอบสอง"), ("switch", "เปลี่ยนวิวเป็นกล้อง Switch"), ("user_ok", "ผู้ใช้ตรวจ (ผ่าน)"),
         ("ready", "เตรียม Switch / เซฟเมนู (ไม่เปิดซ้ำ)"), ("render", "เรนเดอร์วิดีโอ"), ("video_check", "ตรวจไฟล์วิดีโอ"), ("final_review", "ตรวจภาพเคลื่อนไหวและเสียงจริง")]
# Story setup: done ONCE per story, before any part (user 2026-11-22). All read from the central sheet
# stories/<story>.json; nothing per part here.
STORY_STEPS = [("sheet", "ใบงานกลาง (เรื่องอะไร)"),          # user 2026-11-22: BIG picture only; details belong to each part
               ("source", "บท + เสียงเต็ม"),
               ("range", "เวลาที่ทำงาน (ผู้ใช้บอก)"),
               ("split", "ถอดเสียง + แบ่งท่อน"),
               ("chars", "ตัวละครทั้งเรื่อง"),
               ("scenes", "ฉากทั้งเรื่อง"),
               ("partplans", "เนื้อเรื่องแต่ละท่อน"),
               ("output", "ที่เก็บงาน (เซฟ + วิดีโอ)"),
               ("story_ok", "ผู้ใช้อนุมัติแผนเรื่อง")]
J = Path(os.environ.get("LOCALAPPDATA", "")) / "Tidmunz Studio" / "snapgen_data" / "ic8_jobs"
mm = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"


def parse_mmss(t):
    t = t.strip().replace(".", ":")
    if ":" in t: m, s = t.split(":", 1); return int(m) * 60 + float(s)
    return float(t) * 60


def story_states(story):
    """(state, info) per STORY_STEPS key. state: done / todo / warn / bad."""
    f = ROOT / "stories" / f"{story}.json"; st = load(f, {}); out = {}
    # user 2026-11-22: the sheet is work data, NOT backed up in git (git = the program only)
    out["sheet"] = ("done", "✓") if st else ("bad", "ไม่มีไฟล์")
    ok = lambda p: bool(p) and Path(expand(p)).exists()
    src = [ok(st.get("script_docx")), ok(st.get("master_audio"))]
    out["source"] = ("done", f"เสียงเต็ม {mm(st.get('master_len', 0))}") if all(src) else ("bad", "ไม่พบ " + " ".join(n for n, x in zip(("บท", "เสียง"), src) if not x))
    tr = st.get("teacher_range") or [0, 0]
    if tr[1] <= 0: out["range"] = ("todo", "คลิกเพื่อใส่")
    elif not st.get("teacher_range_confirmed"): out["range"] = ("warn", f"{mm(tr[0])}–{mm(tr[1])} ยังไม่ยืนยัน")
    else: out["range"] = ("done", f"{mm(tr[0])}–{mm(tr[1])} ({mm(tr[1] - tr[0])} นาที)")
    parts = [p for p in st.get("parts", []) if p.get("master")]
    if not parts or tr[1] <= 0: out["split"] = ("todo", "")
    else:
        inr = [p for p in parts if p["master"][0] < tr[1] - 0.5]; over = [p for p in parts if p["master"][0] >= tr[1] - 0.5]
        end = max(p["master"][1] for p in inr) if inr else 0
        gap = any(abs(a["master"][1] - b["master"][0]) > 0.5 for a, b in zip(inr, inr[1:]))
        avg = (end - tr[0]) / max(1, len(inr))
        if over: out["split"] = ("bad", f"{len(over)} ท่อนเกินเวลาที่ทำงาน")
        elif gap or abs(end - tr[1]) > 1.0: out["split"] = ("warn", f"{len(inr)} ท่อน ถึง {mm(end)} ≠ {mm(tr[1])}")
        else: out["split"] = ("done", f"{len(inr)} ท่อน ~{mm(avg)}/ท่อน")
    # user 2026-11-22: every part's audio is cut + transcribed, times exactly = the part's range in the master,
    # and every line says who speaks (narrator / which character -> lip sync)
    ad = expand(st.get("audio_dir", "")); good = []; why = ""; inr = []
    inr = [p for p in parts if tr[1] > 0 and p["master"][0] < tr[1] - 0.5]
    for p in inr:
        n = p["n"]; jf = Path(ad) / f"ท่อน{n}.json"; j = load(jf, {})
        if not (Path(ad) / f"ท่อน{n}.wav").exists() or not j.get("segments"): why = why or f"ท่อน {n} ยังไม่ถอด"; continue
        if abs(j.get("start", -9) - p["master"][0]) > 0.05 or abs(j.get("end", -9) - p["master"][1]) > 0.05:
            why = why or f"ท่อน {n} เวลาไม่ตรง"; continue
        if not p.get("transcript") or not all(l.get("who") for l in p["transcript"]): why = why or f"ท่อน {n} ไม่ระบุใครพูด"; continue
        good.append(n)
    if out["split"][0] == "done" and inr and len(good) < len(inr):
        out["split"] = ("warn", f"ถอดเสียง {len(good)}/{len(inr)} {why}")
    outs = [st.get("save_dir"), st.get("video_dir")]
    out["output"] = ("done", "✓") if all(ok(p) for p in outs) else ("todo", "ยังไม่ตั้ง/ไม่มีโฟลเดอร์")
    ch = st.get("characters", {}); miss = [n for n, c in ch.items() if not ok(c.get("avatar"))]
    out["chars"] = ("done", f"{len(ch)} ตัว") if ch and not miss else (("bad", "ไม่พบ: " + ", ".join(miss)[:30]) if ch else ("todo", ""))
    miss_c = miss
    sc = st.get("scenes", {}); miss = [n for n, c in sc.items() if not ok(c.get("file"))]
    out["scenes"] = ("done", f"{len(sc)} ฉาก") if sc and not miss else (("bad", "ไม่พบ: " + ", ".join(miss)[:30]) if sc else ("todo", ""))
    planned = [p for p in parts if p.get("content") and p.get("plan")]
    out["partplans"] = ("done" if parts and len(planned) == len(parts) else "todo", f"{len(planned)}/{len(parts)}")
    out["story_ok"] = ("done", "✓") if st.get("story_plan_ok") else ("todo", "คลิกเมื่อผ่าน")
    # user 2026-11-23: a REAL % on every row that is not done, counted from what is filled / found on disk
    frac = lambda a, b: round(100 * a / b) if b else 0
    pct = {"sheet": frac(sum(1 for k in ("name", "folder") if st.get(k)), 2), "source": frac(sum(src), 2),
           "range": 0 if tr[1] <= 0 else (50 if not st.get("teacher_range_confirmed") else 100),
           "split": frac(len(good), len(inr)) if parts and tr[1] > 0 else 0,
           "chars": frac(len(ch) - len(miss_c), len(ch)), "scenes": frac(len(sc) - len(miss), len(sc)),
           "partplans": frac(len(planned), len(parts)), "output": frac(sum(1 for p in outs if ok(p)), 2)}
    for k, v in pct.items():
        if out[k][0] != "done": out[k] = (out[k][0], ("%d%%  " % v) + out[k][1])
    return out
LOAD_STEPS = {"open", "cast", "sound"}   # user 2026-11-21: each load must finish within 3 minutes


def load(p, d):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return d


_usage = {"t": 0, "v": (0, 0)}


def jobs_usage(max_age=60):
    """(bytes, files) in the iClone work folder ic8_jobs (stills, logs, previews, old backups). Cached 60 s.
    User 2026-11-22: temp files must be visible in the program, never a hidden pile."""
    if time.time() - _usage["t"] > max_age:
        n = b = 0
        for dp, _, fs in os.walk(J):
            for f in fs:
                try: b += os.path.getsize(os.path.join(dp, f)); n += 1
                except OSError: pass
        _usage.update(t=time.time(), v=(b, n))
    return _usage["v"]


def clean_jobs(days=2):
    """Delete temp files in ic8_jobs older than `days` days (all of the old backup\\ folder at once).
    Never a queued job (run\\*.py) or anything newer. Returns (bytes freed, files)."""
    cut = time.time() - days * 86400; b = n = 0
    for dp, _, fs in os.walk(J, topdown=False):
        rel = os.path.relpath(dp, J).lower()
        for f in fs:
            p = os.path.join(dp, f)
            if rel == "run" and f.lower().endswith(".py"): continue
            try:
                st = os.stat(p)
                if rel.startswith("backup") or st.st_mtime < cut:
                    os.remove(p); b += st.st_size; n += 1
            except OSError: pass
        if dp != str(J) and rel not in ("run",):
            try: os.rmdir(dp)   # only if empty
            except OSError: pass
    _usage["t"] = 0
    return b, n


def gb(b):
    return "%.1f GB" % (b / 1e9) if b >= 1e8 else "%d MB" % (b / 1e6)


def load_text(p):
    try:
        return Path(p).read_text(encoding="utf-8").strip()
    except Exception:
        return ""


NO_STORY = ("ยังไม่มีเรื่องในเครื่องนี้\n\n"
            "บอก AI (ChatGPT / Claude) ว่า\n\"วันนี้ทำเรื่อง <ชื่อเรื่อง>\"\n"
            "แล้วส่งบท (.docx) กับไฟล์เสียงเต็มให้มัน\n\n"
            "พอมีเรื่องแล้ว หน้าต่างนี้จะแสดงขั้นตอนเองทันที")


def stories():
    return sorted(p.stem for p in (ROOT / "stories").glob("*.json") if not p.stem.startswith("_"))


def parts_of(story):
    # Parts come from story.json AND parts/<story>_<n>.json, and when every part has its video the
    # next number is shown too (all grey) - a new part appears by itself (user 2026-11-21).
    s = load(ROOT / "stories" / f"{story}.json", {})
    ns = {str(p.get("n")) for p in s.get("parts", [])}
    ns |= {p.stem[len(story) + 1:] for p in (ROOT / "parts").glob(f"{story}_*.json")}
    import re
    ps = sorted((n for n in ns if re.fullmatch(r"\d+(?:\.\d+)?", n)), key=lambda n: tuple(map(int,n.split("."))))
    return ps or ["1"]


def spec_of(story, n):
    return load(ROOT / "parts" / f"{story}_{n}.json", None)


def video_done(spec):
    return bool(spec and spec.get("video") and Path(expand(spec["video"])).exists())


def current_part(story):
    now = load(PROG / "now.json", {})
    ps = parts_of(story)
    from workflow_state import selected_target
    target=selected_target(ROOT,story)
    if target and target["part"] in ps:return target["part"]
    if now.get("story") == story and time.time() - now.get("time", 0) < 3 * 3600:
        n = str(now.get("part"))
        # finished part (video checked) -> move on: the next part starts with every dot grey
        if not (now.get("step") == "final_review" and now.get("state") == "done" and n in ps and ps.index(n) + 1 < len(ps)):
            return n
        return ps[ps.index(n) + 1]
    from sleep_session import complete
    return next((n for n in ps if not complete(ROOT,story,n)), ps[-1] if ps else "1")


def plan_complete(spec):
    """The part plan is done only when the spec is filled: every line has a speaker and there are shots
    (a fresh `ic8_story.py new` skeleton has who "?" and no shots)."""
    return bool(spec and spec.get("shots") and spec.get("lines")
                and all(L.get("who") and L.get("who") != "?" for L in spec["lines"]))


def ai_pct(story, n, k):
    """REAL % of an AI step, counted from what is already filled in its file (user 2026-11-23: % on every row that can
    have one). (pct, text) or None."""
    spec = spec_of(story, n) or {}
    if k == "plan":
        L = spec.get("lines", []); cast = spec.get("cast", {}) or {}; shots = spec.get("shots", [])
        st = load(ROOT / "stories" / f"{story}.json", {})
        p = next((x for x in st.get("parts", []) if str(x.get("n")) == str(n)), {})
        length = (p["master"][1] - p["master"][0]) if p.get("master") else max([l["t"][1] for l in L if l.get("t")] or [0])
        who = sum(1 for l in L if l.get("who") and l["who"] != "?")
        placed = sum(1 for c in cast.values() if isinstance(c, dict) and (c.get("spot") or c.get("pos")) and (c.get("motion") or c.get("motions")))
        cover = min(1.0, max([sh["t"][1] for sh in shots if sh.get("t")] or [0]) / length) if length else 0
        parts = [who / len(L) if L else 0, placed / len(cast) if cast else 0, cover]
        return round(100 * sum(parts) / 3), "ใครพูด %d/%d บรรทัด · วางตัวละคร %d/%d · กล้อง %d ช็อต ถึง %.0f/%.0f วิ" % (
            who, len(L), placed, len(cast), len(shots), cover * length, length)
    if k == "cam_check":   # every answer counts: "see" + each true/false question, per shot
        shots = spec.get("shots", []); ck = load(PROG / f"{story}_{n}_camcheck.json", {})
        qs = ck.get("questions", []) if isinstance(ck, dict) else []
        if not qs:
            try: from cam_check import ASK as qs
            except Exception: qs = []
        rows = ck.get("shots", []) if isinstance(ck, dict) else []
        if not shots: return None
        tot = len(shots) * (1 + len(qs)) or 1
        got = sum((len(str(e.get("see", "")).strip()) >= 10) + sum(e.get(q) is not None for q in qs) for e in rows)
        full = sum(1 for e in rows if len(str(e.get("see", "")).strip()) >= 10 and all(e.get(q) is not None for q in qs))
        return round(100 * got / tot), "ตอบครบ %d/%d ช็อต (%d/%d คำตอบ)" % (full, len(shots), got, tot)
    return None


def step_states(story, n):
    spec = spec_of(story, n)
    st = load(PROG / f"{story}_{n}.json", {})
    done = st.get("steps_done", {})
    ok = st.get("ok", {})
    now = load(PROG / "now.json", {})
    live = now if now.get("story") == story and str(now.get("part")) == n and time.time() - now.get("time", 0) < 3 * 3600 else {}
    narr_only = bool(spec) and all(L.get("who") in ("บรรยาย", "narrator") for L in spec.get("lines", []))
    from sleep_session import complete
    legacy_complete = "scene_review" not in done and bool(ok.get("step5")) and "video_check" in done and "render" in done and complete(ROOT,story,n)
    out = {}
    for k, _ in STEPS:
        if legacy_complete and k in ("scene_review","prop_review","camera_replan","editorial_review","final_review"): s = "skip"
        elif k == "plan": s = "done" if plan_complete(spec) else "todo"
        elif k == "audio": s = "done" if spec and Path(expand(spec.get("wav", ""))).exists() else "todo"
        elif k == "sound":
            from workflow_state import source_changed
            s = "done" if k in done and spec and not source_changed(st.get("sound_source"), expand(spec.get("wav", ""))) else "todo"
        elif k == "motion_plan": s = "done" if k in done else "todo"
        elif k == "user_ok":
            from sleep_session import approval_valid
            s = "done" if ok.get("step5") or approval_valid(ROOT,story,n,st) or ("render" in done and "ready" in done and video_done(spec)) else "todo"
        elif k == "render": s = "done" if k in done and video_done(spec) else "todo"
        elif k == "lip" and narr_only: s = "skip"
        else: s = "done" if k in done else "todo"
        if live.get("step") == k:
            s = {"running": "run", "failed": "fail"}.get(live.get("state"), s)
        out[k] = s
    return out, live


_SEND = [0.0, ""]
def send_status():
    """Image-to-chat state (user 2026-11-28: images silently never arrived). Cached 5 s: it pings the relay."""
    if time.time() - _SEND[0] > 5:
        try:
            import sys
            sys.path.insert(0, str(ROOT / "tools" / "chrome_preview_bridge"))
            import queue_preview
            _SEND[1] = queue_preview.status_line()
        except Exception:
            _SEND[1] = ""
        _SEND[0] = time.time()
    return _SEND[1]


def start_relay():
    """Opening the Preview window brings the image/Goal Tracker relay up too (background, never blocks the window)."""
    import threading
    def go():
        try:
            import sys
            sys.path.insert(0, str(ROOT / "tools" / "chrome_preview_bridge"))
            import queue_preview
            queue_preview.ensure_relay()
        except Exception:
            pass
    threading.Thread(target=go, daemon=True).start()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ai-iclone " + load_text(ROOT / "VERSION"))
        self.geometry("330x770+0+0")   # small (user 2026-11-24: "ใหญ่เกินไป")   # top-left of the screen (user 2026-11-21)
        self.minsize(220, 300)
        self.attributes("-topmost", True)
        self.configure(bg=BG)
        st = ttk.Style(self)
        try: st.theme_use("clam")
        except Exception: pass
        st.configure("TCombobox", fieldbackground=BG, background=BG)
        top = tk.Frame(self, bg=BG); top.pack(fill="x", padx=8, pady=(6, 2))
        self.story = tk.StringVar(value=(stories() or [""])[-1])
        try:
            line = next(l for l in (ROOT / "docs" / "CURRENT_STORY.md").read_text(encoding="utf-8").splitlines() if l.startswith("- เรื่อง:"))
            name = line.split(":", 1)[1].split("/")[0].strip()
            if name in stories(): self.story.set(name)
        except Exception:
            pass
        self.combo = ttk.Combobox(top, textvariable=self.story, values=stories(), state="readonly", font=F, width=22)
        self.combo.pack(fill="x")
        self.story.trace_add("write", lambda *_: self.rebuild())
        # two pages, never mixed (user 2026-11-22): story setup (once per story) / one part at a time
        tabs = tk.Frame(self, bg=BG); tabs.pack(fill="x", padx=8, pady=(4, 2))
        self.tab_story = tk.Label(tabs, font=("Tahoma", 8, "bold"), padx=8, pady=3, cursor="hand2")
        self.tab_part = tk.Label(tabs, font=("Tahoma", 8, "bold"), padx=8, pady=3, cursor="hand2")
        self.tab_story.pack(side="left", fill="x", expand=True); self.tab_part.pack(side="left", fill="x", expand=True)
        self.tab_story.bind("<Button-1>", lambda e: self.set_page("story")); self.tab_part.bind("<Button-1>", lambda e: self.set_page("part"))
        # ONE progress bar for the whole page (user 2026-11-24: "โหลดที่ช่องเดียว" - no bar per step)
        bar = tk.Frame(self, bg=BG); bar.pack(fill="x", padx=8, pady=(4, 2))
        self.bar_txt = tk.Label(bar, bg=BG, fg=TXT, font=("Tahoma", 10, "bold"), anchor="w"); self.bar_txt.pack(fill="x")
        self.bar = tk.Canvas(bar, height=8, bg="#e6e6e6", highlightthickness=0); self.bar.pack(fill="x", pady=(3, 0))
        self.page = None   # None = automatic: story setup until it is approved / parts have started, then parts
        self.pstory = tk.Frame(self, bg=BG)
        self.shead = tk.Label(self.pstory, bg=BG, fg=TXT, font=("Tahoma", 8, "bold"), anchor="w")
        self.shead.pack(fill="x", pady=(6, 4))
        self.slist = tk.Frame(self.pstory, bg=BG); self.slist.pack(fill="x")
        self.srows = {}
        for k, label in STORY_STEPS:
            r = tk.Frame(self.slist, bg=BG); r.pack(fill="x", pady=1)
            dot = tk.Label(r, text="●", bg=BG, fg=GREY, font=("Segoe UI Symbol", 8), width=2); dot.pack(side="left")
            txt = tk.Label(r, text=label, bg=BG, fg=SUB, font=F, anchor="w"); txt.pack(side="left", fill="x", expand=True)
            info = tk.Label(r, text="", bg=BG, fg=SUB, font=("Tahoma", 8)); info.pack(side="right")
            if k in ("range", "story_ok"):
                for w in (dot, txt, info): w.configure(cursor="hand2"); w.bind("<Button-1>", lambda e, k=k: self.story_click(k))
            self.srows[k] = (dot, txt, info)
        self.ppart = tk.Frame(self, bg=BG)
        self.head = tk.Label(self.ppart, bg=BG, fg=SUB, font=("Tahoma", 8), anchor="w", justify="left", wraplength=310)
        self.head.pack(fill="x", pady=(6, 0))
        self.chips = tk.Frame(self.ppart, bg=BG); self.chips.pack(fill="x", pady=(2, 6))
        tk.Frame(self.ppart, bg=LINE, height=1).pack(fill="x")
        self.list = tk.Frame(self.ppart, bg=BG); self.list.pack(fill="x", pady=4)
        # small log box at the bottom: the last 2 lines of what runs now (user 2026-11-24: "1-2 แถวก็พอ")
        self.sep = tk.Frame(self, bg=LINE, height=1)
        self.logbox = tk.Frame(self, bg="#f6f8fa", highlightbackground=LINE, highlightthickness=1)
        tk.Label(self.logbox, text="บันทึกงาน", bg="#f6f8fa", fg=TXT, font=("Tahoma", 8, "bold"), anchor="w").pack(fill="x", padx=6, pady=(3, 0))
        self.log = tk.Label(self.logbox, bg="#f6f8fa", fg=BLUE, font=("Consolas", 8), anchor="nw", justify="left", height=2, wraplength=300)
        self.log.pack(fill="x", padx=6, pady=(0, 4))
        self.logbox.pack(side="bottom", fill="x", padx=8, pady=6)
        self.log.bind("<Configure>", lambda e: self.log.configure(wraplength=max(120, e.width - 4)))
        self.tick_n = 0
        self.rows = {}
        self.subs = {}
        self.rebuild()
        self.loop()

    def rebuild(self):
        self.rows.clear(); self.subs = {}
        for w in self.list.winfo_children(): w.destroy()
        for k, label in STEPS:
            r = tk.Frame(self.list, bg=BG); r.pack(fill="x", pady=0)
            dot = tk.Label(r, text="●", bg=BG, fg=GREY, font=("Segoe UI Symbol", 8), width=2)
            dot.pack(side="left")
            # +/- fold of the detail lines (user 2026-11-22: minimal screen; finished details stay folded)
            tog = tk.Label(r, text="", bg=BG, fg=SUB, font=("Consolas", 9, "bold"), width=2, cursor="hand2")
            tog.pack(side="left"); tog.bind("<Button-1>", lambda e, k=k: self.toggle(k))
            txt = tk.Label(r, text=label, bg=BG, fg=SUB, font=F, anchor="w")
            txt.pack(side="left", fill="x", expand=True)
            info = tk.Label(r, text="", bg=BG, fg=SUB, font=("Tahoma", 8))
            info.pack(side="right")
            if k == "user_ok":
                for w in (dot, txt): w.bind("<Button-1>", lambda e: self.tick_ok())
            # detail under the row: motion plan / live % bar + what the job is doing now
            sub = tk.Label(self.list, text="", bg=BG, fg=SUB, font=("Tahoma", 8), anchor="w", justify="left", wraplength=280)
            self.rows[k] = (dot, txt, info)
            self.subs[k] = (r, sub, tog)
        self.refresh()

    def toggle(self, k):
        op = getattr(self, "opened", set())
        op.symmetric_difference_update({k}); self.opened = op; self.refresh()

    def set_page(self, pg):
        self.page = pg; self.refresh()

    def story_click(self, k):
        f = ROOT / "stories" / f"{self.story.get()}.json"; st = load(f, None)
        if st is None: return
        if k == "range":   # the user types the teacher's range; never guessed (rules.md)
            from tkinter import simpledialog, messagebox
            tr = st.get("teacher_range") or [0, 0]
            v = simpledialog.askstring("เวลาที่ทำงาน", "เรื่องนี้ทำงานช่วงเวลาไหนของเสียงเต็ม (นาที:วินาที)\nเช่น 0:00-5:10",
                                       initialvalue=f"{mm(tr[0])}-{mm(tr[1])}", parent=self)
            if not v: return
            try:
                a, b = (parse_mmss(x) for x in v.replace("–", "-").split("-", 1))
                assert 0 <= a < b
            except Exception:
                messagebox.showerror("เวลาที่ทำงาน", "อ่านไม่ออก: " + v, parent=self); return
            st["teacher_range"] = [round(a, 2), round(b, 2)]; st["teacher_range_confirmed"] = time.strftime("%Y-%m-%d %H:%M user")
        else:
            st["story_plan_ok"] = time.strftime("%Y-%m-%d %H:%M user")
        f.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
        self.refresh()

    def tick_ok(self):
        story = self.story.get(); n = current_part(story)
        from sleep_session import state
        if state(ROOT).get("enabled"):return
        states,_=step_states(story,n)
        if next((k for k,_ in STEPS if states[k] not in ("done","skip")),None)!="user_ok":return
        f = PROG / f"{story}_{n}.json"
        d = load(f, {"ok": {}, "orders": []}); d.setdefault("ok", {})["step5"] = True
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        self.refresh()

    def refresh(self):
        story = self.story.get()
        if not story:   # fresh install: no story yet (user 2026-11-23: the window was blank and looked broken)
            have = stories()
            if have:
                self.log.configure(fg=BLUE, font=("Consolas", 8), height=2, text="")
                self.combo.configure(values=have); self.story.set(have[-1]); return
            self.log.configure(fg=TXT, font=F, height=0, text=NO_STORY)
            return
        n = current_part(story)
        states, live = step_states(story, n)
        ndone = sum(1 for s in states.values() if s in ("done", "skip"))
        st = load(ROOT / "stories" / f"{story}.json", {})   # user 2026-11-22: real numbers from the central sheet (story.json teacher_range)
        tr = st.get("teacher_range") or [0, 0]; mm = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
        inr = [p for p in st.get("parts", []) if p.get("master") and p["master"][0] < tr[1] - 0.5]
        txt = f"ท่อน {n} จาก {len(inr)}   เวลาที่ทำงาน {mm(tr[0])}–{mm(tr[1])}" if tr[1] > 0 else f"ท่อน {n}   (ยังไม่ได้ใส่เวลาที่ทำงาน)"
        cur = next((p for p in st.get("parts", []) if str(p.get("n")) == str(n)), None)
        if cur and tr[1] > 0 and cur.get("master", [0])[0] >= tr[1] - 0.5: txt += "   ⚠ ท่อนนี้เกินเวลาที่ทำงาน"
        b, _ = jobs_usage()
        txt += "   ไฟล์ชั่วคราว %s%s" % (gb(b), "  ⚠ สั่ง Ai-iclone clean" if b > 5e9 else "")
        from repair_queue import lines as repair_lines
        checks=repair_lines(PROG,story,n)
        if checks: txt += "\n" + "\n".join(checks)
        send = send_status()
        if send: txt += "\n" + send
        self.head.configure(text=txt)
        ss = story_states(story); sdone = sum(1 for s, _ in ss.values() if s == "done")
        allok = sdone == len(STORY_STEPS)
        started = any(spec_of(story, p) for p in parts_of(story))   # parts already being made -> part page
        pg = self.page or ("part" if allok or ss["story_ok"][0] == "done" or started else "story")
        self.shead.configure(text=f"เตรียมเรื่อง (ทำครั้งเดียว)   {sdone}/{len(STORY_STEPS)}" + ("  ✓" if allok else ""), fg=GREEN if allok else TXT)
        for tab, key, label in ((self.tab_story, "story", f"① เตรียมเรื่อง {sdone}/{len(STORY_STEPS)}"), (self.tab_part, "part", f"② ทำทีละท่อน  ท่อน {n}")):
            on = pg == key
            tab.configure(text=label, bg=BLUE if on else "#eeeeee", fg="#fff" if on else (AMBER if key == "story" and not allok else SUB))
        show, hide = (self.pstory, self.ppart) if pg == "story" else (self.ppart, self.pstory)
        if getattr(self, "_shown", None) != pg:   # repack only on a page change (no flicker every tick)
            self._shown = pg
            hide.pack_forget(); show.pack(fill="both", expand=True, padx=8)
        col = {"done": GREEN, "todo": GREY, "warn": AMBER, "bad": RED}
        for k, _ in STORY_STEPS:
            s, inf = ss[k]; dot, t, info = self.srows[k]
            dot.configure(text="●" if s == "done" else "○", fg=col[s]); t.configure(fg=TXT if s == "done" else (col[s] if s != "todo" else SUB))
            info.configure(text=inf, fg=col[s] if s != "todo" else SUB)
        for w in self.chips.winfo_children(): w.destroy()
        for p in parts_of(story):
            fin = video_done(spec_of(story, p))
            tk.Label(self.chips, text=f" {p} ", font=("Tahoma", 8), padx=2,
                     bg=GREEN if fin else (BLUE if p == n else "#eeeeee"),
                     fg="#fff" if fin or p == n else SUB).pack(side="left", padx=1)
        first_todo = next((k for k, _ in STEPS if states[k] == "todo"), None)
        for k, label in STEPS:
            dot, txt, info = self.rows[k]; s = states[k]
            if s == "done": dot.configure(text="●", fg=GREEN); txt.configure(fg=TXT, font=F); info.configure(text="✓", fg=GREEN)
            elif s == "skip": dot.configure(text="●", fg=LINE); txt.configure(fg=SUB, font=F); info.configure(text="ไม่มีบทพูด", fg=SUB)
            elif s == "run":
                secs = int(time.time() - live.get("time", time.time()))
                dot.configure(text=SPIN[self.tick_n % 4], fg=BLUE); txt.configure(fg=BLUE, font=("Tahoma", 8, "bold"))
                late = k in LOAD_STEPS and secs > 180   # over the 3-minute load limit: must be looked at now
                lv = load(J / "live.json", {})
                info.configure(text=f"{'เกิน 3 นาที! ' if late else ''}{secs // 60}:{secs % 60:02d}", fg=RED if late else BLUE)
            elif s == "fail": dot.configure(text="●", fg=RED); txt.configure(fg=RED, font=("Tahoma", 8, "bold")); info.configure(text="ล้มเหลว", fg=RED)
            else:
                nxt = k == first_todo and live.get("state") != "running"
                dot.configure(text="○", fg=AMBER if nxt else GREY)
                txt.configure(fg=AMBER if nxt else SUB, font=("Tahoma", 8, "bold") if nxt else F)
                info.configure(text=("คลิกเมื่อผ่าน" if k == "user_ok" else "ถัดไป") if nxt else "", fg=AMBER)
        # detail lines under rows
        lv = load(J / "live.json", {})
        plan = load(PROG / f"{story}_{n}_motions.json", [])
        for k, (row, sub, tog) in self.subs.items():
            text, col = "", SUB
            if states[k] == "run" and lv.get("step") == k and time.time() - lv.get("time", 0) < 600:
                text = str(lv.get("text", ""))[:60]; col = BLUE      # what it does now; the % is in the ONE bar on top
            elif states[k] == "todo" and k == first_todo and ai_pct(story, n, k):
                text = ai_pct(story, n, k)[1]; col = AMBER
            elif k == "motion_plan" and plan:
                text = chr(10).join(("⚠ " if m.get("warn") or not m.get("ok") else "   ") + f"{m['who']} ← {m['motion']} ×{m['speed']}" + (f"  หน้า: {m['face']}" if m.get('face') else "") for m in plan)
                col = AMBER if any(m.get("warn") or not m.get("ok") for m in plan) else SUB
            running = states[k] == "run"
            show = bool(text) and (running or col == AMBER and k == first_todo or k in getattr(self, "opened", set()))
            tog.configure(text="" if not text or running else ("−" if show else "+"), fg=AMBER if col == AMBER else SUB)
            if show:
                sub.configure(text=text, fg=col); sub.pack(fill="x", padx=(26, 0), after=row)
            else:
                sub.pack_forget()
        if pg == "story":
            nd, tot, part = sdone, len(STORY_STEPS), 0.0
        else:
            nd, tot = ndone, len(STEPS); part = 0.0
            run = next((k for k, _ in STEPS if states[k] == "run"), None)
            if run and lv.get("step") == run and time.time() - lv.get("time", 0) < 600: part = max(0, min(100, int(lv.get("pct", 0)))) / 100
            elif first_todo and ai_pct(story, n, first_todo): part = ai_pct(story, n, first_todo)[0] / 100
        self.draw_bar(nd, tot, part, any(v == "fail" for v in states.values()) and pg != "story")
        try:
            lines = (PROG / "now_log.txt").read_text(encoding="utf-8").splitlines()[-2:] if live else []
        except Exception:
            lines = []
        self.log.configure(text="\n".join(l[:70] for l in lines))

    def draw_bar(self, nd, tot, part, failed):
        p = round(100 * min(tot, nd + part) / max(1, tot))
        self.bar_txt.configure(text=f"{nd}/{tot} ขั้น · {p}%", fg=RED if failed else TXT)
        self.bar.update_idletasks(); w = self.bar.winfo_width()
        self.bar.delete("all")
        if p: self.bar.create_rectangle(0, 0, max(2, w * p / 100), 8, fill=RED if failed else (GREEN if p >= 100 else BLUE), width=0)

    def loop(self):
        self.tick_n += 1
        if self.tick_n % 4 == 0:
            self.refresh()
        else:   # only spin the running dot between full refreshes
            for k, (dot, _, _) in self.rows.items():
                if dot.cget("text") in SPIN: dot.configure(text=SPIN[self.tick_n % 4])
        if self.tick_n % 5 == 0 and self.state() == "normal":   # stay on top of every window until the user minimises it
            self.attributes("-topmost", True); self.lift()
        self.after(400, self.loop)


if __name__ == "__main__":
    start_relay()
    App().mainloop()
