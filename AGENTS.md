# iClone Story Pipeline: instructions for any AI that picks this up

The work: turn Thai folk-tale audio, one part at a time, into an animated 3D video in **iClone 8**
(characters built in Character Creator 5), driven by **Python scripts instead of mouse clicks** so it costs fewer credits.
The user speaks Thai; answer in Thai. They want work done one step at a time as they say, with every new rule they give
**written into this project immediately** (`docs/rules.md`) so they never have to repeat it.

## Mandatory lip-sync audio workflow (user update 2026-11-07)
For any speaking character, import the **full N.mp3** directly to that avatar through iClone's Voice/AccuLips process, then **split/trim/remove unused speech sections within the iClone Timeline** to leave only that character's dialogue at the original timestamps. Repeat with the original full audio for every speaker. **Do not pre-cut short WAVs externally to import as lip-sync source.** Leave full original audio on Project Sound track; prevent doubled playback. Verify actual Viseme clips, mouth animation and speaker timing, not just Look front.iTalk or successful audio import. Preserve AccuPOSE. See docs/iclone-key-SKILL.md and docs/rules.md. Last survey showed 0 Viseme clips for all 6 Part 2 avatars.

## Always review a contact sheet
After poses and after every camera pass: render stills and combine them with `scripts/contact_sheet.py` into one image, look at it, fix bad shots, send it to the user. See docs/rules.md (Review step).

## Start here
**docs/WORKFLOW.md** = the step list. **data/** = ready-made data for all 11 parts (times, transcripts, story text, assets).

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
- Part 2: done in `E:\FileSave\2.iProject` (poses, face, blink, lip sync trimmed per speaker, 9 moving cameras
  incl. a villager group shot). Rendered to `E:\Video\2_raw.mp4` → audio muxed from 2.mp3 → `E:\Video\2.mp4`.
- Part 3: shot plan approved → `docs/part3_plan.md`. Times are estimates (no 3.txt); check the monk's line and the statues.

## Lessons from part 2 (reuse for every part)
- Lip sync: `scripts/ic8_lip_trim.py` after GUI Create Script > Audio File with the full N.mp3 (see rules).
  RLPy: index `RVisemeKeyVector` with `kv[i]` (iterating gives raw Swig objects); RTime → `.ToFloat()` (no GetValue).
- Mouth QA: `scripts/ic8_mouth_check.py` (close-up stills, 2 speaking + 1 silent per speaker).
- Cameras: `scripts/ic8_part2_cams.py` = one camera, hard cuts (hold key at end−1/60 s), DOF keys, slow zoom/orbit per
  shot, Switcher key at 0, `MODE="stills"` renders the middle of every shot for review. Template for later parts.
- Head positions: read the `...Head` skin bone (`GetSkeletonComponent().GetSkinBones()`, `WorldTransform().T()`).
- Render time: 86.5 s at 60 fps with DOF ≈ 40 min on the RTX 4060 Ti; the file appears only at the end. Don't touch iClone meanwhile.
- `RenderImage` leaves the Render panel open; close it before clicking the toolbar.
- Git commit needs `-c user.name=Apinan -c user.email=apinan.autan@gmail.com` (no global identity).
