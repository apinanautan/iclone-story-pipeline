# RLPy / iClone hard-won lessons (write every new technique here immediately)

กฎข้อที่ผู้ใช้ย้ำ 2026-11-11: **ทุกวิธี/แนวทางใหม่ที่ทำให้ทำงานเร็วขึ้นหรือเก่งขึ้น ต้องเขียนลง project ทันที**
เพื่อให้ AI รอบถัดไปเริ่มจากจุดที่ถูก ไม่ทำซ้ำข้อผิดพลาดเดิม.

## Part 7 checks (2026-11-12)
- RScene.Hide alone can leave IsVisible(T(0)) True. Also set avatar.SetVisible(T(0),False) and at tail, then verify IsVisible(time); Part7 Sunee verified False.
- Inspect existing hand world-z before lowering arms. Priya local avatar already has a still natural pose (hands z95.31/95.41cm); test rotations raised the hands, so restore zero arm Layer rotations and preserve the existing pose. No body-motion asset was loaded.
- Dense camera stills revealed foreground heads/shoulders at the edges of nominal singles; start/mid/end contact sheets catch this. A clean central face alone does not meet the single-person rule.

## 1. ห้ามอ้างอิงเวลา/โครงบทจากไฟล์เสียงผิดเรื่อง (สาเหตุงานเสียทั้งรอบ)
- `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\3.wav` (72.8s) = เสียงท่อน 3 ของเรื่องเก่า "มหาอกหัก" ตกค้างจาก 11/7
  **ห้ามใช้เป็นตัวอ้างอิง** ชื่อไฟล์ชนกับเสียงจริง.
- เสียงจริงดวงเมียน้อย ท่อน 3 = `{DESKTOP}\ดวงเมียน้อย_ดาต้าเสียง\เสียงที่ตัดแล้ว\ท่อน3.wav` (67.4s)
  + transcript `ถอดเสียง_8นาทีแรก.json` (ท่อน 3 = ต้นฉบับ 87.8–155.2 วินาที).
- **ก่อน trim/align เสียงใด ๆ ต้องยืนยัน duration ของไฟล์อ้างอิงก่อน** (ตรงกับ Project Sound จริงไหม).
- วิธีตรวจว่าเสียงในโปรเจกต์คือไฟล์ไหน: FFT cross-correlation (numpy) ระหว่าง audio ของพรีวิว/โปรเจกต์ กับ candidate wav
  → ไฟล์ที่ตรง = lag 0.00, score ~0.9999. (numpy ต้องรันผ่าน `py.exe -3` ไม่ใช่ code_exec python ที่ไม่มี numpy)

## 2. กล้อง "แว๊บ/ไถล" = transition ของ transform key (ไม่ใช่ต้องสร้างกล้องหลายตัว)
- iClone ใช้**กล้องตัวเดียวในฉาก + วางคีย์ตำแหน่งหลายช็อต** แล้วสลับด้วยค่า transition ของคีย์.
- ค่า default ของ key transition เป็นแบบ **linear/ease → กล้องค่อย ๆ ไถลจากช็อตหนึ่งไปอีกช็อต = "แว๊บ"** ที่ผู้ใช้เห็น.
- **วิธีแก้ที่ถูก:** ตั้ง transition ทุกคีย์กล้องเป็น `RLPy.ETransitionType_Step` (ค่า int = 1) ด้วย
  `ctrl.SetKeyTransition(kTime, RLPy.ETransitionType_Step, 0.0)` → ตัดทันที ไม่เกลี่ย.
- ตรวจด้วยการสุ่มตำแหน่งกล้องทุก 0.05 วินาที (GetValue + เทียบ tuple ตำแหน่ง): ตำแหน่งต้องเปลี่ยน**เฉพาะที่จุดตัด**เท่านั้น.
- Enum ที่มี: `ETransitionType_Linear`(=0) / `ETransitionType_Step`(=1) / Ease_In_*/Ease_Out_* ฯลฯ (dir(RLPy)).
- focal length (`GetFocalLength`) ก็ตัดทันทีที่จุดตัด ไม่ interpolate เมื่อตั้งคีย์ถูก.

## 3. RLPy API ที่สำรวจแล้ว (กันเสียเวลารอบหน้า)
- สร้างกล้องหลาย object ผ่านสคริปต์ **ไม่ได้** (`RICamera` เป็น abstract, `Clone()` คืน None) — ต้อง Create menu (GUI).
  แต่**ไม่จำเป็น**: ใช้กล้องตัวเดียว + switch/transition step ก็ได้ผลเท่ากล้องหลายตัว.
- มี `RLPy.RScene.AddSwitchCameraKey(kSetTime, spCamera)` / `ClearSwitchCameraKeys()` / `GetSwitchCameraFrameIndexs(fps)` —
  switch-camera ระบบจริงของ iClone.
- `RTransformControl` API จริง: `GetKeyCount`, `GetKeyTimeAt(kTick)`, `GetTransformKeyAt`, `ClearKeys`, `AddKey`,
  `RemoveKeyAt`, `MoveKey`, `GetKeyTransitionType/Strength`, `SetKeyTransition(kTick, eType, fStrength)`.
  **ไม่มี GetKey(i)** (ใช้ GetKeyTimeAt + GetValue(time) แทน).
- Viseme: `GetVisemeComponent().GetClipCount()/GetVisemeKeys()/AddVisemesClip(T, name, T(length))/RemoveVisemesClip(T)/AddVisemeKey(k)`;
  `RVisemeKey` = `SetTime/SetID/SetWeight(*100)`; อ่าน key: `kv[i].GetTime().ToFloat()/6000.0`.
- Face expression: `GetFaceComponent()`, `BeginKeyEditing()/AddExpressionKeys(T, [name], [weight], T(.32))/EndKeyEditing()`,
  `GetExpressionNames('Brows'|'EyeLid'|'MouthBase')`.
- หัว/มือ: `avatar.GetSkeletonComponent().GetSkinBones()` → bone ที่ `GetName().endswith('Head'|'Hand')`, `.WorldTransform().T()`.
- Audio: `RLPy.RAudio` มีแค่ `CreateAudioObject/LoadAudioToObject` (ไม่มี enumerate/remove บน avatar); ใช้ FFT correlation ตรวจแทน.
- Project end time: `RLPy.RGlobal.GetEndTime()/SetEndTime(T)`.
- Render preview: `SetRenderExportType(1)`, `GetRenderExportVideoParameter()` ตั้ง `MP4/854/480/fps"30"/bFinalRender/bExportAudio`,
  `RenderVideo(path)` (refuse overwrite). Render 480p ใช้ `ic8_render_preview480.py` (copy ของ ic8_render2).

## 4. ลำดับทำงานท่อน 3 (สถานะจริง 2026-11-11 ~03:10)
- โครงเหตุการณ์จากบทจริง+เสียงจริง: 3.1=0–43.0 (สนทนา; พ่อพูด 15.11–40.02), 3.2=43.0–56.5 (เดินหนี),
  3.3=56.5–63.0 (แม่กอดลูก), 3.4=63.0–จบ (เดินกลับ).
- กล้อง 3.1: 8 จุดตัด (7.05/16.05/26.35/28.9/31.4/36.6/38.3/40.4) ตั้ง transition=Step แล้ว; project end=43.0.
- ลิปซิงก์พ่อ: 15.09–40.09 (225 keys) ตรงคำจริง.
- reaction แม่ 28.9–31.4 (CU, ใช้ transform เดียวกับช็อต 45.0), เด็ก 36.6–38.3 (cam -4230,-3300,205 → look -4270,-3175,190, f=80).
- คลังโมชั่นสำหรับ 3.2–3.4: ดู docs/motion_catalog.md ท้ายหัวข้อ "คลังโมชั่นที่ค้นพบและจะใช้กับท่อน 3".
- สำรอง master: `{SAVE}\3_master_full_20261111.iProject`.

## 2026-11-17 — Avatar visibility API
RIAvatar.GetVisible() ไม่มีใน iClone 8 ที่ใช้; ใช้ vatar.IsVisible(T(0)) เพื่อเช็กสถานะ ณ เวลา 0. พบจากกล้องทั่วไปหยุดก่อนสร้างกล้อง; ปรับ scripts/ic8_cams.py แล้ว.


## 2026-11-17 — Light type capability
RIDirectionalLight ไม่มี SetRange(); ตรวจ hasattr(light, 'SetRange') ก่อนใช้ API point/spot. ถ้าไม่มีไฟที่รองรับ ให้ข้าม FaceLight และบันทึกคำเตือน ไม่ให้กล้องพาสหยุด.


## 2026-11-17 — Directional light color scale
RIDirectionalLight.SetColor ตั้งด้วยค่า RGB 255,236,214 แล้วขาวล้นในภาพ; ค่าที่ไม่ล้นสำหรับ Directional Light ฉากนี้คือ normalized RRgb(1.0,0.92,0.84). อย่านำไปแทนค่า point/spot FaceLight ซึ่งมีคู่มือเดิมแยกต่างหาก.


## 2026-11-20 — ภาพสำรวจกล้องแบบ read-only-ish และคืนตำแหน่ง
- สคริปต์กลาง scripts/ic8_scene_overview.py อ่าน ic8_jobs/scene_overview.json และสร้างภาพ RenderImage ตามมุมกล้องสำรวจ; ตั้ง survey_only=true, คงกล้องต้นฉบับ Cam_A และค่า Focal ที่เวลา 0 กลับใน finally.
- ผลจริง 4 ภาพกว้าง + 4 ภาพ 80/100mm, errors=0; Cam_A Transform key count ก่อนและหลัง = 8 เท่ากัน; iClone title ไม่ติด * หลัง job. ยังคงต้องตรวจภาพจริงก่อนอนุมัติ spot/cam.
- A1/A2 เห็นหน้า 3/4, แต่ B1/B2 เป็น profile ไม่ผ่าน. ห้ามใช้การผ่านของ script/การมีไฟล์ภาพแทนการตรวจคุณภาพภาพ.

## 2026-11-20 — Real still QA: explicit Linear camera transitions
- In ic8_cams.py, after c.SetValue(T(s),tr), call c.SetKeyTransition(T(s), RLPy.ETransitionType_Linear,0.0). Otherwise default ease differs from planned constant-speed trajectory by 3-6 cm and STILL_MISMATCH flags real nonlinearity. With Linear, all sampled errors were 0cm.
- Set project length AND End/PreviewEnd to WAV length+5s; camera view must be Qt ComboBox qtCameraSwitchAction currentText Switch at frame0. QA contact sheets 1/sec 3-8 per shot mechanical success is NOT content success (head cropped/work props missing/child missing).

## 2026-11-20 — Offline still QA: consistency is not framing quality
- Actual saved 54 stills / 7 shots: shift estimate 0.0% for every adjacent pair = image-consistency PASS, NOT cinematic/framing approval.
- Synthetic 120 px jump -> JUMP 6.3%; 250 px jump -> JUMP 10.1%; A-B-A -> FLIP. Steady frames PASS. No files and incorrect per-shot frame count -> FAIL exit 1.
- ic8_cams.py checks active camera ID and evaluated camera position before RenderImage and aborts at >3 cm; verifies PNG exists and is non-empty.
- ic8_part.py passes expected frame counts to still_check.py, which rejects missing shots, missing frame indices, unreadable PNGs and empty input.
- Image shift alone cannot distinguish camera error from actor/environment motion; inspect camera keys, image tiles and acting before diagnosis. This turn only exercised offline checks. New iClone capture loop not yet runtime-tested under the no-iClone-test rule. Persistent offline regressions: tests/test_still_check.py, 6 tests passing (steady, jump, flip, no frames, missing index, corrupt image).

## 2026-11-20 — Job source race and inspection workflow
- ic8_part.py job() must write input scripts into ic8_jobs/staging/ before ic8_gui.ps1 job; writing directly to watched run/ races watcher rename and PowerShell Get-Content. Verified after patch by importing trial avatar with shared cast step.
- ic8_cams.py supports no_dof:true for environmental/architectural insert without treating it as an additional establishing wide; this keeps camera check rules for people unchanged.
- review_per_sec:0 mid-only intentionally does not pass still_check.py filename validation; for mandatory final still QA restore review_per_sec:1 to capture 3-8/shot and contact sheet 3x3 per page.
- For child motions, verify child bone head positions at multiple times: LivingRoom_CleanOut&Chat_C moved along y >100cm so camera clipped the child; Yard_Watering_C kept head y stable and passed per-second framing, but no prop yet, hence not approved final.
