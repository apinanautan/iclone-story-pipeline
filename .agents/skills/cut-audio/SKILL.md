---
name: cut-audio
description: Cut a part's audio out of a story's master WAV/MP3 by time range at real silences and transcribe it (Thai, large-v3). Use whenever a part needs its own wav or transcript.
---
# Cut + transcribe audio (one command, ~20 s)

```
python scripts/cut_audio.py "<master wav/mp3>" <start> <end> "C:/Users/<user>/Desktop/<story>/เสียงที่ตัดแล้ว/ท่อน<N>.wav"
```
- start/end in seconds or m:ss. Edges snap to the nearest silence within 3 s (printed as `CUT ... a-b`).
- Output: `ท่อนN.wav` (48 kHz) + `ท่อนN.json` = {src, start, end, len, segments:[{t:[a,b], text}]}, times LOCAL to the wav.
- Uses the large-v3 model already on the PC (Tidmunz Studio's whisper.cpp; Tidmunz need not be open). Never downloads a model. If it says no model, ask the user.
- Allowed without asking (user 2026-11-17). Do not write other ffmpeg/whisper scripts; do not open Tidmunz for this.
- Master audio paths: `docs/CURRENT_STORY.md` or the story folder on G: (read only).
- Whisper text is rough: use the script .docx for exact wording, the json for timing.
