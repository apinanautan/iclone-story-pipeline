# iClone Story Pipeline: instructions for any AI that picks this up

**START HERE (2026-11-22): run `Ai-iclone.exe` (no arguments) in this folder and follow what it prints.** It is the program for this work: it shows the story/part status (same as the Ai-iclone window), the one next command (`Ai-iclone do`), and the rules card of that step. Do not read the rest of this file or docs/ unless it says so.
Older notes below are history/reference.

## Skills first (2026-11-17)
Step-by-step skills live in `.agents/skills/*/SKILL.md` (Codex loads them; any other AI: read them). For a story part
start with **story-part** (master flow): cut-audio -> plan-part -> build-part -> review-stills (STOP for user) -> lip-sync -> save-render.
Helpers: **paths** (never hardcode G:/E: - use {MOTION} {DRIVE} {SAVE} {VIDEO} {DESKTOP}), acting (slow motion, face expressions), pose-bones (bone posing by Python), iclone-control (driving iClone without mouse), motion-ai (only after the user says yes).

The work: turn Thai folk-tale audio, one part at a time, into an animated 3D video in **iClone 8**
(characters built in Character Creator 5), driven by **Python scripts instead of mouse clicks** so it costs fewer credits.
The user speaks Thai; answer in Thai. They want work done one step at a time as they say, with every new rule they give
**written into this project immediately** (`docs/rules.md`) so they never have to repeat it.

## Codex / GPT: do NOT use GPT-side tools (user 2026-11-15)
The ChatGPT tunnel ("MyComp Bot for Windows"; one per PC, each PC has its own name, e.g. Dino) (OpenAI Tunnel over Tailscale) is the user's tool for ChatGPT (their Minecraft bot / PC control for GPT), NOT for Codex. Codex must not call that tunnel (on any PC) or other ChatGPT-side tools (connectors, Computer Use, Agent Desktop, subagents) to drive iClone. Use only the local watcher (`ic8_jobs/run/*.py`) + `scripts/` + PowerShell. First message of every part: read docs/rules.md and docs/DELIVERY_CHECKLIST.md in full and make the checklist the task list.

**STAGE 1 BEFORE PARTS (hard gate, 2026-11-22):** every new story starts with story setup (Preview tab ① เตรียมเรื่อง, 8 rows). No per-part work (plan, cast, pose, cams, render) until all 8 are green; `ic8_part.py` refuses every step otherwise. The teacher's range comes from the user only. Commit PROGRAM changes to git after each finished piece of work; story sheets/parts/progress are work data and stay out of git.

## Mandatory lip-sync audio workflow (user update 2026-11-07)
For any speaking character, import the **full N.mp3** directly to that avatar through iClone's Voice/AccuLips process, then **split/trim/remove unused speech sections within the iClone Timeline** to leave only that character's dialogue at the original timestamps. Repeat with the original full audio for every speaker. **Do not pre-cut short WAVs externally to import as lip-sync source.** Leave full original audio on Project Sound track; prevent doubled playback. Verify actual Viseme clips, mouth animation and speaker timing, not just Look front.iTalk or successful audio import. Preserve AccuPOSE. See docs/iclone-key-SKILL.md and docs/rules.md. Last survey showed 0 Viseme clips for all 6 Part 2 avatars.

## Cinematic action beat & motion QA (2026-11-10)
Read docs/motion_direction_10pass.md before directing motion. Use 10 passes for human acting and cinematic editorial coverage. Do not use a single forced long wide shot for stand-turn-walk; split dramatic beats and match movement across edits. Do not confuse software checks with artistic QA. No automatic preview render.

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
| **ic8_gui.ps1** | **GUI chores in one command each (use instead of screenshot+click):** `save`, `saveas <path>`, `open <path> [-Discard]`, `reopen`, `switch`, `tozero`, `sound <wav> [-Replace]`, `lip <avatar> <wav> <s> <e>`, `render <out.mp4> <end> <wav> [-Shots ..] [-Publish dir]`, `press <button>`, `shot`, `job <py>`. Saves only via GUI, backs up first, verifies disk + reload. |
| **ic8_story.py** | **START HERE for any part:** `python scripts/ic8_story.py <story> brief <N>` = story/part facts as points (master time range, content, plan, scene + character files, previous project, docx script block, transcript). `init` = new story from `stories/_template.json`; `close` = story finished → its story/part files to Recycle Bin (only the 2 templates stay). `list` = all parts + which files exist. `new <N>` = write the part spec. Facts live in `stories/<story>.json` (update it, never re-hunt). |
| **ic8_part.py** | **Build a part from ONE spec** `parts/<story>_<N>.json` (example: `parts/_example.json`): steps `audio`, `check`, `open`, `cast`, `pose`, `sound`, `lip`, `cams`, `ready` (`all` = check..ready; `<step> --from` re-runs from there), `render --approved` only after the user says ผ่าน. `check` refuses specs that break the rules. The AI fills numbers; the script does the order. |
| **ic8_scene_scan.py** | **Measure a scene ONCE** (read-only job): objects + bounding boxes -> `ic8_jobs/scene_scan.json`; then `ic8_story.py <story> scan <scene>` stores them + a room guess. Then name **spots** (where people stand/sit: pos, yaw, motions) and **cams** (pos, target, focal) under that scene in the story file, show the user a still of each, set `approved: true`. Part specs then say `"spot": "<name>"` / `"cam": "<name>"` instead of numbers; Indoor scenes use `room` (walls), outdoor scenes (`"type": "outdoor"`) use `area` (where the action is); `check` refuses cameras/people outside it, cameras INSIDE a scanned object (house, tree, bed) and two people on one spot, warns when a scanned object blocks the camera→target line, and warns on unapproved names and on cams reused from the previous part. User comments about a scene go in its `notes_list` (printed by brief + check). |
| ic8_pose_place.py + pose_place.json | generic: body clips back to back (slowed), root pos/yaw/tilt, Look front, Look At, face keys, visibility |
| ic8_cams.py + cams.json | generic: deletes all cameras, Cam_A/Cam_B alternate, 2 keys per shot, switcher, start/mid/end stills, play range 0..end |
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
- **Mandatory iClone scene delivery gate (2026-11-11):** ก่อนใช้คำว่า "เสร็จ/พร้อมตรวจ" ต้องยืนยันในโปรแกรมจริง 1) Project Sound Track มีเสียงหลัก full part (นำเข้า Sound Track ผ่าน GUI), 2) Avatar ผู้พูดทุกคนมี Viseme Clip/Keys เฉพาะช่วงพูดจริง โดยนำไฟล์เต็มเข้า Create Script > Audio File แล้วแก้ที่ Timeline/iClone ไม่ใช่คีย์ปากเดาสุ่ม, 3) สร้างและยืนยัน expression keys และรีแอ็กชันตามบท, 4) Timeline แสดงช่วง 0–end และ playhead เล่นเดินได้, 5) ช็อตทั้งหมดโดยเฉพาะตอนจบไม่ติดกำแพง/หลุดเฟรม, 6) ตรวจโมชั่น/กล้องและเสียงจริงก่อนอนุมัติเรนเดอร์. ถ้ายังไม่ผ่านข้อใด ให้รายงาน "ยังไม่เสร็จ" กับหลักฐานและจุดค้าง. ต้องไม่ข้ามเสียง/ปาก/สีหน้าซ้ำอีก, ทำบนจอ 2 โดยไม่แย่งโฟกัสจอหลัก.
- **iClone dual-monitor startup popup preflight (2026-11-11):** เมื่อเปิดหรือรีสตาร์ต iClone ต้องตรวจหน้าต่างของ iClone ทุกหน้าต่างทั้งจอ 1 และจอ 2 ก่อนทำงาน ไม่ใช่ดูแค่ main window. เคยพบ connection error ชื่อ iClone 8 (ข้อความ Failed to establish a connection due to unknown error, ปุ่ม OK) และหน้าสมัคร SIGN UP NOW AND GET ชื่อ iClone (กด No, thank you.). หากกดปุ่มไม่ได้ หลังยืนยันชนิดหน้าต่างแล้วจึงส่ง WM_CLOSE เฉพาะ dialog HWND ห้ามปิดโปรแกรมหลัก/Save dialog; ตรวจว่าปิดจริงและหน้าต่างหลักยังอยู่. หลีกเลี่ยงการแย่งโฟกัสจอ 1; เช็ก watcher และชื่อโปรเจกต์จริงหลังเคลียร์ popup. ดู docs/iclone_startup_popup_recovery.md.
- **Action-based chapter splitting (2026-11-11):** **ผลลัพธ์สุดท้ายท่อน 3 คือวิดีโอเรื่องต่อเนื่องหนึ่งไฟล์** ไม่ตัดเป็น 3.1/3.2/3.3 โดยอัตโนมัติตามเวลา/เสียง และไม่แยกทุกช็อต. ให้แบ่งฉากย่อย 3.1, 3.2, ... เฉพาะเมื่อเกิด **action/movement beat** ที่ต้องเปลี่ยนท่าจริง เช่น ยืน→หัน→เดินออก→เข้าประตู, พาลูกลุกแล้วเดิน, หรือการเคลื่อนไหวที่ทำเทคเดียวดูไม่เนียน. ถ้ายืนพูด/ฟัง/แสดงสีหน้าต่อเนื่อง ให้เก็บเป็นช่วงเดียว ไม่สร้างไฟล์ย่อยหรือหั่นเสียงเพียงเพราะเปลี่ยนผู้พูด/กล้อง; การเปลี่ยนกล้องเป็น coverage ภายในช่วงเดียวได้. แยก working-takes เฉพาะจุดที่จำเป็นเพื่อกำกับโมชั่นและตัดต่อ match-on-action (foot phase, root, eyeline, screen direction) จากนั้นประกอบเป็นวิดีโอท่อน 3 ไฟล์เดียวพร้อมเสียงหลักไม่ขาด ไม่เหลือรอยต่อแข็ง. แผน 3.1=0–12.32, 3.2=12.32–40.48, 3.3=40.48–67.4 ที่ทำก่อนหน้าเป็น **การแบ่งผิดตามคำสั่งล่าสุด**: ห้ามใช้เป็นกรอบบังคับ; WAV เหล่านั้นเป็นเพียงไฟล์อ้างอิงที่สร้างไว้ ไม่ใช่ชิ้นงานที่ต้องส่ง. ใช้ชื่อไฟล์ย่อยโดยลำดับ action ที่เกิดจริงเท่านั้น; ก่อนผู้ใช้ได้ไฟล์ ต้องตรวจภาพเคลื่อนไหว, บทพูด/ปาก, สีหน้า, เสียง และทุกคัต. ยึดเวลาไม่เกิน 15 นาทีต่อรอบเพื่อลง checkpoint จริง ไม่อ้างว่า 15 นาทีพอสำหรับงานคุณภาพทั้งหมด. **อัปเดต 2026-11-11 (user):** เปลี่ยนไปทำเป็น event-clip: จบหนึ่งเหตุการณ์→ตรวจ→render ไฟล์คลิป (3.1_preview480.mp4)→save 3.1.iProject ก่อนคลิปถัดไป (3.2…) ห้ามสะสม Timeline ยาวแล้วเรนเดอร์ทีเดียว; ประกอบท่อน 3 เมื่อคลิปผ่านครบ (ดู docs/rules.md 'Event-clip workflow 2026-11-11').
- **iCloneStoryBridge startup compatibility warning (2026-11-11):** พบหน้าต่างบนจอ 2 ข้อความ iCloneStoryBridge Python plugin is not compatible with this version of iClone, ถาม Do you still want to proceed? ให้ตรวจว่าเป็นหน้าต่างนี้จริง, กักคิว Python .py ที่ค้างก่อน, คลิก OK แบบ accessibility โดยไม่แย่งโฟกัส แล้วตรวจ mcp_autostart_status.txt ใหม่ว่า STARTED และรัน read-only watcher job ให้ผ่าน. ตรวจ popup ทั้งสองจอทุกครั้ง ไม่คลิก dialog ไม่ทราบชนิด. ดู docs/iclone_startup_popup_recovery.md.
- **Event-clip render-first workflow (2026-11-11, FINAL CLARIFICATION):** หนึ่งเลขคลิป = หนึ่งเหตุการณ์ที่จบสมบูรณ์ และต้องทำ/ตรวจ/Save/Render คลิปนั้นก่อนเริ่มเลขถัดไป. ห้ามทำ Part 3 เป็น Timeline ยาวทั้งท่อนแล้วค่อย render ทีเดียว; ห้ามแบ่งเลขใหม่เพราะเปลี่ยนกล้อง, reaction ภายในเหตุการณ์เดิม, เปลี่ยนผู้พูด หรือ arbitrary audio time. กล้อง/reaction เป็น coverage ภายในเลขเดิม. ปัจจุบัน 3.1=standing conversation จนเหตุการณ์พูดจบ; 3.2=father+mistress decision/turn/walk-away; 3.3=mother+children aftermath/comfort; 3.4=walk-home เฉพาะถ้าเป็น movement event ใหม่จริง. ต่อเลข: event-only build -> camera coverage -> moving QA -> save N.iProject -> ถามก่อน render ตาม policy -> render preview -> ดูไฟล์จริง -> ผ่านแล้วค่อยเริ่มเลขถัดไป. เวลาเสียงใช้ sync เท่านั้น; fixed splits 0–12.32/12.32–40.48/40.48–67.4 และ WAV ที่ตัดตามนั้นเป็น reference only. Canonical: docs/event_clip_workflow.md, docs/part3_event_clip_plan.md, data/part3_event_clips.json.

## Current status pointer

Read docs/CURRENT_STORY.md (ONE neutral file, overwritten per story/part; no per-story files). Generic scripts to edit per part: scripts/ic8_cast.py, ic8_pose_face.py, ic8_cameras.py, ic8_save.py.
Current workflow is event-clip render-first. Do not infer completion from filenames; 3.1 may exist while still failing event-isolation/QA gates.
- **Dedicated multi-camera dialogue rule (2026-11-11):** สำหรับ dialogue/event coverage เช่น 3.1 ให้สร้าง custom camera object แยกตามหน้าที่ เช่น Mom CU, Dad CU, two-shot/depth, kids reaction, OTS/profile แล้วใช้ Project > Switcher / AddSwitchCameraKey ตัดระหว่างกล้อง. ห้ามใช้กล้องตัวเดียว teleport/hard-step ไปทุกมุมเป็นวิธีหลัก เพราะแก้ framing/DOF/continuity ยากและทำให้ coverage ดูซ้ำ/ง่อย. กล้องแต่ละตัวควรมีชื่อสื่อหน้าที่, transform/focal/DOF ของตัวเอง; ใช้กล้องเดิมซ้ำได้เมื่อกลับมาที่มุมเดิม. เปลี่ยนกล้องไม่ใช่ event boundary. ก่อน Save ต้องตรวจ camera count, switch-key sequence และ still framing ทุก beat; moving playback QA ยังต้องทำแยกต่างหาก.
- **Gaze-first camera and moving occlusion rule (2026-11-11):** ใน dialogue scene ให้ตั้ง eyeline ก่อนออกแบบกล้อง: ใช้ iClone Look At ผูกตัวละครกับ Head bone ของคู่สนทนาจริง เพื่อให้สายตายังถูกต้องเมื่อเปลี่ยนหรือแพนกล้อง. อย่าจัดกล้องโดยสมมติว่าตัวละครมองถูกอยู่แล้ว. หากใช้ OTS หรือ foreground shoulder/shirt ต้องตรวจทั้งช่วงโมชั่นหลายเฟรม อย่างน้อย start/mid/end และเพิ่มจุดเมื่อ motion มาก; ห้ามอนุมัติจาก still เฟรมเดียว. ถ้ามีโอกาส foreground/แขน/เสื้อบังหน้า subject ให้ย้ายกล้อง ลด foreground ให้เหลือ sliver ที่ปลอดภัย หรือเปลี่ยนเป็น clean 3/4/profile/dirty single. Face visibility สำคัญกว่า forcing OTS. หลังตั้ง Look At ต้อง re-QA ทุก dedicated camera เพราะ head orientation เปลี่ยน framing ได้.
- **Part 3 original-audio continuity + every-frame review (2026-11-11):** คลิปย่อย 3.1/3.2/3.3/3.4 เป็น visual event เท่านั้น; master ต้องยาว 67.40s = 2,022 frames ที่ 30fps และใช้ WAV ท่อน3.wav ฉบับเต็ม 3,235,200 sample frames @48kHz โดยไม่ตัด/ซ้ำ/ยืด/บีบ/กระโดดเสียง. ตอนประกอบตัดเสียงของ MP4 ย่อยทิ้งทั้งหมด แล้วใส่ original WAV เป็น audio track เดียว. ตรวจ EDL ให้ครบ [0,2022) ไม่มี hole/overlap; 3.1.mp4 ปัจจุบันยาว 72.433s จึงเลือก VIDEO เพียง 1290 เฟรมแรกและห้ามทับต้นฉบับ. 3.2 ต้องไม่ข้ามช่วง 43–52.94; ต้องมีภาพตามบทตลอดช่วง. QA ช็อตเสี่ยงที่ 30fps ทุกเฟรม (contact sheet 30 เฟรม/แผ่น), เช็กก่อน/หลังทุกคัต; re-QA ทุกเฟรมของช็อตหลังแก้. ห้ามเรนเดอร์คลิปใหม่ก่อนผู้ใช้ตรวจอนุมัติ. เอกสาร docs/part3_audio_continuity.md; EDL data/part3_frame_edl.json.
- **การแยกมอง/คุย/เดินแบบตัดจริง 3.2–3.3 (2026-11-11):** ต้องแยกไฟล์ iProject/iVideo ตาม ACTION จริง: คลิปมอง/ฟัง/คุยอยู่กับที่ให้การกระทำนั้นจบก่อน; ห้ามให้คนในคลิปเดียวมอง→หมุนตัวกลับ→เริ่มเดินเพราะ transition ไม่เนียน. เมื่อ action เดินเริ่ม ให้ขึ้นเลขคลิปใหม่โดย **เฟรมแรกของคลิปใหม่นั้นต้องเห็นตัวละครกำลังเดินอยู่แล้ว**, เดินต่อเนื่องตลอดคลิปจนจบ; ห้ามแทรก reaction ยืนมองกลับเข้ากลางคลิปเดิน. เปลี่ยนมุมกล้องระหว่างคลิปเดินได้โดยไม่เปลี่ยนเลข. การหมุน/เปลี่ยนทิศที่ทำไม่ได้สมูทต้องจัดให้อยู่นอกจอหรือแยก action ไม่สร้าง spinning/body teleport ในเทค. ล่าสุด 3.2=43.000–54.200s (ยืนมอง/ตอบสนอง), 3.3=54.200–59.133s (พ่อกับเมียน้อยเดินตั้งแต่ต้น). เสียงท่อน 3 WAV เดิม 67.40s **ไม่แบ่ง/ไม่ขาด/ไม่ซ้ำ**, master ใช้เสียงต้นฉบับครั้งเดียว. ห้ามเรนเดอร์คลิปใหม่ก่อนผู้ใช้ตรวจอนุมัติ. ตรวจจุดตัด global frame 1625→1626 @30fps. อ้างอิง data/part3_frame_edl.json.

- **BEFORE ANY DELIVERY read docs/DELIVERY_CHECKLIST.md and show it as a task list; do every item without being asked (user, 2026-11-11).**

## PART4_2_MERGE_AND_STATIC_COMFORT_20261111
- 4.1 + 4.2 is ONE continuous factory-working event in E:/ไฟล์งาน/ไฟล์ Save/นิทาน/4.1.iProject. Part4 local 0.0-30.3s, 35.3s iClone timeline including tail. 4.2 work is local 15.3-30.3s. DO NOT create duplicate 4.2.iProject or split merely at camera switches.
- Use the real สุนีย์ (red floral blouse, hair bun), not scene placeholder Sunee; keep placeholder hidden. Factory work: slow, small natural movement, no gratuitous turn/walk/drama.
- Latest user rule for 3.4 comfort: FAKE EMBRACE by camera composition; characters grouped and almost still, only very small head/breathing motion. NO exaggerated Hug Kid mocap, no required literal arm contact, no forced transitions, and NO Look At on 3.4. Existing 3.4 is NOT verified updated to this direction.
- Do not render 4.1/4.2 before user approval; contact-sheet QA is not a finished MP4. Story WAV must be continuous across 4.1+4.2 to 4.3.
- Live iClone 4.1 has two Cam41_A/B cameras, six switches, 28 props. Read-only QA checked 18 source frames during 15.3-30.2s: visible red-clad Sunee, mixing bowl and restrained work. See docs/part4_2_qa_20261111.md.
