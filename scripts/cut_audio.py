"""cut_audio.py - cut one part out of a story's master audio by time, at real silences, and transcribe it.

  python scripts/cut_audio.py <master.wav|mp3> <start> <end> <out.wav> [--no-text]
  start/end: seconds or m:ss (e.g. 4:15 5:15). Each edge snaps to the nearest silence within +-3 s.
  Writes out.wav (48 kHz, same channels) and out.json {src, start, end, len, segments:[{t:[a,b], text}]}
  (times in the json are LOCAL to out.wav). Transcript = faster-whisper large-v3 (same model as Tidmunz), Thai.
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

def main():
    a = sys.argv[1:]
    if len(a) < 4: print(__doc__); sys.exit(1)
    src, t0, t1, out = a[0], sec(a[1]), sec(a[2]), a[3]
    t0 = 0 if t0 < 0.5 else snap(src, t0)
    t1 = snap(src, t1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0),
                    "-i", src, "-ar", "48000", out], check=True)
    info = {"src": src, "start": t0, "end": t1, "len": round(t1 - t0, 2), "segments": []}
    print("CUT %s  %.2f-%.2f (%.2f s)" % (out, t0, t1, t1 - t0))
    if "--no-text" not in a:
        from faster_whisper import WhisperModel
        try: m = WhisperModel("large-v3", device="cuda", compute_type="float16")
        except Exception: m = WhisperModel("large-v3", device="cpu", compute_type="int8")
        import numpy as np   # decode with ffmpeg ourselves (faster-whisper's PyAV path breaks on some av versions)
        pcm = subprocess.run([ffmpeg(), "-loglevel", "error", "-i", out, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="th", vad_filter=True)
        for s in segs:
            info["segments"].append({"t": [round(s.start, 2), round(s.end, 2)], "text": s.text.strip()})
            print("  %6.2f-%6.2f %s" % (s.start, s.end, s.text.strip()))
    json.dump(info, open(out[:-4] + ".json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
