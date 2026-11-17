---
name: lip-sync
description: Make speaking characters' mouths move in iClone (AccuLips from the part wav, keep only each speaker's line windows). Use after the user approved the stills.
---
# Lip-sync

```
python scripts/ic8_part.py parts/<spec>.json lip
```
- Per speaker: GUI Animation > Create Script > Audio File with the part wav, then visemes outside that speaker's `lines` windows are removed. Non-speakers' mouths are cleared.
- One speaker by hand: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ic8_gui.ps1 lip <avatar> <wav> <start> <end>`.
- Verify: Viseme clip count > 0 for each speaker, and the mouth moves in a mid-line still.
- RAudio.LoadAudioToObject makes NO visemes and can crash iClone: never use it.
