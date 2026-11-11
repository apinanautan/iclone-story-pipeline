# Part 3 — Original Audio Continuity and Dense Frame QA
Mandatory production contract, 2026-11-11.

## Source-of-truth
Original full Part 3 WAV:
C:\Users\Apinan\Desktop\ดวงเมียน้อย_ดาต้าเสียง\เสียงที่ตัดแล้ว\ท่อน3.wav
48,000 Hz stereo, 3,235,200 sample frames, exactly 67.40 seconds.
Master must have 30fps × 67.4 sec = exactly 2,022 visual frames.

3.1, 3.2, 3.3, 3.4 are VISUAL EVENT clips. Do not trim narrative content, repeat words, speed up, change pitch, restart or crossfade independently encoded audio. Finished Part 3 plays full original audio from first sample through last without gaps. Final master audio: one unmodified ORIGINAL Part 3 WAV source; do not use event MP4 audio streams.

Avatar lip-sync: import FULL original audio through Create Script > Audio File then trim avatar speaking windows in iClone against GLOBAL source timestamps; no pre-cut WAV lip shortcuts.

## Verified severe defects
Existing E:\Video\3.1.mp4 intended visual 0–43s but contains 2,173 video frames (72.433333s), not 1,290 frames. Keep the existing file untouched; use ONLY its first 1,290 video frames when assembling master.
The interim 3.2 work was re-scoped to 52.94–59.13, which DROPS 43.00–52.94. Prohibited. For current draft mapping, rebuild 3.2 visuals to cover 43.00–59.133 including meaningful response, acting and movement before the actual walk-away starts near 52.94. No 10-second static reaction, and no missing narration.

## Video frame EDL — draft until 3.2 visual approval
Half-open intervals, 30fps, no overlap/no gap:
3.1 [0,1290): 0.000–43.000
3.2 [1290,1774): 43.000–59.133 — must cover mother accepts + departure, with main walk-away near 52.94
3.3 [1774,1910): 59.133–63.667 — mother/children comfort
3.4 [1910,2022): 63.667–67.400 — mother leads children home

A change to editorial boundaries requires re-validation of complete frame coverage [0,2022). Frame-snapping is necessary for 30fps. Never split WAV to match event boundaries.

## Dense visual storyboard QA, NOT only 3 stills per shot
- For motion/turns/walking/contact/OTS/eyeline, review EVERY 30fps source frame in consecutive chronological contact sheets. 30 frames per contact sheet = 1 second. The intermediate frames are not skipped.
- For standing dialogue also check dialogue/face beat changes, and at minimum every camera switch; when failure is recurrent, review every frame for whole event.
- Check BOTH sides of each cut, frames N-1 and N. Check subject face obstruction, gaze, first step/root motion/foot sliding, wardrobe foreground, sudden jumps, hands/contact, composition and screen direction.
- Frame audit is not a substitute for continuous playback; also watch moving performance in iClone.
- After a fix, RE-RUN all frames in the affected shot, not only one corrected still. Report defects and fixes with exact frame/time.
- The user need not open or approve a storyboard document. It is internal QA evidence for the operator.
- Do not render next event without explicit event-specific approval. User permission for 3.1 does not authorize render of 3.2.

## Final assembly
1. Validate the original source WAV exactly 3,235,200 samples / 67.4s.
2. Each event video must cover a declared half-open frame range; its source-frame offset must be explicitly verified.
3. Strip/ignore every event clip audio stream. Select only corresponding VIDEO frames and concatenate to 2,022 total.
4. Add one entire original WAV as master audio (one AAC stream, sample rate 48k). No fades, no speed/time changes.
5. Reject missing visual clips, unknown source offset, unapproved events, overlaps, holes, or wrong video count/duration.
6. Verify final count/duration and audio timeline at exact joins. Do not claim ready based on filenames.
Canonical frame plan: data/part3_frame_edl.json.
Validator/assembler: scripts/part3_continuity_guard.py.
Full-frame capture job: scripts/ic8_dense_frame_review.py.
- **การแยกมอง/คุย/เดินแบบตัดจริง 3.2–3.3 (2026-11-11):** ต้องแยกไฟล์ iProject/iVideo ตาม ACTION จริง: คลิปมอง/ฟัง/คุยอยู่กับที่ให้การกระทำนั้นจบก่อน; ห้ามให้คนในคลิปเดียวมอง→หมุนตัวกลับ→เริ่มเดินเพราะ transition ไม่เนียน. เมื่อ action เดินเริ่ม ให้ขึ้นเลขคลิปใหม่โดย **เฟรมแรกของคลิปใหม่นั้นต้องเห็นตัวละครกำลังเดินอยู่แล้ว**, เดินต่อเนื่องตลอดคลิปจนจบ; ห้ามแทรก reaction ยืนมองกลับเข้ากลางคลิปเดิน. เปลี่ยนมุมกล้องระหว่างคลิปเดินได้โดยไม่เปลี่ยนเลข. การหมุน/เปลี่ยนทิศที่ทำไม่ได้สมูทต้องจัดให้อยู่นอกจอหรือแยก action ไม่สร้าง spinning/body teleport ในเทค. ล่าสุด 3.2=43.000–54.200s (ยืนมอง/ตอบสนอง), 3.3=54.200–59.133s (พ่อกับเมียน้อยเดินตั้งแต่ต้น). เสียงท่อน 3 WAV เดิม 67.40s **ไม่แบ่ง/ไม่ขาด/ไม่ซ้ำ**, master ใช้เสียงต้นฉบับครั้งเดียว. ห้ามเรนเดอร์คลิปใหม่ก่อนผู้ใช้ตรวจอนุมัติ. ตรวจจุดตัด global frame 1625→1626 @30fps. อ้างอิง data/part3_frame_edl.json.
