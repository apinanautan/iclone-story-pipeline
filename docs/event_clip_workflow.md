# Event-Clip Production Workflow — iClone Story Pipeline

**CURRENT / MANDATORY (2026-11-11)** — supersedes the old one-long-timeline-per-audio-part approach when a part contains distinct acting/movement events.

## Core rule
**One numbered clip = one complete dramatic event / acting block.**

Finish that event, inspect it, save it, render/check it, then move to the next numbered clip.

Do NOT:
- build the entire Part 3 as one long timeline first
- create a new clip number because the camera changes
- create a new clip number because the speaker changes
- create a new clip number for every reaction
- split at arbitrary audio timestamps

Create a new numbered clip only when the MAIN EVENT/ACTION changes.

## Boundary decision
Ask: **Has the main event changed?**
- Same event + new camera = SAME numbered clip.
- Same conversation + another speaker = SAME numbered clip.
- Reaction caused by a line inside that conversation = SAME numbered clip.
- Conversation ends and actor decides to leave / turns / starts walking = NEW numbered clip.
- Walking-away event ends and focus becomes mother+children aftermath = NEW numbered clip.
- Comfort event ends and a new walk-home movement sequence begins = NEW numbered clip if it needs separate movement direction.

## Required workflow for EACH numbered clip
1. Define one event only.
2. Build only that event: blocking, body motion, face, eyeline, lip-sync, hands/contact, reactions.
3. Design camera coverage inside the event. CU/MCU/OTS/reaction/cutaway can all remain inside the SAME numbered clip.
4. QA the event as moving video, not just stills/contact sheets.
5. Save its own project, e.g. 3.1.iProject.
6. Ask user before rendering unless explicit render permission for that event already exists.
7. Render that event as a reviewable file, e.g. 3.1_preview480.mp4.
8. Watch the rendered file and verify sound, lips, face, motion, camera, reactions, first frame, last frame.
9. If it fails, fix THAT event and rerender it. Do not begin the next event to hide unfinished work.
10. Only after it passes begin 3.2, then 3.3, etc.
11. After all events pass, assemble them into one continuous Part 3 master and verify joins.

## Camera and reaction are NOT file boundaries
Example inside 3.1:
- MCU father talking
- mother reaction
- OTS back to father
- child reaction
- close father finishing line

All remain 3.1 if the event is still the standing conversation.

Reaction belongs after/between the stimulus that causes it, but normally stays inside the same numbered event.

## Movement direction
For movement events direct:
perceive -> gaze -> decision -> breath/prep -> weight shift -> head lead -> shoulders -> hips -> planted foot -> first step -> acceleration/travel

Never:
idle -> instant yaw rotation -> walk loop

When long action exposes animation weakness, use coverage INSIDE that event:
- decision close-up
- turn preparation
- first-step medium shot
- reaction cutaway
- return after actor progressed farther

Maintain world position, root direction/speed, foot phase, pose, eyeline, screen direction and emotional continuity.

## Audio and lip-sync
- Story sound must be visible/audible on Project Sound Track for the event.
- Character dialogue: import full original source through iClone Create Script > Audio File, then trim to actual speaking window inside iClone.
- Do not use arbitrary pre-cut WAV fragments as a shortcut for avatar lip-sync.
- Do not let Project Sound and avatar voice create doubled audio.
- Audio time is for sync, NOT for deciding 3.1/3.2/3.3 boundaries.
- Old fixed chapter-3 split WAVs are reference only unless user explicitly requests them.

## Performance rules
- Characters think/react before major movement.
- Speaker mouth matches dialogue.
- Listeners react on meaningful beats.
- Children do not move in copied/synchronized timing.
- Hands relaxed; contact must read physically.
- If hug/contact fails, change blocking/coverage rather than show penetration.
- Facial performance changes by dramatic beat; no frozen default faces.

## Camera rules
- Film language, not game-camera language.
- Prefer 80/100mm for character coverage, but verify actual framing.
- Prioritize CU, MCU, OTS, three-quarter front, reaction.
- Avoid unnecessary full-body/wide, long rear view, tiny characters, prop-dominant frames, camera through walls, actor drifting out.
- Camera movement minimal and motivated.
- Event ending must visually resolve the event.

## 10-pass moving QA per event
1. Dramatic intention
2. Anticipation
3. Body mechanics
4. Stand/walk/turn transitions
5. Root path / foot slide / collisions
6. Individual rhythm
7. Eyeline / dialogue / lips
8. Hands / contact / weight
9. Camera/framing
10. Edit continuity / event ending

Record timestamp + actor + observed problem + repair + recheck result.

## 15-minute checkpoint
Do not go more than roughly 15 minutes without a real checkpoint. This is not a promise that a polished event finishes in 15 minutes.
Each checkpoint reports only verified progress, defects, fixes, saved/rendered artifacts, and what still fails.

## Two-monitor / startup rule
- User works on monitor 1; iClone production belongs on monitor 2.
- Every launch/relaunch: inspect BOTH monitors for startup blockers.
- Follow docs/iclone_startup_popup_recovery.md.
- Clear only verified dialogs. Never blindly dismiss unknown/save dialogs.
- Prefer non-focus-stealing controls.

## Completion language
Never call an event ready merely because motion/camera/save command succeeded.
Ready for review requires sound, correct dialogue/lips, facial acting, human movement, camera, event QA, and actual reviewable video when rendering was requested.
Final 1080p still requires explicit user approval.
- **Dedicated multi-camera dialogue rule (2026-11-11):** สำหรับ dialogue/event coverage เช่น 3.1 ให้สร้าง custom camera object แยกตามหน้าที่ เช่น Mom CU, Dad CU, two-shot/depth, kids reaction, OTS/profile แล้วใช้ Project > Switcher / AddSwitchCameraKey ตัดระหว่างกล้อง. ห้ามใช้กล้องตัวเดียว teleport/hard-step ไปทุกมุมเป็นวิธีหลัก เพราะแก้ framing/DOF/continuity ยากและทำให้ coverage ดูซ้ำ/ง่อย. กล้องแต่ละตัวควรมีชื่อสื่อหน้าที่, transform/focal/DOF ของตัวเอง; ใช้กล้องเดิมซ้ำได้เมื่อกลับมาที่มุมเดิม. เปลี่ยนกล้องไม่ใช่ event boundary. ก่อน Save ต้องตรวจ camera count, switch-key sequence และ still framing ทุก beat; moving playback QA ยังต้องทำแยกต่างหาก.
- **Gaze-first camera and moving occlusion rule (2026-11-11):** ใน dialogue scene ให้ตั้ง eyeline ก่อนออกแบบกล้อง: ใช้ iClone Look At ผูกตัวละครกับ Head bone ของคู่สนทนาจริง เพื่อให้สายตายังถูกต้องเมื่อเปลี่ยนหรือแพนกล้อง. อย่าจัดกล้องโดยสมมติว่าตัวละครมองถูกอยู่แล้ว. หากใช้ OTS หรือ foreground shoulder/shirt ต้องตรวจทั้งช่วงโมชั่นหลายเฟรม อย่างน้อย start/mid/end และเพิ่มจุดเมื่อ motion มาก; ห้ามอนุมัติจาก still เฟรมเดียว. ถ้ามีโอกาส foreground/แขน/เสื้อบังหน้า subject ให้ย้ายกล้อง ลด foreground ให้เหลือ sliver ที่ปลอดภัย หรือเปลี่ยนเป็น clean 3/4/profile/dirty single. Face visibility สำคัญกว่า forcing OTS. หลังตั้ง Look At ต้อง re-QA ทุก dedicated camera เพราะ head orientation เปลี่ยน framing ได้.
- **Part 3 original-audio continuity + every-frame review (2026-11-11):** คลิปย่อย 3.1/3.2/3.3/3.4 เป็น visual event เท่านั้น; master ต้องยาว 67.40s = 2,022 frames ที่ 30fps และใช้ WAV ท่อน3.wav ฉบับเต็ม 3,235,200 sample frames @48kHz โดยไม่ตัด/ซ้ำ/ยืด/บีบ/กระโดดเสียง. ตอนประกอบตัดเสียงของ MP4 ย่อยทิ้งทั้งหมด แล้วใส่ original WAV เป็น audio track เดียว. ตรวจ EDL ให้ครบ [0,2022) ไม่มี hole/overlap; 3.1.mp4 ปัจจุบันยาว 72.433s จึงเลือก VIDEO เพียง 1290 เฟรมแรกและห้ามทับต้นฉบับ. 3.2 ต้องไม่ข้ามช่วง 43–52.94; ต้องมีภาพตามบทตลอดช่วง. QA ช็อตเสี่ยงที่ 30fps ทุกเฟรม (contact sheet 30 เฟรม/แผ่น), เช็กก่อน/หลังทุกคัต; re-QA ทุกเฟรมของช็อตหลังแก้. ห้ามเรนเดอร์คลิปใหม่ก่อนผู้ใช้ตรวจอนุมัติ. เอกสาร docs/part3_audio_continuity.md; EDL data/part3_frame_edl.json.
- **การแยกมอง/คุย/เดินแบบตัดจริง 3.2–3.3 (2026-11-11):** ต้องแยกไฟล์ iProject/iVideo ตาม ACTION จริง: คลิปมอง/ฟัง/คุยอยู่กับที่ให้การกระทำนั้นจบก่อน; ห้ามให้คนในคลิปเดียวมอง→หมุนตัวกลับ→เริ่มเดินเพราะ transition ไม่เนียน. เมื่อ action เดินเริ่ม ให้ขึ้นเลขคลิปใหม่โดย **เฟรมแรกของคลิปใหม่นั้นต้องเห็นตัวละครกำลังเดินอยู่แล้ว**, เดินต่อเนื่องตลอดคลิปจนจบ; ห้ามแทรก reaction ยืนมองกลับเข้ากลางคลิปเดิน. เปลี่ยนมุมกล้องระหว่างคลิปเดินได้โดยไม่เปลี่ยนเลข. การหมุน/เปลี่ยนทิศที่ทำไม่ได้สมูทต้องจัดให้อยู่นอกจอหรือแยก action ไม่สร้าง spinning/body teleport ในเทค. ล่าสุด 3.2=43.000–54.200s (ยืนมอง/ตอบสนอง), 3.3=54.200–59.133s (พ่อกับเมียน้อยเดินตั้งแต่ต้น). เสียงท่อน 3 WAV เดิม 67.40s **ไม่แบ่ง/ไม่ขาด/ไม่ซ้ำ**, master ใช้เสียงต้นฉบับครั้งเดียว. ห้ามเรนเดอร์คลิปใหม่ก่อนผู้ใช้ตรวจอนุมัติ. ตรวจจุดตัด global frame 1625→1626 @30fps. อ้างอิง data/part3_frame_edl.json.

## PART4_2_MERGE_AND_STATIC_COMFORT_20261111
- 4.1 + 4.2 is ONE continuous factory-working event in {SAVE}/4.1.iProject. Part4 local 0.0-30.3s, 35.3s iClone timeline including tail. 4.2 work is local 15.3-30.3s. DO NOT create duplicate 4.2.iProject or split merely at camera switches.
- Use the real สุนีย์ (red floral blouse, hair bun), not scene placeholder Sunee; keep placeholder hidden. Factory work: slow, small natural movement, no gratuitous turn/walk/drama.
- Latest user rule for 3.4 comfort: FAKE EMBRACE by camera composition; characters grouped and almost still, only very small head/breathing motion. NO exaggerated Hug Kid mocap, no required literal arm contact, no forced transitions, and NO Look At on 3.4. Existing 3.4 is NOT verified updated to this direction.
- Do not render 4.1/4.2 before user approval; contact-sheet QA is not a finished MP4. Story WAV must be continuous across 4.1+4.2 to 4.3.
- Live iClone 4.1 has two Cam41_A/B cameras, six switches, 28 props. Read-only QA checked 18 source frames during 15.3-30.2s: visible red-clad Sunee, mixing bowl and restrained work. See docs/part4_2_qa_20261111.md.
