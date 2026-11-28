# Workflow for one audio part (any AI: follow in order, report to the user after each step)

ดู [คู่มือคีย์ลัด iClone 8](iclone8_keyboard_shortcuts.md) สำหรับรายการคีย์ลัดครบตามคู่มือทางการ บริบทโฟกัส และทางเลือกเมนูคลิก

## CURRENT OVERRIDE — Event-clip render-first workflow (2026-11-11)

For action-heavy story parts such as ดวงเมียน้อย Part 3, this section OVERRIDES the legacy one-audio-part = one-long-project/timeline procedure below.

Use docs/event_clip_workflow.md as canonical.

- Build one complete dramatic event per numbered clip/project.
- Camera changes and reactions inside the same event DO NOT create new clip numbers.
- Speaker changes inside the same conversation DO NOT create new clip numbers.
- New number begins when the story changes to a new main action/event.
- Save/check/render that event before starting the next event.
- Do not hard-code event boundaries from audio timestamps. Audio is sync, not structure.
- Part 3 canonical plan: docs/part3_event_clip_plan.md and data/part3_event_clips.json.
- Old fixed 3.1/3.2/3.3 WAV split is reference only.
- After each event passes, assemble event videos into one final Part 3 master.



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
- Save As `{SAVE}\N.iProject` and CHECK the file time on disk.

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
- Manually click iClone File > Save Project (never use a shortcut or script), then check file time.

## 6. Render — ONLY when the user says. User currently renders themselves.
- If asked: `scripts/ic8_render2.py` (whole project, 60 fps) → ffmpeg mux N.mp3 → `{VIDEO}\N.mp4`. Check the raw file exists
  before muxing (part 3 script render returned without a file once).

- Step 3b (after chained clips exist): run scripts/ic8_blend_clips.py so every chained face/body clip crossfades (no head snap).

- Part 5/6 recipe (narration only): Save As previous -> N.iProject (confirm overwrite dialog: Yes), delete old Sound clip, set playhead 0 by script, Ctrl+I N.mp3, run scripts/ic8_partN_setup.py (SetProjectLength+SetEndTime), run scripts/ic8_partN_cams.py (stills -> contact sheet), pick Switch in the camera dropdown (menu is slow: click, wait 3 s, zoom, click Switch), manually click File > Save Project; check file time.

- Part 7 added standing characters (นายอิ่ม, สีกาอ๋อย): scripts/ic8_part7_cast.py (STAND body, ONLY per job) + scripts/ic8_part7_cast_extras.py (nods + look-at monk head). Part 7 = 23 s audio, 28 s timeline.
- **Dedicated multi-camera dialogue rule (2026-11-11):** สำหรับ dialogue/event coverage เช่น 3.1 ให้สร้าง custom camera object แยกตามหน้าที่ เช่น Mom CU, Dad CU, two-shot/depth, kids reaction, OTS/profile แล้วใช้ Project > Switcher / AddSwitchCameraKey ตัดระหว่างกล้อง. ห้ามใช้กล้องตัวเดียว teleport/hard-step ไปทุกมุมเป็นวิธีหลัก เพราะแก้ framing/DOF/continuity ยากและทำให้ coverage ดูซ้ำ/ง่อย. กล้องแต่ละตัวควรมีชื่อสื่อหน้าที่, transform/focal/DOF ของตัวเอง; ใช้กล้องเดิมซ้ำได้เมื่อกลับมาที่มุมเดิม. เปลี่ยนกล้องไม่ใช่ event boundary. ก่อน Save ต้องตรวจ camera count, switch-key sequence และ still framing ทุก beat; moving playback QA ยังต้องทำแยกต่างหาก.
- **Gaze-first camera and moving occlusion rule (2026-11-11):** ใน dialogue scene ให้ตั้ง eyeline ก่อนออกแบบกล้อง: ใช้ iClone Look At ผูกตัวละครกับ Head bone ของคู่สนทนาจริง เพื่อให้สายตายังถูกต้องเมื่อเปลี่ยนหรือแพนกล้อง. อย่าจัดกล้องโดยสมมติว่าตัวละครมองถูกอยู่แล้ว. หากใช้ OTS หรือ foreground shoulder/shirt ต้องตรวจทั้งช่วงโมชั่นหลายเฟรม อย่างน้อย start/mid/end และเพิ่มจุดเมื่อ motion มาก; ห้ามอนุมัติจาก still เฟรมเดียว. ถ้ามีโอกาส foreground/แขน/เสื้อบังหน้า subject ให้ย้ายกล้อง ลด foreground ให้เหลือ sliver ที่ปลอดภัย หรือเปลี่ยนเป็น clean 3/4/profile/dirty single. Face visibility สำคัญกว่า forcing OTS. หลังตั้ง Look At ต้อง re-QA ทุก dedicated camera เพราะ head orientation เปลี่ยน framing ได้.
- **Part 3 original-audio continuity + every-frame review (2026-11-11):** คลิปย่อย 3.1/3.2/3.3/3.4 เป็น visual event เท่านั้น; master ต้องยาว 67.40s = 2,022 frames ที่ 30fps และใช้ WAV ท่อน3.wav ฉบับเต็ม 3,235,200 sample frames @48kHz โดยไม่ตัด/ซ้ำ/ยืด/บีบ/กระโดดเสียง. ตอนประกอบตัดเสียงของ MP4 ย่อยทิ้งทั้งหมด แล้วใส่ original WAV เป็น audio track เดียว. ตรวจ EDL ให้ครบ [0,2022) ไม่มี hole/overlap; 3.1.mp4 ปัจจุบันยาว 72.433s จึงเลือก VIDEO เพียง 1290 เฟรมแรกและห้ามทับต้นฉบับ. 3.2 ต้องไม่ข้ามช่วง 43–52.94; ต้องมีภาพตามบทตลอดช่วง. QA ช็อตเสี่ยงที่ 30fps ทุกเฟรม (contact sheet 30 เฟรม/แผ่น), เช็กก่อน/หลังทุกคัต; re-QA ทุกเฟรมของช็อตหลังแก้. ห้ามเรนเดอร์คลิปใหม่ก่อนผู้ใช้ตรวจอนุมัติ. เอกสาร docs/part3_audio_continuity.md; EDL data/part3_frame_edl.json.

## Project Sound / Preview — 2026-11-27
- Cast → Sound → Pose → Lip → Cams. Import Project Sound only once per loaded project; inspect the clip name and full part range at frame 0. Repair Pose/Motion/face/camera or add cast without importing it again. Re-import only when a different project/audio is loaded or sound is confirmed missing/wrong. Lip Sync uses the original full part audio per speaker and retains the Project Sound track.
- Save/reopen only via the visible iClone File menu. No automatic script save, and no render before approval.
- For the locally installed Chrome Preview Bridge and Goal Tracker, read docs/CHROME_PREVIEW_GUIDE.md; check actual installation and exact authorized conversation before use.

## Current candidate workflow (1.7.8)
Read docs/CINEMATIC_SLEEP.md and current Preview cards. Scene-aware replan, prop review, editorial/final review use identical standards in BOTH modes. Old 80/100-only and five-second-cut rules are superseded. Sleep changes approval and handoff only. Use Ai-iclone repair <step> and do, not direct ic8_part calls. Motion Analyzer requires verified transfer and explicit bone map; no invented evidence. Do not claim live pass before verification.
