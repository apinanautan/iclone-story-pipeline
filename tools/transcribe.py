# Transcribe audio parts (Thai) with faster-whisper on CPU -> audio_output\ถอดเสียง\N.txt and data\parts\N.segments.json
# Usage: python tools/transcribe.py 3 4 5 ...
import json, os, sys
from faster_whisper import WhisperModel

AUD = r"C:\Users\Apinan\Downloads\audio_output"
FF = r"C:\Users\Apinan\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin\ffmpeg.exe"
OUT_TXT = os.path.join(AUD, "ถอดเสียง")
OUT_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "parts")
os.makedirs(OUT_TXT, exist_ok=True); os.makedirs(OUT_JSON, exist_ok=True)
model = WhisperModel("small", device="cuda", compute_type="float16")
for n in sys.argv[1:]:
    # decode with ffmpeg (the installed `av` is too new for faster-whisper's own decoder)
    import subprocess, numpy as np
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(AUD, f"{n}.mp3"), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    segs, _ = model.transcribe(audio, language="th", vad_filter=True)
    segs = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
    txt = os.path.join(OUT_TXT, f"{n}.txt")
    if not os.path.exists(txt):  # never overwrite a transcript the user made
        open(txt, "w", encoding="utf-8").write(" ".join(s["text"] for s in segs))
    json.dump(segs, open(os.path.join(OUT_JSON, f"{n}.segments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, len(segs), "segments")
