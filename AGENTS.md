# iClone Story Pipeline: instructions for any AI that picks this up

The work: turn Thai folk-tale audio, one part at a time, into an animated 3D video in **iClone 8**
(characters built in Character Creator 5), driven by **Python scripts instead of mouse clicks** so it costs fewer credits.
The user speaks Thai; answer in Thai. They want work done one step at a time as they say, with every new rule they give
**written into this project immediately** (`docs/rules.md`) so they never have to repeat it.

## Read first
1. `docs/rules.md`: every rule the user has given (cameras, lights, motion speed, files, timeline…). **Follow all of them.**
2. `docs/scene_anchors.md`: coordinates of every scene spot already measured (where characters/cameras go).
3. `docs/accupose_presets.md`: list of all 420 AccuPOSE poses + how to use them safely.
4. `docs/iclone-key-SKILL.md`: the full working notes (Claude Code skill copy; same content as rules + history).

## How control works (no mouse)
- In iClone: **Script > Load Python > `scripts/ic8_watch.py`** once per iClone launch (the only manual step).
  It runs every `.py` dropped into `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\run\` within ~1 s,
  renames it `.done` / `.err`, writes `<name>.log`.
- So: write a script → copy into `run\` → wait for the `.py` to disappear → read the log / rendered PNG.
- Popups at iClone start: `scripts/ic8_ui.ps1 click "OK"` then `click "No, thank you."` (UI Automation, no mouse).
- Things RLPy cannot do (need the GUI): create cameras/lights (Create menu), import audio into the Project Sound
  track (File > Import, tick **Sound** in the Project row's ⌄ menu so it shows), apply AccuPOSE poses, Save As.

## Scripts (`scripts/`)
| file | what it does |
|---|---|
| ic8_watch.py | the job runner inside iClone (load once) |
| ic8_survey2.py | lists props/avatars/cameras with positions → `ic8_jobs\survey.txt` |
| ic8_solo.py + solo.json | one character standing, one slowed motion, one camera, stills / video |
| ic8_part2_build.py | multi-character seated scene: load cast, face clip, blink, lip-sync segments, face lights |
| ic8_render2.py + render.json | render video by script (export type 1 = Video). Renders whole project → trim with ffmpeg |
| ic8_stage.py / ic8_key_shot.py | older multi-shot staging scripts (from an earlier story) |
| ic8_ui.ps1 / ic8_open.ps1 | click iClone buttons / fill file dialogs without the mouse |

## Paths
- Story folders: `G:\ไดรฟ์ของฉัน\<story>\` (characters in `<story>\<story>\`, scenes in `<story>\ฉาก\`). **Never write into G:.**
- Audio parts: `C:\Users\Apinan\Downloads\audio_output\N.mp3`; transcript `audio_output\ถอดเสียง\N.txt`.
- Motions: `G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\` (face clips: `Digital Soul 100+`).
- Save project: `E:\FileSave\N.iProject` only. Video: `E:\Video\N.mp4` only, 1920×1080 **60 fps**.
- ffmpeg: `C:\Users\Apinan\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin\ffmpeg.exe`.

## Status (2026-11-07)
- Part 1 (มหาอกหัก): done → `E:\FileSave\1.iProject`, `E:\Video\1.mp4`.
- Part 2: plan + shot list in `docs/part2_plan.md`; build script ready; iClone crashed before saving (see rules: save often).
  Next: reopen scene `ภายในโบสถ์ของวัดอีกวัด`, load watcher, import 2.mp3 (Sound row), extend timeline, run
  `ic8_part2_build.py`, save `E:\FileSave\2.iProject`, apply AccuPOSE sitting poses per character, add face/lips, save, cameras last.
