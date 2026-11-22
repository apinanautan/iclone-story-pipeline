# CURRENT STORY — updated 2026-11-22 (read this block first; older notes below are history)
- เรื่อง: ชัยชนะของคนไม่ยอมแพ้
- ท่อน 6 (ท่อนสุดท้าย, 376.39–434.00 จากเสียงต้นฉบับ, 57.61 วินาที): ใช้ Preview และ `parts/ชัยชนะของคนไม่ยอมแพ้_6.json` ฉากโรงทำอิฐมอญต้นฉบับเปิดจากสำเนาในเครื่องที่ `{SAVE}/_pipeline_cache/ชัยชนะฯ_ต้นฉบับโรงทำอิฐมอญ.iProject` หลังเปิดจากไดรฟ์แชร์ไม่ผ่าน. บันทึกโปรเจกต์ `{SAVE}/ชัยชนะของคนไม่ยอมแพ้/ท่อน6.iProject` พร้อมเสียงบรรยายท่อน 6 ที่เฟรม 0. ใช้โมเดลน้องชายชัยยศจากโฟลเดอร์เรื่อง, ลูกค้าใช้โมเดลสมทบจากคลังเรื่อง. มี 11 ช็อตและป้ายขายอิฐหน้าอาคารกับริมทาง. ตรวจภาพจริง 53 ภาพครบ 11 ช็อต, motion_check, light_check และ face_check ผ่าน, Project Sound มีท่อน6 ที่เฟรม 0, ตั้ง Switch แล้ว. รอขั้นผู้ใช้ตรวจ (ผ่าน) ใน Preview ก่อนเซฟกล้องรอบสุดท้ายและเรนเดอร์. ภาพตรวจอยู่ที่ {DESKTOP}/ชัยชนะของคนไม่ยอมแพ้/ภาพตรวจ/ท่อน6.
- ท่อน 1: DONE, rendered {VIDEO}/ชัยชนะของคนไม่ยอมแพ้/GPT_ท่อน1_20261120.mp4
- ท่อน 2 (โรงอิฐ, 76.07 s): DONE. Saved via GUI to {SAVE}/นิทาน/ชัยชนะของคนไม่ยอมแพ้/ท่อน2_โรงอิฐ_20261121.iProject. Rendered {VIDEO}/ชัยชนะของคนไม่ยอมแพ้/GPT_ท่อน2_20261121.mp4 (1080p60, sound, video_check OK). Spec: parts/ชัยชนะของคนไม่ยอมแพ้_2.json (good template for part 3: landmark-relative cast, in-place motions, subject auto-aim, face_light_multiplier 0.15).
- ท่อน 3 (บ้าน, 83.72 s): DONE. Rendered {VIDEO}/ชัยชนะของคนไม่ยอมแพ้/GPT_ท่อน3_20261121.mp4 (re-render with textures, OCR texture wait before render).
- ท่อน 4 (บ้านนายชัยยศ / ร้านชำหน้าบ้าน, 84.90 s, master 225.92-310.82): RENDERED 2026-11-22 (user ผ่าน): E:/Video/ชัยชนะของคนไม่ยอมแพ้/GPT_ท่อน4_20261121.mp4, 84.9 s 1080p60, video_check OK. Camera bounce left for later parts. Only อัมพร + ชัยยศ (no siblings). Spec parts/ชัยชนะของคนไม่ยอมแพ้_4.json; project {SAVE}/ชัยชนะของคนไม่ยอมแพ้/ท่อน4_บ้านชัยยศ_20261121.iProject. All motions slow 0.65-0.7, heroine calm/modest poses, smile keys (couple 0.7), clips back to back with 2 s transition (no overlap), face_light_multiplier 0.2. iClone crashed 2026-11-22 after the 22:14 save; reopened, cams re-run. 2026-11-22 added TV shot (user): 62.68-68.12 อัมพร_ทีวี sits on a stool (PRK_Bench_Sit_Relax_01A_F 0.65) watching an old CRT TV, camera behind her shoulder, TV blank. Props via spec "props" (Tidmunz old_crt_tv + wood_stool, fbx scale 100). Newspaper shot now 47.7-62.68. Saved 07:37. Stills: docs/review/p4_cams_v4_tv.jpg, docs/review/p4_tv_shot.png. 2026-11-22 09:4x full re-run with the new face flow (blink + Digital Soul face clips 70% + smile ramp 10->max 80%, thinking face) and clip joins (clips only on screen, 1 s gap, crossing X); อัมพร_ร้าน motion_from 0 (calm phase of the cashier motion). All checks pass. Stills: docs/review/p4_cams_v5.jpg. Next: user ผ่าน -> ready -> render --approved -> video_check.
- WORK THROUGH THE PREVIEW (user 2026-11-22): run every change as ic8_part.py steps so progress_app.py shows the true state; after any iClone (re)open, OCR-check until no popup / Texture Loading is left.
- Pipeline (ic8_part.py) ORDER: check, motion_plan, open, cast, pose, sound, lip, cams, motion_check, light_check, switch -> user says ผ่าน -> ready (GUI save) -> render --approved (+video_check). Preview (progress_app.py) shows every step with live %.
- New since 2026-11-21: Thai keyboard breaks Ctrl+S (ic8_gui.ps1 switches to English); per-cast shadowless face spotlight linked to the head (untested in iClone yet); render wait limit 2 h.

- เรื่อง: ชัยชนะของคนไม่ยอมแพ้ / ท่อน 1 / เสียงต้นฉบับ 0:00–1:06.13 (66.13 วินาที)
- สถานะที่ผู้ใช้ยืนยัน: **ท่อน 1 ยังไม่เสร็จ**; ยังไม่ผ่าน QA การเล่าเรื่อง ภาพ และกล้อง; ห้ามอ้างว่าเป็น final หรือเรนเดอร์
- Source: {DRIVE}/ชัยชนะของคนไม่ยอมแพ้/บท - ชัยชนะของคนไม่ยอมแพ้.docx; {DRIVE}/ชัยชนะของคนไม่ยอมแพ้/เสียง - ชัยชนะของคนไม่ยอมแพ้.wav
- ฉาก: {DRIVE}/ชัยชนะของคนไม่ยอมแพ้/ฉาก/บ้านของครอบครัวอำพร (ค่อนข้างยากจน) ตอนสร้างใหม่.iProject
- ตัวละครตาม story.json: พ่ออัมพร, แม่อัมพร, อัมพร; ช่วงนี้เป็นเสียงบรรยายล้วน ไม่มีบทพูดตัวละคร/ลิปซิงก์
- เนื้อหาท่อน 1 ตามบท: อัมพรลูกสาวคนโตในบ้านยากจน; พ่อแม่รับจ้างทั่วไปเลี้ยงลูกสี่คน; ฐานะพอกินพอใช้แต่ไม่มีเงินเก็บ; ท้ายท่อนอัมพรเริ่มช่วยงานบ้าน
- ภาพต้องแสดงกิจกรรมรับจ้างและช่วยงานบ้านจริง ไม่ใช้การตัดกล้องวนพ่อ–แม่ที่ยืนนิ่ง; บันทึก spot/cam ที่อนุมัติใน story.json ก่อนใช้งานจริง
- เสียงตัดแล้ว: {DESKTOP}/ชัยชนะของคนไม่ยอมแพ้/เสียงที่ตัดแล้ว/ท่อน1.wav พร้อม ท่อน1.json 8 ช่วง; ต้องนำ transcript พร้อม who/about ไป story.json ในสเต็ป 2/3
- โปรเจกต์ที่เคยเซฟเพื่อทำงานต่อ: {SAVE}/ชัยชนะของคนไม่ยอมแพ้/GPT_ท่อน1_20261120.iProject; มี Sound และ Timeline ~71.12 วินาทีที่ตรวจหลัง reopen แต่ภาพชุดเดิม **ไม่ผ่าน**
- ผลลัพธ์เป้าหมายแยกจากไฟล์ร่าง: {SAVE}/ชัยชนะของคนไม่ยอมแพ้/ท่อน1.iProject และ (หลังอนุมัติเท่านั้น) {VIDEO}/ชัยชนะของคนไม่ยอมแพ้/1.mp4
- จุดขาดก่อนสร้าง: story.json scene spots/cams ยังว่าง; ยังไม่พบ avatar อัมพร *วัยเด็ก* ยืนยันตรงบท; ห้ามใช้ avatar วัยสาวแสร้งเป็นเด็กก่อนอนุมัติ
- สถานะกระบวนการ: จบสเต็ป 0; ตรวจ brief และบท .docx สำหรับสเต็ป 1 แล้ว; รออนุมัติแผนภาพตามสเต็ป 1 — ห้ามลงมือ iClone ต่อก่อนได้คำว่า โอเค
## 2026-11-20 หลังอนุมัติสเต็ป 1
- จบสเต็ป 2: ยืนยัน ท่อน1.wav PCM16 48kHz stereo 66.130s, แหล่งเสียงตรงกับ Master เรื่องนี้ (1317.692s); ใช้ไฟล์ cut_audio.py เดิม ไม่ตัดใหม่/ไม่ทับเสียง.
- บันทึก transcript 8 ช่วงที่แก้คำตามบท .docx ลง stories/ชัยชนะของคนไม่ยอมแพ้.json parts[1].transcript; ยังไม่สร้างกล้องใหม่หรือเรนเดอร์.
- สถานะ: audio_verified_transcribed_pending_stage; กล้อง/จุดยืนต้องสำรวจและให้ผู้ใช้อนุมัติก่อนใช้งาน.

## สำรวจจุดยืน/กล้องหลังอนุมัติแผน (2026-11-20)
- สเต็ป 2 จบ: ยืนยันเสียง 66.13s PCM16 48kHz stereo, ต้นฉบับเรื่องถูกต้อง, transcript 8 บรรทัดบันทึกใน story.json
- สเต็ป 3 ยังไม่ผ่าน approval gate: story.json เก็บ spot 3 ชื่อ + cam 3 ชื่อ ทุกชื่อ approved=false; ไม่มีการคีย์มุมเหล่านี้เป็น production
- Scene scan จริง 48 props + 4 avatars + 2 cameras, errors=0.
- ภาพสำรวจ 4 มุมจาก iClone: 
C:\Users\Apinan\AppData\Local\Tidmunz Studio\snapgen_data\ic8_jobs\scene_overview\wide_scene_overview_sheet.jpg
- ภาพตรวจตัวละครกล้อง 80/100mm 4 มุมจาก iClone: 
C:\Users\Apinan\AppData\Local\Tidmunz Studio\snapgen_data\ic8_jobs\scene_overview\scene_camera_candidates_sheet.jpg
- QA: A1/A2 มองหน้าแบบ 3/4 ได้ แต่ยังต้องแก้ช่องว่างเหนือหัว/โมชั่น/พร็อพ; B1/B2 เป็น profile ใช้ไม่ได้; overview 01 มีต้นไม้บัง ไม่อนุมัติเป็น shot
- คลังเรื่องนี้ไม่มีอัมพรเด็ก; มีโมเดลหญิงวัยประถมในเรื่องอื่น เช่น กรงกตัญญู/อรวรรณ วัยประถม และ ดวงเมียน้อย/นาวีวัยประถม แต่ยังไม่ได้รับอนุมัติให้ใช้แทน
- ห้ามเปิดท่อนใหม่, วางโมชั่น, ใช้ภาพเป็น final, ลิปซิงก์ หรือเรนเดอร์ จนได้รับคำอนุมัติจุดยืน/กล้องและโมเดลอัมพรเด็ก
- ไฟล์ iProject เดิม GPT_ท่อน1_20261120.iProject ไม่ถูกทับ; บันทึกเสียงในโปรเจกต์และเปิดใหม่ผ่านในรอบก่อน; ยังไม่มีท่อน1.iProject final.

## 2026-11-20 — Actual iClone camera + 1fps still QA (not final)
- Stage updated in iClone: father Sawing.rlMotion (local safe motion, 9 clips), mother LivingRoom_DoChores_F.rlMotion (7 clips); unsuitable Yard_Weeding_M root travel was rejected; adult Amphon hidden during entire part (no child model approved).
- Camera spec changed and run in iClone; Cam_A/B with 7 actual switcher shots, first house wide now 4.7s; viewport switched to Switch at frame 0 (Qt verified).
- RenderImage QA: 
54
 172 with labels. Latest ic8_part.py cams run exits 0; RLPy camera position error 0cm after Linear key transition; still_check.py OK.
- Visual QA deliberately FAILS: father Sawing bends head too low near frame edge in some frames (S02/S04/S06); mother work action unclear in shot3/5/7; no child Amphon housework in S07. These are not approved frames; no final render.
- Sound: Project > Sound has ท่อน1.wav at time0; master length 66.13s, project and End/PreviewEnd 71.1167s including 5s tail.
- Draft save/reopen verified GUI 2026-11-20 21:42:31: {SAVE}/ชัยชนะของคนไม่ยอมแพ้/GPT_ท่อน1_20261120.iProject (1,637,235,379 bytes). Final ท่อน1.iProject NOT created; video NOT rendered.
- All scene candidate spots/cams in story.json remain approved=false. Next: reframe low working motions, strengthen visible household chores and choose approved child actor, then repeat complete moving/camera QA and ask review.

- Reopen QA confirmed 7 saved Switcher keys at 60fps: frames 0, 282, 955, 1665, 2184, 2625, 3088; Qt viewport Switch. Visual QA still FAILED, no final video.

## 2026-11-20 22:37 — ท่อน 1: ภาพตรวจรอบปัจจุบัน (รออนุมัติ ไม่ใช่ final)
- User instructed to continue part 1. Used shared ic8_part.py cast/pose/cams on DESKTOP-F1PJT4S, not another machine.
- Imported an explicitly TEMPORARY child trial avatar อัมพรเด็ก_ตัวทดลอง based on {DRIVE}/กรงกตัญญู/กรงกตัญญู/3. อรวรรณ/อรวรรณ วัยประถม.iAvatar; original asset remained untouched. This model is NOT approved as Amphon.
- Trial girl staged at [-2520,-3259,-34], motion Yard_Watering_C.rlMotion; visible from 51.48s. Real adult Amphon remains hidden. Father Sawing.rlMotion; mother LivingRoom_DoChores_F.rlMotion (rejected squat clip because it moved the head out of frame).
- Storyboard: 7 camera switches; house 0-4.7, father 4.7-15.93, mother 15.93-27.76, father alternate 27.76-36.4, mother alternate 36.4-43.76, porch/grassy yard detail 43.76-51.48, temporary girl 51.48-66.13.
- Latest checked spec: parts/ชัยชนะของคนไม่ยอมแพ้_1.json check OK. review_per_sec=1; actual cams exit0, 54 stills across 7 contact-sheet pages, still_check.py OK.
- Contact sheets copied for user to Desktop/ชัยชนะของคนไม่ยอมแพ้/ภาพตรวจ/ท่อน1/ท่อน1_ตรวจกล้อง_20261120_223732: 00 overview + 01-07 per-second pages; opened overview on Windows desktop.
- Visual QA remains NOT FINAL: saw/work motions lack visible saw/props, some father frames show bent head instead of face; child watering gestures lack visible watering can and is from another story; shot 6 porch detail is simple. Need user approval/adjustment before final iProject.
- iClone currently UNSAVED (*) with new cast/camera work; do not close or discard. Existing saved GPT_ท่อน1_20261120.iProject remains fallback, no final ท่อน1.iProject, no MP4; save via GUI only after approval.
- Project Sound remains ท่อน1 at time0; 66.13s, stage ProjectLength/End 71.1167s. Qt viewport set to Switch and 7 switcher keys present.
- FIX: ic8_part.py job staging moved out of watched run/ to prevent race, ic8_cams.py accepts no_dof for architectural inserts; both compiled.
## 2026-11-20 - 480p trial rendered and verified on NTFS
- Source project separately saved using GUI as E:\ไฟล์งาน\ไฟล์ Save\นิทาน\ชัยชนะของคนไม่ยอมแพ้\GPT_ท่อน1_ทดลอง480p_20261120.iProject (1,805,399,205 bytes).
- Native 480p60 iClone rendering finished and the clean original audio was muxed. Native export was 852x480, encoded preview scaled to exact 854x480.
- Verified output E:\Video\ชัยชนะของคนไม่ยอมแพ้\ท่อน1_480p_ทดลอง.mp4, 10,142,564 bytes, H.264 854x480 at 60fps, 66.133333 seconds, AAC.
- Full decode success. Audio volume mean -22.3 dB, max -2.6 dB.
- SHA256 9B476CF1867D8CB75C99F9A8A889F2662193A2800370D0BEEE766AF8345E267D.
- The user requested a TEST video, not approval of the visual QA. Temporary child actor and weak-looking work motions remain unapproved for final.

## ntfy delivery verified — part 1 trial 480p
- User explicitly requested delivery to ntfy; confirmed topic Pic-Gptz from project rules dated 2026-11-10.
- Notification attachment uploaded successfully, HTTP 200, id mUJ6Wkv2hIRg, link https://ntfy.sh/file/mUJ6Wkv2hIRg.mp4.
- ntfy size-limited copy: 1,714,224 bytes, H.264 854x480 at 20 fps, AAC mono, 66.15 seconds; compressed to fit ntfy attachment size limit.
- Original full-quality test remains E:\Video\ชัยชนะของคนไม่ยอมแพ้\ท่อน1_480p_ทดลอง.mp4, 10,142,564 bytes, 854x480 at 60fps, 66.13s.
- Receipt saved %LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\part1_480p_ntfy_receipt.json. Do not send duplicate notification.
- Delivery does not mean story Visual QA is approved or final.

## 2026-11-21 — Part 1 true front of house (verified after reopen)
- User rejected earlier camera because it showed the rear/side of main house node_0.
- Surveyed all sides using iClone RenderImage; true FRONT is NORTH with broad staircase and entry porch.
- Selected clean north-front camera [-2000,-1350,950], target [-1710,-4600,530], focal 36; northwest views rejected due foreground decorative roof obstruction.
- Camera actual still QA passed 54 images, seven shots. Reopened new saved iProject, verified Cam_A at 1.9s (-2000,-1355,949), focal36, Switch viewport with seven keys.
- Source saved separately: E:\ไฟล์งาน\ไฟล์ Save\นิทาน\ชัยชนะของคนไม่ยอมแพ้\GPT_ท่อน1_หน้าบ้านจริง_แก้คอ_20261121.iProject 1,772,540,919 bytes.
- Character work tracking disabled and saved: father/mother/child trial face clips=0, both LookAt weights=0. Child motion still has maximum 8.65 degree change in one 60fps frame. Do not claim final smoothness or re-rendering.
- Correct before/after image and seven contact sheets in Desktop\ชัยชนะของคนไม่ยอมแพ้\ภาพตรวจ\ท่อน1\แก้เป็นหน้าบ้านจริง_20261121.
- Earlier 480p ntfy video was NOT replaced and still contains the rejected opening angle.

## 2026-11-21 — Delivered new color 480p front-house revision
- User requested corrected Part 1 video in color at 480p; reused saved/verified GPT_ท่อน1_หน้าบ้านจริง_แก้คอ_20261121.iProject.
- Native iClone render saved at E:\Video\ชัยชนะของคนไม่ยอมแพ้\ท่อน1_480p_หน้าบ้านจริง_20261121_raw.mp4 (14,783,896 bytes, 852x480 at 60 fps, initial 71.136s including tail).
- Final color 480p with clean WAV trimmed 66.1333s: E:\Video\ชัยชนะของคนไม่ยอมแพ้\ท่อน1_สี480p_หน้าบ้านจริง_20261121.mp4 (10,077,069 bytes; H.264 yuv420p 854x480 60fps AAC), full frame decode checked.
- ntfy 2MB-size copy: E:\Video\ชัยชนะของคนไม่ยอมแพ้\part1_color_480p_front_house_ntfy.mp4 (1,641,991 bytes; color H.264 854x480 at 20fps; AAC; 66.15 sec).
- ntfy Pic-Gptz confirmed HTTP 200, event id 6JQy28tHY7Dg, attachment https://ntfy.sh/file/6JQy28tHY7Dg.mp4. Receipt saved part1_color_front_house_ntfy_receipt.json; NEVER duplicate on retry.
- Independently extracted 7 representative frames from the FINAL 60fps video and inspected visibly in color; shot1 truly shows stair-front view of node_0. Other shots show working father/mother/child but work poses are not final QA-approved.
- IMPORTANT: this is a preview and does not supersede user approval for 1080p final. Previous rejected 480p ntfy video remains separate and must not be mistaken for current.
