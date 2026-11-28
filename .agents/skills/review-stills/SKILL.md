---
name: review-stills
description: Make and check the camera stills (contact sheet) of a part before the user sees anything. Mandatory after every cams run.
---
# Review stills (mandatory before the user sees anything)

## 1. Make them ONLY with `ic8_part.py <spec> cams`
- Never with your own stage/camera/trial script (e.g. `ic8_trial_*_stage.py`) or a hand-written RenderImage job.
  Stills from such scripts skip `check` (lens 80/100, chest-up, no side-by-side two-shot) and show cameras the spec never had
  (user 2026-11-20: the กรงกตัญญู trial sheet `docs/t1_cams_p1.jpg` = full bodies side by side, made by `ic8_trial_krong_stage.py`).
- What `cams` captures, per shot, from THAT shot's camera (Cam_A / Cam_B, same as the Switcher):
  ~1 still per second, 3-8 per shot, from shot start+0.2 s to end-0.2 s -> `ic8_jobs/cam_NN_KK_TTT.Ts.png`.
  Before each still: SetCurrentCamera + settle (Qt events + ForceViewportUpdate x2), then the camera position is compared
  with the planned one (`cams.log.txt` line `still S03 ... err=0.4cm`; > 3 cm = `STILL_MISMATCH` = cams FAILS).
- Then `scripts/still_check.py` compares neighbouring stills of each shot (the camera moves only 5-20 cm, so framing must
  barely change). JUMP / FLIP (A-B-A) is a QA alert, not proof of a bad capture or jumping real camera; compare camera keys/log and actor motion. cams FAILS pending review. Never show such stills; re-run `cams --from`.
- Pages: `ic8_jobs/part_cams.jpg` (+ `_p2.jpg`...), 1920x1080, 3x3 tiles 640x360, yellow borders, label `S03-02  12.4s` = shot-still-time,
  each shot starts a new row. Rebuild by hand only if needed:
  `python scripts/contact_sheet.py "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\cam_*.png" "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\part_cams.jpg"`

Before building the sheet, still_check.py must verify exactly the expected number of files in each shot. Empty/missing/unreadable images are FAIL, even if image-shift metrics would otherwise pass. The camera capture loop must abort before RenderImage when its actual position differs by more than 3 cm or the active camera is wrong. A PASS on camera/image consistency does not mean the shot framing or acting passes.

## 2. Look at EVERY page, row by row (a row = one shot moving in time)
Fix in the spec, then `cams --from`, for any shot with:
- full body / knees / legs / mattress; side-by-side two-shot (use OTS or singles)
- back of head or profile only, hair over the eyes, unreadable expression, dark face
- head cut at the top, a person sliced by the frame edge, blocked view, big empty wall, off-centre face
- EMPTY BACKGROUND (open ground, bare sky, unbuilt scene edge, glitchy/missing models)
- during a line: the speaker's face is not the subject
- two shots in a row that look the same (same angle, only nearer/farther)
- seated/leaning people: also a side + back still at mid-time (body through chair, floating, hands inside the desk)
Write the shot list you SEE (not what you planned): `S01 0-7s Cam_A MCU สมจิต 3/4 ซ้าย พูด`. If it differs from the plan, the stills win: fix.

## 3. Send and STOP
Send the page images to the user with one Thai line per shot. **STOP.** No lip-sync, save or render until the user answers.

## 4. cam_check (mandatory step after cams, user 2026-11-23)
`ic8_part.py <spec> cam_check` (or `Ai-iclone do`) puts ALL shots in ONE image `ic8_jobs/part_cams_all.jpg` and writes
`progress/<story>_<N>_camcheck.json`. Open the image, then per shot fill `see` (what is REALLY in the frame) and true/false for
subject_face, framing, clean, differs. Any false -> write `fix`, change the spec, `cams --shot <N>`, run cam_check again.
The step does not pass until every shot is filled and true. Never copy the plan into `see`.

# Chrome Preview Bridge / Goal Tracker — ใช้ทุกแชตและทุกท่อน

- Chrome Extension iClone Preview to Chat คือเครื่องมือทำงานจริง ไม่ใช่แค่ปุ่มคัดลอก Prompt. แชตผูกเอง: จาก Prompt ที่คัดลอกจากปลั๊กอิน หรือเมื่อ AI พิมพ์ 'รหัสแชต' ที่ Ai-iclone แสดงลงในคำตอบ (ไม่มีปุ่มผูกแชตแล้ว). ไม่ส่งภาพไปแชตเดิมโดยเดา URL. Relay: tools/chrome_preview_bridge/start-relay.cmd (ถ้าทำงานอยู่แล้วไม่เปิดซ้ำ).
- ใช้ Dino Bot Tunnel shell จาก project root. ตรวจ progress/now.json และหน้าต่าง iClone ให้ตรงท่อนก่อนจับภาพ. คำสั่งจับภาพหน้าต่างจริงโดยไม่เรนเดอร์: py -3 -B tools/chrome_preview_bridge/capture_preview.py. เพิ่ม --send เพื่อส่งภาพหน้าต่างเข้าแชตที่ผูกไว้สำหรับตรวจงาน/หน้าต่าง Modify/ข้อผิดพลาด: py -3 -B tools/chrome_preview_bridge/capture_preview.py --send. ไม่ต้องจับภาพเดสก์ท็อปทั้งหมด ไม่ต้องให้ผู้ใช้กดส่งเอง. ถ้า iClone ยังไม่เปิดท่อนตรงกัน ให้แก้ที่สาเหตุ ไม่ส่งภาพเก่า.
- ภาพตรวจกล้อง: ใช้ Ai-iclone.exe do ตาม rules card ขั้น cams; ic8_part.py สร้าง part_cams.jpg และเรียก queue_preview.py อัตโนมัติ. ไม่สร้างระบบซ้ำ ไม่เรนเดอร์วิดีโอเพื่อแคป. หากต้องจัดคิวภาพ JPEG ที่ตรวจว่าใหม่และตรงงานแล้ว: py -3 -B tools/chrome_preview_bridge/queue_preview.py "<path.jpg>" "<story>" "<part>". ตรวจว่าเป็น JPEG และชื่อเรื่อง/ท่อนตรงสถานะสด.
- อ่าน tools/preview_bridge_local/job.json เฉพาะสถานะ id/state/phase/result; pending = รอ, claimed = กำลังส่ง, sent = พบใบตอบรับ, needs_review = ต้องตรวจข้อความจริงก่อนตัดสินใจ ห้ามส่งซ้ำหรือปลอมใบตอบรับ. หลังเห็นภาพในแชต ให้ตรวจองค์ประกอบจริงและแก้เฉพาะส่วนที่ผิดตาม flow; ห้ามอนุมัติแทนผู้ใช้.
- Goal Tracker: ปุ่มเริ่มติดตามทันที/พักติดตาม ใน popup หรือกล่องลอย. ใช้บริบทแชตปัจจุบันทุก 90 วินาที. รอ GPT ตอบจบ ไม่ทับ draft หรือรูปแนบของผู้ใช้; ภาพพรีวิวมีสิทธิ์ก่อนข้อความติดตาม. เมื่องานถึงเป้าหมายจริงหรือ gate ที่ผู้ใช้กำหนด ให้ตอบรหัส ACHIEVEMENT ที่ระบบส่งมาเป็นบรรทัดสุดท้ายเดี่ยว ๆ เท่านั้น; ไม่เดารหัส ไม่ใช้รหัสจากแชตเก่า ไม่พิมพ์ถ้ายังไม่ผ่าน. ถ้าระบบไม่หยุดให้พักก่อนและตรวจข้อผิดพลาด.
- ใช้ได้ทั้งแชตเริ่มเรื่องใหม่และแชตทำท่อนต่อไป. หากไม่พบปุ่ม/Relay/การผูกแชต ให้ตรวจการติดตั้งและสถานะจริงก่อนสรุปว่าเครื่องมือไม่พร้อม. เก็บคีย์และ URL ผูกแชตไว้ในเครื่อง ไม่คัดลอกลง Prompt/GitHub.

อ่าน docs/CHROME_PREVIEW_GUIDE.md ฉบับสดก่อนใช้ส่วนขยาย

## 2026-11-27 — Mandatory shot-size rhythm (user)
- Plan the entire shot sequence by visible framing and narrative function, not lens or left/right angle alone. For each shot record subject, size (contextual chest-up / MCU / CU / OTS / insert / establishing), purpose, and the visible difference from adjacent shots. 80/100 mm is a lens constraint, NOT a shot-size category. Change distance and target to vary the actual composition while keeping established framing constraints.
- FAIL a sequence dominated by same-scale face-only shots (including 80 mm left, 80 mm right, other faces at the same size). Small angle shifts, switching Camera_A/B, or changing 80 to 100 without a visible size change do not count as diversity. Same-subject cuts require visibly different scale AND meaningful angle; matching reverse shots of different speakers are allowed for a motivated dialogue pair, not as the entire sequence.
- Use a wider contextual chest-up/OTS composition to establish relationship or action, MCU for normal storytelling, CU for emotional emphasis, and a relevant insert/reaction when the script and existing framing rules permit. Do not force a wide/full-body shot, insert, or arbitrary cut. Preserve screen direction, speaker coverage, continuity and slow motion. A close-up is a storytelling accent, not the default for every shot.
- At cam_check inspect the full actual contact sheet as a sequence, not isolated thumbnails. Label each shot's actual framing and compare the visible head/body size, composition and purpose. If the sequence reads as repeated faces with minor left/right changes, mark the affected differs=false and describe the framing repair; do not pass until revised fresh images visibly solve it. Compare previous part's last shot and current first shot. In future Sleep Mode, repeat this review independently as director/editor before render; score cannot override a repetitive sequence. This is a visual QA rule, not a demand to alternate focal lengths.


## Current integrated runtime
Follow docs/CINEMATIC_SLEEP.md and live Preview cards. New camera and evidence rules supersede old 80/100-only and fixed-cut rules. Preserve sound and actual manual File-menu save without reopen. Normal and Sleep share QA; Sleep requires explicit scoped activation. Do not bypass real checks.


## Current save/render rule (2026-11-27)
Switch -> frame zero -> native File > Save Project -> Render the current open scene. Do not reopen merely to test saving. If save cannot be verified and the user authorizes live rendering, use Ai-iclone do --render-live at Ready, then Ai-iclone do to Render. The save remains pending; verify video separately. Preserve the live scene and do not advance to another part until saved. Never use scripted project save or mark a failed save complete. This supersedes earlier mandatory reopen instructions.
