# Part 4 (ดวงเมียน้อย) — event plan  (2026-11-11)

Source audio (already cut by user via Tidmunz): `Desktop\ดวงเมียน้อย_ดาต้าเสียง\เสียงที่ตัดแล้ว\ท่อน4.wav`
= master 155.2–208.6 s (53.4 s). Scene: `G:\ไดรฟ์ของฉัน\ดวงเมียน้อย\ฉาก\โรงงานทำขนมของฝาก (ใน).iProject`.
Cast per แผน_8นาทีแรก.md: สุนีย์, เถ้าแก่โรงงานขนม (extra). Kids (นาวี, นิวัตน์) appear only in narration/optional cutaway.
(Old `part4_plan.md` is the previous story "มหาอกหัก" — ignore.)

Local time = master time − 155.2. Transcript segment edges are NOT verified pauses.

| event | local sec | main action | narration |
|---|---|---|---|
| 4.1 | 0 – ~15.3 | Sunee, no husband now, goes to work: arrives / applies at the sweet factory | จากที่เคยมีสามีคอยเลี้ยงดู … สมัครเป็นคนงานที่โรงงานทำขนมหวาน … ของดีประจำจังหวัด |
| 4.2 | ~15.3 – ~30.3 | Sunee works: shaping the filling, factory line, overtime | ร้านสาขาหลายแห่ง … ปั้นไส้ขนม และทำงานล่วงเวลา |
| 4.3 | ~30.3 – 53.4 | Sunee tired/thinking about money for two kids; costs rise at secondary; she resolves "ส่งได้แค่มัธยมต้น" | เพื่อให้มีเงินพอสำหรับลูก … ค่าใช้จ่ายเริ่มมากขึ้น … แม่ส่งลูกได้แค่มัธยมต้นนะนารี |

Boundaries only change when the MAIN action changes (arrive/apply → work → worry). Cameras stay inside each event.
Line "แม่ส่งลูกได้แค่มัธยมต้นนะนารี" (~52–53 s) is Sunee speaking → needs lip-sync via Create Script > Audio File on Sunee, trimmed to that window.

## Next steps
1. Open the factory scene, list avatars/props/cameras (read-only).
2. Check which cast exist (Sunee, boss) and the 3.5 final pose/position continuity.
3. Build 4.1 only → inspect as video → save `4.1.iProject` → wait for user before render.

## 4.1+4.2 BUILT (2026-11-11) — E:\ไฟล์งาน\ไฟล์ Save\นิทาน\4.1.iProject (saved 18:02:54, 1.565 GB)
- Merged 4.1+4.2 = local 0–30.3 s + 5 s tail = 35.3 s. Scene from Downloads copy of โรงงานทำขนมของฝาก (ใน).iProject. Sunee only.
- Motion: Drill Floor (local copy Drill_Floor_local.rlMotion) one clip speed 0.449, max root drift 15.8 cm. Audio ท่อน4.wav on Project Sound at frame 0.
- Cameras Cam41_A / Cam41_B alternate via Switcher, 6 shots: 0–6 A MCU 3/4 80mm; 6–11.5 B hands CU side 100mm; 11.5–17.5 A face CU 100mm; 17.5–23.5 B profile MCU 80mm; 23.5–29 A MCU other 3/4 80mm; 29–35.3 B front MCU pull-out 80mm. DOF keys, keys every 0.25 s. Viewport = Switcher.
- Not done: mouth/visemes (narration only), face light (scene key lights give readable faces), render (waiting for user), 4.3.
