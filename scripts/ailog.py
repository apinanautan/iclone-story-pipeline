# -*- coding: utf-8 -*-
"""ailog.py - real progress + a fail report any AI (GPT) can read (user 2026-11-23: "show real %, which step broke,
when; screen text + log + timing for GPT, no more blind waiting").

  progress/now_log.txt   every line: clock, +seconds since the step started, text
  ic8_jobs/live.json     {step, pct, text, time}  (the Preview window shows % + text)
  progress/last_fail.txt the fail report: command, step, how long, iClone windows' text, screenshot, last log lines
  Ai-iclone log          prints all of that
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROG = os.path.join(ROOT, "progress")
LOG = os.path.join(PROG, "now_log.txt")
FAILF = os.path.join(PROG, "last_fail.txt")
J = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tidmunz Studio", "snapgen_data", "ic8_jobs")
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
T0 = {"step": "", "t": time.time()}   # the step now running and when it started


def start(step):
    T0["step"], T0["t"] = step, time.time()


def log(s, echo=True):
    s = str(s)
    if echo: print(s, flush=True)
    if not s.strip(): return
    try:
        os.makedirs(PROG, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s +%5.0fs %s\n" % (time.strftime("%H:%M:%S"), time.time() - T0["t"], s.strip().splitlines()[0][:160]))
    except Exception: pass


_last, _pct = {}, {}
def wait(step, text):
    """waiting for iClone/another program: keep the step's real % (never fake it), show what we wait for + seconds."""
    try:
        with open(os.path.join(J, "live.json"), "w", encoding="utf-8") as f:
            json.dump({"step": step, "pct": round(_pct.get(step, 0)), "text": text, "time": time.time() - 4}, f, ensure_ascii=False)
    except Exception: pass


def live(step, pct, text):
    """real % of one step (e.g. 3 of 7 characters = 43%). Logs a line each time it crosses 10 %."""
    pct = max(0, min(100, pct)); _pct[step] = pct
    try:
        os.makedirs(J, exist_ok=True)
        with open(os.path.join(J, "live.json"), "w", encoding="utf-8") as f:
            json.dump({"step": step, "pct": round(pct), "text": text, "time": time.time()}, f, ensure_ascii=False)
    except Exception: pass
    k = int(pct // 10)
    if _last.get(step) != k or pct >= 100:
        _last[step] = k; log("[%3d%%] %s: %s" % (pct, step, text))


def count(step, i, n, text):
    """i of n done -> live %"""
    live(step, 100.0 * i / max(n, 1), "%d/%d %s" % (i, n, text))


def windows_text():
    """text of every iClone window that is not the main one (dialogs, popups) via UI Automation (no OCR guess)."""
    ps = ("Add-Type -AssemblyName UIAutomationClient; $A=[Windows.Automation.AutomationElement];"
          "$p=(Get-Process iClone -ErrorAction SilentlyContinue).Id; if(-not $p){'iClone is NOT running'; exit};"
          "$A::RootElement.FindAll('Children',[Windows.Automation.Condition]::TrueCondition)|"
          "?{$_.Current.ProcessId -eq $p -and $_.Current.Name -notmatch '^iClone 8 - '}|%{ $_.Current.Name + ': ' + "
          "(($_.FindAll('Descendants',[Windows.Automation.Condition]::TrueCondition)|%{$_.Current.Name}|?{$_}|select -first 40)-join ' | ') }")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30, creationflags=NOWIN)
        return r.stdout.strip() or "no iClone dialog open"
    except Exception as e:
        return "could not read windows: %s" % e


def _grab(p, half):
    ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing; $v=[System.Windows.Forms.SystemInformation]::VirtualScreen;"
          "$b=New-Object System.Drawing.Bitmap $v.Width,$v.Height; [System.Drawing.Graphics]::FromImage($b).CopyFromScreen($v.X,$v.Y,0,0,$b.Size);"
          + ("$b=New-Object System.Drawing.Bitmap $b,([int]($v.Width/2)),([int]($v.Height/2));" if half else "")
          + "$b.Save('%s',[System.Drawing.Imaging.ImageFormat]::%s)" % (p, "Jpeg" if half else "Png"))
    try: subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=30, creationflags=NOWIN)
    except Exception: pass
    return os.path.isfile(p)


def _rapid(img):
    """OCR for a PC whose Windows has no OCR language: rapidocr (CPU, any PC), installed once by itself (user 2026-11-23)."""
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        log("OCR: Windows has no OCR language on this PC -> installing rapidocr once (~60 MB)")
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--disable-pip-version-check", "rapidocr_onnxruntime"],
                           capture_output=True, text=True, timeout=900, creationflags=NOWIN)
        if r.returncode: return "OCR install failed: " + (r.stderr.strip().splitlines() or ["?"])[-1]
        import site, importlib; importlib.invalidate_caches(); sys.path.append(site.getusersitepackages())
        from rapidocr_onnxruntime import RapidOCR
    res, _ = RapidOCR()(img)
    return "\n".join(x[1] for x in (res or []))


def ocr_screen():
    """read the WHOLE screen fresh (full size), return its text, delete the image at once (no junk files)."""
    p = os.path.join(PROG, "_ocr_now.png")
    try:
        if not _grab(p, False): return "screenshot failed"
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                os.path.join(ROOT, "scripts", "ocr.ps1"), p], capture_output=True, text=True, timeout=60,
                               encoding="utf-8", errors="replace", creationflags=NOWIN)
            t = r.stdout.strip()
        except Exception as e: t = "NO_OCR_LANGUAGE (%s)" % e
        if t.startswith("NO_OCR_LANGUAGE"): t = _rapid(p)
        return " | ".join(l.strip() for l in t.splitlines() if len(l.strip()) > 2)[:1500] or "(no text on screen)"
    except Exception as e:
        return "OCR failed: %s" % e
    finally:
        try: os.remove(p)
        except OSError: pass


def screen(tag="wait"):
    """what is on screen now = iClone dialogs (UI Automation) + OCR of the whole screen. No file left behind."""
    return "iClone windows: %s || OCR: %s" % (windows_text(), ocr_screen())


def screenshot(tag="fail"):
    """FAIL only: half-size picture for GPT -> progress/fails/. Deleted when the step passes (clean_fails)."""
    d = os.path.join(PROG, "fails"); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):   # only the newest fail picture is kept
        try: os.remove(os.path.join(d, f))
        except OSError: pass
    p = os.path.join(d, time.strftime("%Y%m%d_%H%M%S_") + tag + ".jpg")
    return p if _grab(p, True) else "screenshot failed"


def clean_fails():
    """the step passed: its fail picture and report are not needed any more."""
    d = os.path.join(PROG, "fails")
    for f in (os.listdir(d) if os.path.isdir(d) else []):
        try: os.remove(os.path.join(d, f))
        except OSError: pass
    try: os.remove(FAILF)
    except OSError: pass


def tail(n=25):
    try:
        with open(LOG, encoding="utf-8") as f: return f.read().splitlines()[-n:]
    except OSError: return []


def fail_report(msg, iclone=True):
    """write + return the report GPT reads to fix the real cause (not a guess)."""
    secs = time.time() - T0["t"]
    lines = ["FAIL REPORT %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
             "command : %s" % " ".join(os.path.basename(a) if i == 0 else a for i, a in enumerate(sys.argv)),
             "step    : %s  (failed after %.0f s)" % (T0["step"] or "?", secs),
             "error   : %s" % msg]
    if iclone:
        lines += ["screen now: %s" % screen(), "screenshot (deleted when this step passes): %s" % screenshot(T0["step"] or "fail")]
    lines += ["last log lines (clock, +seconds in the step):"] + ["  " + l for l in tail()]
    txt = "\n".join(lines)
    try:
        with open(FAILF, "w", encoding="utf-8") as f: f.write(txt + "\n")
    except Exception: pass
    return txt


def show():
    """Ai-iclone log: what runs now, its %, the log, the last fail."""
    out = []
    try: now = json.load(open(os.path.join(PROG, "now.json"), encoding="utf-8"))
    except Exception: now = {}
    if now:
        out.append("NOW: %s part %s step %s = %s (%.0f s ago)" % (now.get("story"), now.get("part"), now.get("step"),
                                                               now.get("state"), time.time() - now.get("time", 0)))
    try:
        lv = json.load(open(os.path.join(J, "live.json"), encoding="utf-8"))
        out.append("LIVE: %s %s%% %s (%.0f s ago)" % (lv.get("step"), lv.get("pct"), lv.get("text"), time.time() - lv.get("time", 0)))
    except Exception: pass
    out += ["LOG (clock, +seconds in the step):"] + ["  " + l for l in tail(40)]
    if os.path.isfile(FAILF):
        out += ["", open(FAILF, encoding="utf-8").read().strip()]
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(show())
