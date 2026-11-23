"""cut_audio.py - cut one part out of a story's master audio by time, at real silences, and transcribe it.

  python scripts/cut_audio.py <master.wav|mp3> <start> <end> <out.wav> [--no-text] [--allow-download]
  start/end: seconds or m:ss (e.g. 4:15 5:15). Each edge snaps to the nearest silence within +-3 s.
  Writes out.wav (48 kHz, same channels) and out.json {src, start, end, len, segments:[{t:[a,b], text}]}
  (times in the json are LOCAL to out.wav). Transcript (Thai, for TIMING): Tidmunz's whisper.cpp large-v3 if on the PC, else faster-whisper: GPU large-v3-turbo / CPU small.
  Downloads a model only with --allow-download.
Read-only on the master (G: is fine to read). Allowed for every AI without asking (user 2026-11-17).
"""
import json, os, re, subprocess, sys

def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"

def sec(s):
    p = [float(x) for x in s.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))

def silences(src, a, b):
    """silence intervals (absolute seconds) between a and b."""
    r = subprocess.run([ffmpeg(), "-hide_banner", "-ss", str(max(0, a)), "-t", str(b - max(0, a)), "-i", src,
                        "-af", "silencedetect=n=-30dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [(max(0, a) + s, max(0, a) + e) for s, e in zip(st, en)]

def snap(src, t):
    sil = silences(src, t - 3, t + 3)
    if not sil: print("WARN no silence within 3 s of %.2f; cutting exactly there" % t); return t
    s, e = min(sil, key=lambda x: abs((x[0] + x[1]) / 2 - t))
    return round((s + e) / 2, 2)

def transcribe(wav):
    """1st: Tidmunz Studio's whisper.cpp (Vulkan GPU), with a HARD time limit. 2nd: faster-whisper (see whisper_model).
    3rd: Tidmunz whisper.cpp on CPU (-ng). user 2026-11-23: on another PC Tidmunz's whisper hung even on 2-3 s audio
    and nothing fell back -> every way now has a time limit and the next way runs after a hang or error."""
    import wave
    with wave.open(wav) as w: dur = w.getnframes() / float(w.getframerate())
    cli, mdl = tidmunz_whisper()
    if cli and mdl:
        r = whisper_cpp(cli, mdl, wav, [], 60 + 2 * dur)
        if r is not None: return r
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        WhisperModel = None
    if WhisperModel:
        import numpy as np   # decode with ffmpeg ourselves (faster-whisper's PyAV path breaks on some av versions)
        m = whisper_model(WhisperModel)
        pcm = subprocess.run([ffmpeg(), "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="th", vad_filter=True, beam_size=1)
        return [{"t": [round(x.start, 2), round(x.end, 2)], "text": x.text.strip()} for x in segs]
    if cli and mdl:   # no faster-whisper: Tidmunz's whisper on the CPU, smallest model it has
        r = whisper_cpp(cli, tidmunz_whisper(small=True)[1], wav, ["-ng"], 120 + 6 * dur)
        if r is not None: return r
    sys.exit("TRANSCRIBE FAIL: Tidmunz whisper hung/failed and faster-whisper is not installed. "
             "Tell the user (Thai). Do NOT test GPUs or install things yourself.")


def whisper_cpp(cli, mdl, wav, extra, limit):
    """run whisper.cpp once with a hard time limit; segments or None (hang / error / bad output)."""
    import tempfile
    tmp = tempfile.mkdtemp()
    w16, base = os.path.join(tmp, "a.wav"), os.path.join(tmp, "a")
    subprocess.run([ffmpeg(), "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "16000", w16], check=True)
    print("WHISPER tidmunz %s %s (max %d s)" % (os.path.basename(mdl), "CPU" if extra else "GPU", limit), flush=True)   # + VAD like Tidmunz
    try:
        # the SAME switches Tidmunz Studio uses (snapgen_whisper_vulkan.py): -np + --vad with its silero model.
        # Without VAD large-v3 loops on silence and looks stuck (user 2026-11-23: "in Tidmunz it works").
        import glob
        vad = (glob.glob(os.path.join(os.path.dirname(mdl), "ggml-silero*.bin")) +
               glob.glob(os.path.join(os.path.dirname(os.path.dirname(cli)), "**", "ggml-silero*.bin"), recursive=True))
        cmd = [cli, "-m", mdl, "-f", w16, "-l", "th", "-t", str(max(1, min(8, (os.cpu_count() or 4) - 1))), "-oj", "-of", base, "-np"]
        if vad: cmd += ["--vad", "-vm", vad[0]]
        pr = subprocess.Popen(cmd + extra, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              cwd=os.path.dirname(cli), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            pr.wait(timeout=limit)
        except subprocess.TimeoutExpired:   # kill it AND its children, then go on
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pr.pid)], capture_output=True); raise
        j = json.load(open(base + ".json", encoding="utf8", errors="replace"))
        out = []
        for x in j.get("transcription", []):
            o = x.get("offsets") or {}
            out.append({"t": [o.get("from", 0) / 1000, o.get("to", 0) / 1000], "text": x.get("text", "").strip()})
        if out: return out
        print("WARN tidmunz whisper gave no text; trying the next way")
    except subprocess.TimeoutExpired:
        print("WARN tidmunz whisper took over %d s (stuck); trying the next way" % limit)
    except Exception as e:
        print("WARN tidmunz whisper failed (%s); trying the next way" % str(e)[:200])
    return None

def tidmunz_whisper(small=False):
    """(whisper-cli.exe, best ggml model) from any Tidmunz Studio install, else (None, None).
    user 2026-11-23: on another PC Tidmunz transcribed fine but Ai-iclone did not find it (fixed path + one model name)."""
    import glob
    la, pf = os.environ.get("LOCALAPPDATA", ""), os.environ.get("ProgramFiles", r"C:\Program Files")
    roots = [os.path.join(la, "Tidmunz Studio"), os.path.join(la, "Programs", "Tidmunz Studio")] + glob.glob(os.path.join(pf, "Tidmunz*"))
    rank = ["large-v3-turbo", "large-v3", "large-v2", "large", "medium", "small", "base"]
    for r in roots:
        if not os.path.isdir(r): continue
        clis = glob.glob(os.path.join(r, "**", "whisper-cli.exe"), recursive=True)
        if not clis: continue
        cli = clis[0]; top = os.path.dirname(os.path.dirname(cli))
        mdls = [m for m in glob.glob(os.path.join(top, "**", "ggml-*.bin"), recursive=True) if "silero" not in m.lower()]
        if not mdls: mdls = [m for m in glob.glob(os.path.join(r, "**", "ggml-*.bin"), recursive=True) if "silero" not in m.lower()]
        def score(m):
            n = os.path.basename(m).lower()
            return next((i for i, k in enumerate(rank) if "ggml-" + k in n), len(rank))
        if mdls:
            return cli, (max if small else min)(mdls, key=score)
    return None, None


def norm(t):   # Whisper writes sara am as nikhahit + sara aa
    return t.replace("ํา", "ำ")


def fix_words(segments, docx, split="(AD.)"):
    """Replace Whisper's rough Thai with the exact words of the script .docx; times stay EXACTLY the same
    (user 2026-11-23). Finds this audio's place in the script, aligns letters, cuts the script at each segment's
    boundary. Keeps Whisper's text in 'heard'. Segments that match nothing keep their text."""
    import difflib, zipfile
    xml = zipfile.ZipFile(docx).read("word/document.xml").decode("utf-8")
    paras = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)]
    full = "\n".join(x for x in paras if x.strip()).replace(split, "\n")
    keep = [i for i, c in enumerate(full) if not c.isspace()]      # script letters without spaces -> index in full
    S = "".join(full[i] for i in keep)
    heard = [re.sub(r"\s+", "", norm(g["text"])) for g in segments]
    W = "".join(heard)
    if not W or not S: return segments
    # 1) the window of the script this audio is in (best ratio, step = 1/4 of the audio length)
    n = len(W); win = int(n * 1.4) + 20; best = (0, 0)
    for st in range(0, max(1, len(S) - n // 2), max(1, n // 4)):
        r = difflib.SequenceMatcher(None, W, S[st:st + win], autojunk=False).ratio()
        if r > best[0]: best = (r, st)
    st = max(0, best[1] - n // 4); Sw = S[st:st + win + n // 2]
    sm = difflib.SequenceMatcher(None, W, Sw, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size]
    if not blocks or sum(b.size for b in blocks) < 0.3 * n: return segments   # not this script
    def to_s(i):   # letter i of W -> letter of Sw (interpolate between matching blocks)
        prev = (0, 0)
        for b in blocks:
            if i < b.a: return prev[1] + round((i - prev[0]) * ((b.b - prev[1]) / max(1, b.a - prev[0])))
            if i <= b.a + b.size: return b.b + (i - b.a)
            prev = (b.a + b.size, b.b + b.size)
        return min(len(Sw), prev[1] + (i - prev[0]))
    cut, pos = [0], 0
    for h in heard: pos += len(h); cut.append(to_s(pos))
    cut[0] = to_s(0); cut[-1] = blocks[-1].b + blocks[-1].size
    # 2) snap each inner cut to the nearest space/line break in the real script (no word split in half)
    def snap_full(k):
        i = keep[min(len(keep) - 1, st + max(0, k))]
        for d in range(0, 25):
            for j in (i - d, i + d):
                if 0 < j < len(full) and full[j - 1].isspace() is False and full[j].isspace(): return j
        return i
    edges = [keep[min(len(keep) - 1, st + cut[0])]] + [snap_full(k) for k in cut[1:-1]] + [keep[min(len(keep) - 1, st + max(0, cut[-1] - 1))] + 1]
    out = []
    for g, a, b in zip(segments, edges, edges[1:]):
        t = re.sub(r"\s+", " ", full[a:b]).strip() if b > a else ""
        out.append(dict(g, text=t or g["text"], heard=g["text"]))
    return out


def whisper_model(WhisperModel):
    """Fast enough on any PC (user 2026-11-23: transcription on another PC took far too long).
    The text only gives TIMING (exact words come from the script .docx), so a fast model is enough:
    NVIDIA GPU -> large-v3-turbo (float16); CPU only -> small (int8, all cores). A model already on the PC is used
    first; a download (turbo ~1.6 GB / small ~0.5 GB) only with --allow-download (ask the user once)."""
    try:
        import ctranslate2
        gpu = ctranslate2.get_cuda_device_count() > 0
    except Exception:
        gpu = False
    dev, ct = ("cuda", "float16") if gpu else ("cpu", "int8")
    order = ["large-v3-turbo", "large-v3", "medium", "small"] if gpu else ["small", "medium", "large-v3-turbo", "large-v3"]
    kw = dict(device=dev, compute_type=ct) if gpu else dict(device=dev, compute_type=ct, cpu_threads=os.cpu_count() or 4)
    for name in order:
        try:
            m = WhisperModel(name, local_files_only=True, **kw)
            print("WHISPER %s on %s" % (name, dev)); return m
        except Exception:
            continue
    if "--allow-download" not in sys.argv:
        sys.exit("No Whisper model on this PC. Ask the user once, then re-run with --allow-download "
                 "(downloads %s, %s)." % (order[0], "~1.6 GB" if gpu else "~0.5 GB"))
    print("WHISPER downloading %s for %s ..." % (order[0], dev))
    return WhisperModel(order[0], **kw)

def main():
    a = sys.argv[1:]
    if len(a) < 4: print(__doc__); sys.exit(1)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paths import expand   # accepts {DRIVE} / {DESKTOP} placeholders
    src, t0, t1, out = expand(a[0]), sec(a[1]), sec(a[2]), expand(a[3])
    t0 = 0 if t0 < 0.5 else snap(src, t0)
    t1 = snap(src, t1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0),
                    "-i", src, "-ar", "48000", out], check=True)
    info = {"src": src, "start": t0, "end": t1, "len": round(t1 - t0, 2), "segments": []}
    print("CUT %s  %.2f-%.2f (%.2f s)" % (out, t0, t1, t1 - t0))
    if "--no-text" not in a:
        info["segments"] = transcribe(out)
        if "--script" in a:   # exact words from the script .docx, same times
            info["segments"] = fix_words(info["segments"], expand(a[a.index("--script") + 1]))
            info["words_from"] = "script"
        for g in info["segments"]: print("  %6.2f-%6.2f %s" % (g["t"][0], g["t"][1], g["text"]))
    json.dump(info, open(out[:-4] + ".json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
