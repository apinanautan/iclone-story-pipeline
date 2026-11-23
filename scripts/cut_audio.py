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
    """Use the large-v3 model ALREADY on this PC - never download a second copy.
    1st: Tidmunz Studio's whisper.cpp (Vulkan) + ggml-large-v3.bin (Tidmunz need not be open).
    2nd: faster-whisper large-v3 only if it is already in the HuggingFace cache (local_files_only)."""
    W = os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "tools", "whisper_vulkan")
    cli, mdl = os.path.join(W, "bin", "whisper-cli.exe"), os.path.join(W, "ggml-large-v3.bin")
    if os.path.exists(cli) and os.path.exists(mdl):
        import tempfile
        tmp = tempfile.mkdtemp()
        w16 = os.path.join(tmp, "a.wav")
        subprocess.run([ffmpeg(), "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "16000", w16], check=True)
        subprocess.run([cli, "-m", mdl, "-l", "th", "-oj", "-of", os.path.join(tmp, "a"), "-f", w16],
                       capture_output=True, check=True)
        j = json.load(open(os.path.join(tmp, "a.json"), encoding="utf8", errors="replace"))
        return [{"t": [x["offsets"]["from"] / 1000, x["offsets"]["to"] / 1000], "text": x["text"].strip()} for x in j["transcription"]]
    from faster_whisper import WhisperModel
    import numpy as np   # decode with ffmpeg ourselves (faster-whisper's PyAV path breaks on some av versions)
    m = whisper_model(WhisperModel)
    pcm = subprocess.run([ffmpeg(), "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="th", vad_filter=True, beam_size=1)
    return [{"t": [round(x.start, 2), round(x.end, 2)], "text": x.text.strip()} for x in segs]


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
        for g in info["segments"]: print("  %6.2f-%6.2f %s" % (g["t"][0], g["t"][1], g["text"]))
    json.dump(info, open(out[:-4] + ".json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
