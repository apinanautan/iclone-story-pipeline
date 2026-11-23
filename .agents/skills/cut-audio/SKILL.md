---
name: cut-audio
description: Cut a part's audio out of a story's master WAV/MP3 by time range at real silences and transcribe it (Thai, large-v3). Use whenever a part needs its own wav or transcript.
---
# Cut + transcribe audio (one command, ~20 s)

```
python scripts/cut_audio.py "<master wav/mp3>" <start> <end> "{DESKTOP}/<story>/เสียงที่ตัดแล้ว/ท่อน<N>.wav" --script "<script_docx>"
```
- start/end in seconds or m:ss. Edges snap to the nearest silence within 3 s (printed as `CUT ... a-b`).
- Output: `ท่อนN.wav` (48 kHz) + `ท่อนN.json` = {src, start, end, len, segments:[{t:[a,b], text}]}, times LOCAL to the wav.
- Model (user 2026-11-23, faster on other PCs): Tidmunz Studio's whisper.cpp large-v3 if on the PC; else faster-whisper, NVIDIA GPU -> large-v3-turbo, CPU only -> small (the text is only for timing). It prints `WHISPER <model> on <device>`. No model on the PC -> it says so: ask the user ONCE, then re-run with `--allow-download`.
- Never test GPUs, benchmark, install other Whisper versions or try Vulkan yourself: just run this command. Run it for all parts in one go, not part by part with checks in between.
- Allowed without asking (user 2026-11-17). Do not write other ffmpeg/whisper scripts; do not open Tidmunz for this.
- Master audio paths: `docs/CURRENT_STORY.md` or the story folder in {DRIVE} (read only).
- `--script <docx>` (always use it, user 2026-11-23): each segment's text is replaced by the exact words of the script .docx; the times stay exactly the same; Whisper's words are kept in `heard`. Check the json once by eye; never move a time.
- Tidmunz's whisper.cpp is found anywhere under its install (any ggml model, best first): prints `WHISPER tidmunz <model>`.
