# Workflow for one audio part (any AI: follow in order, report to the user after each step)

Data you get for free (no need to re-derive):
- `data/parts_index.json` — every part 1–11: audio path, seconds, timeline length (+5 s), status, scene suggestion,
  whisper segments with times. Transcripts: `audio_output\ถอดเสียง\N.txt` (whisper, rough Thai — use the story text for wording).
- `data/story_script.txt` — the full story text. Quotes `ชื่อ : “...”` are character lines → need lip sync.
- `data/assets.json` — every scene (.iProject) and character (.iAvatar) of the story.
- `docs/scene_anchors.md` — measured coordinates (temple stairs, Naga node_0/node_1, Wessuwan node_3 …).
- `docs/rules.md` — every rule from the user. Wins over anything here.

## 0. Before starting
- Parsec must be DISCONNECTED during iClone work (audio import froze iClone 3× with it).
- iClone open, watcher loaded (Script > Load Python > ic8_watch.py; "not compatible" popup → OK).

## 1. Plan (user approves)
- Read the part's segments + story text. Mark narration vs. character lines (speaker, start, end).
- Shot table: time | narration | picture | lens. Cut on pauses (silencedetect). 4–8 shots.
  Chest-up only, at least one group shot, statue/place shots show the whole thing big.
- Write `docs/partN_plan.md`. If the scene is the same as the previous part: Save As the previous project as N.iProject
  and reuse cast/poses (part 4 did this from part 3).

## 2. Scene + audio (GUI)
- Open scene by script: `RLPy.RFileIO.LoadFile(<scene>)` (or Save As from previous part).
- Delete the old Sound clip (click it on the Sound row → Delete). Clear selection by script, then Ctrl+I → full path of N.mp3.
  Confirm "N (100.00%)" on the Sound row.
- `SetProjectLength` + `SetEndTime` = seconds + 5. Zoom the timeline to show the whole length.
- Save As `E:\FileSave\N.iProject` and CHECK the file time on disk.

## 3. Characters (script, one avatar per job)
- `scripts/ic8_part3_build.py` pattern: CAST dict, ONLY='<key>' per job (loading all at once froze iClone).
  Face Look front slowed, auto blink, Stand00 body for standing people.
- Poses in GUI: AccuPOSE toolbar button (440,86) → Kneel Seiza (391,425) after scrolling → Apply (482,580). Select each
  avatar first with `scripts/ic8_select.ps1`. Panel keeps its scroll position.
- Head motion: `scripts/ic8_head_nod.py` (PREFIX, L). Look-at: standing person facing someone →
  `GetLookAtComponent().AddLookAtKey(T(0), T(1), <target Head bone>, 1.0, 0.0)`.
- Contact sheet of placement stills → user.

## 4. Lip sync (GUI + script) — only for character lines
- Select speaker → Animation > Create Script > Audio File → type `4.mp3` style name (dialog opens in audio_output) → Open.
- Trim: run `scripts/ic8_lip_trim.py` with WIN = {'<avatar>': (start, end)}. Check mouth stills (ic8_mouth_check.py pattern).

## 5. Cameras (last)
- Copy `scripts/ic8_part3_cams.py` / `ic8_part4_cams.py`, edit SHOTS only. Two cameras (create Camera_0 via Create > Camera >
  Linear Camera if missing). MODE "stills" → `python scripts/contact_sheet.py "<ic8_jobs>\c4_*.png" sheet.jpg` → look, fix, send.
- Save (File > Save Project), check file time.

## 6. Render — ONLY when the user says. User currently renders themselves.
- If asked: `scripts/ic8_render2.py` (whole project, 60 fps) → ffmpeg mux N.mp3 → `E:\Video\N.mp4`. Check the raw file exists
  before muxing (part 3 script render returned without a file once).
