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
- เสียงจริงดวงเมียน้อย ท่อน 3 = `C:\Users\Apinan\Desktop\ดวงเมียน้อย_ดาต้าเสียง\เสียงที่ตัดแล้ว\ท่อน3.wav` (67.4s)
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
- สำรอง master: `E:\ไฟล์งาน\ไฟล์ Save\นิทาน\3_master_full_20261111.iProject`.
