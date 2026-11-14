# CURRENT STORY (one neutral file: OVERWRITE it when the story changes, never make a per-story copy)

**Story: รักลำเอียง (นิทาน 3D)** — started 2026-11-14. **User range: 0:00–08:21** (script start → สมหวัง "ไม่เป็นไรลูก" + narration "…อดเสียดายเงินล้านที่จ่ายออกไปไม่ได้"; user pasted 2026-11-14). Status: **audio cut 2026-11-14, nothing built in iClone yet.**

## Source (read-only, never write into G:)
- Folder: `G:\ไดรฟ์ของฉัน\รักลำเอียง (นิทาน 3D)\`
- Script: `บท - รักลำเอียง.docx` (7 blocks separated by "(AD.)")
- Audio: `รักลำเอียง _mixdown.wav` = 1529.68 s (25:29.7), 48 kHz stereo. Cut/transcribe **only in Tidmunz Studio** (whisper large-v3), not with own ffmpeg/whisper scripts.
- Characters: `รักลำเอียง\<n.name>\*.iAvatar`; scenes: `ฉาก\*.iProject`

## Cast
| role | file | note |
|---|---|---|
| สุดา (พี่สาว, ขาว สวย) | 1.สุดา\สุดา.iAvatar | |
| วารี (น้องสาว, ผิวเข้มกว่า) | 2.วารี\วารี.iAvatar | |
| นายสมหวัง (พ่อ) | 3.นายสมหวัง\นายสมหวัง.iAvatar | |
| นางวิไล (แม่) | 3.1.นางจีไล\นางจีไล.iAvatar | folder/file spelled "จีไล"; script says วิไล — confirm it is the same person |
| ชาวบ้าน | 4.ชาวบ้าน01\ชาวบ้าน (ตัวแทนคนแรก).iAvatar | |
| พิชัย (สามีสุดา) | 5.พิชัย\พิชัย.iAvatar | |
| มานพ (สามีวารี) | 6.มานพ\มานพ.iAvatar | |
| ลูกชายสุดา 7 ขวบ | 7.ลูกชาย7ขวบ\ลูกชายสุดาและพิชัย — 7 ขวบ.iAvatar | |
| ลูกชายทารก | 7.ลูกชายทารก\ | **folder empty on 2026-11-14** |

## Scenes (`ฉาก\`)
หมู่บ้าน (2.5 GB) · บ้านนายสมหวัง · ภายในบ้าน · ออฟฟิศที่ทำงานในบริษัท · โรงพยาบาล · งานเลี้ยงเปิดกิจการ (3.2 GB) · ร้านอาหาร · บ้านพิชัยที่กรุงเทพ(ภายใน)

## Script blocks → likely scene (to confirm against audio times after transcription)
1. ชาวบ้านชมสุดา, วารีนั่งฟังเฉย ๆ — หมู่บ้าน/บ้านนายสมหวัง. Speakers: ชาวบ้าน, สมหวัง.
2. สุดาทำงานกรุงเทพ พาแฟนมาแนะนำ; พ่อกระซิบเรื่องแบ่งเงินขายที่ — ออฟฟิศ → บ้านนายสมหวัง. Speakers: สมหวัง, สุดา.
3. งานแต่งสุดา/วารี; พ่อป่วยเข้า รพ.เอกชน; รังนก — โรงพยาบาล, ร้านอาหาร. Speakers: สุดา, สมหวัง, วิไล.
4. สุดามีลูก ขอเงินลงทุน งานเลี้ยงเปิดกิจการ; วารีแท้ง พ่อแม่ไม่ไปเฝ้า; มานพปลอบ — งานเลี้ยง, ร้านอาหาร, โรงพยาบาล. Speakers: วิไล, มานพ, วารี.
5. วารีลาออกย้ายตามมานพ; ทะเลาะ; สุดาปฏิเสธรับพ่อแม่ (โทรศัพท์) — บ้านนายสมหวัง, บ้านพิชัย. Speakers: วารี, วิไล, มานพ, สมหวัง, สุดา.
6. แม่ป่วย รพ.รัฐ; เงิน/ทองหมด; สุดาตัดสาย; สองตายายร้องไห้ — โรงพยาบาล, บ้านพิชัย. Speakers: วิไล, สมหวัง, สุดา.
7. วารีกลับมาดูแล จ่ายค่ารักษา; ยกที่ดินผืนสุดท้ายให้วารี; สุดาอาละวาด — โรงพยาบาล, บ้านนายสมหวัง. Narration only.

## Open questions for the user
1. Which minutes of the 25:29 audio are yours?
2. Save folder/file names — `E:\ไฟล์งาน\ไฟล์ Save\นิทาน\` already holds ดวงเมียน้อย 1–9 (`1.iProject`…); a new story must not overwrite them (suggest sub-folder `รักลำเอียง\`).

## Audio parts (cut by Claude with ffmpeg + whisper large-v3, one-time user OK 2026-11-14)
Folder: C:\Users\Apinan\Desktop\รักลำเอียง\เสียงที่ตัดแล้ว\ท่อนN.wav (+ transcript json). Cut at real pauses; times = source-file seconds.
| ท่อน | src start-end | len | content |
|---|---|---|---|
| 1 | 0-36.8 | 36.8 | narration: sisters compared |
| 2 | 36.8-99.1 | 62.3 | villager praises Suda, สมหวัง replies, Wari listens |
| 3 | 99.1-139.9 | 40.8 | Suda's boyfriend introduced, father whispers, Suda replies |
| 4 | 139.9-188.0 | 48.1 | father compares Wari's boyfriend |
| 5 | 188.0-255.8 | 67.8 | Suda asks about money, father splits land money, Suda displeased |
| 6 | 255.8-285.7 | 29.9 | Suda's wedding, gifts from parents |
| 7 | 285.7-347.0 | 61.3 | Suda disappointed in in-laws, urges husband to split off |
| 8 | 347.0-383.0 | 36.0 | Wari marries Manop, small house |
| 9 | 383.0-447.8 | 64.8 | gold bought, father ill, Suda pushes private hospital, Wari nurses |
| 10 | 447.8-501.0 | 53.2 | Suda's กงสี excuse, father "ไม่เป็นไรลูก" |
Whisper text is rough (use the docx for wording). Lip-sync windows still to be measured per part.

## Progress
- ท่อน1: DONE (saved, no render). `E:\ไฟล์งาน\ไฟล์ Save\นิทาน\รักลำเอียง\ท่อน1.iProject`, scene ภายในบ้าน, สุดา+วารี, Cam_A/Cam_B 4 shots (0/10/20/31 s), end 41.8 s, audio on Project Sound at 0 (verified by RenderAudio: sound 0.25-36.3 s).
- ท่อน1: rendered `E:\Video\รักลำเอียง\1.mp4` (1080p60, 41.82 s). User has not yet reviewed it.
- ท่อน2: `E:\ไฟล์งาน\ไฟล์ Save\นิทาน\รักลำเอียง\ท่อน2_v2.iProject` (GUI-saved, reopen test OK). Scene บ้านนายสมหวัง, 5 avatars (ชาวบ้าน/สมหวัง/จีไล/สุดา/วารี) standing in a row at x3120-3480,y4300 facing +y, Cam_A/Cam_B 6 shots (0/9/21/29/36/52 s), end 67.3 s, ท่อน2.wav imported (not verified by RenderAudio: it hung iClone). NOT rendered. `ท่อน2.iProject` and `ท่อน2_เสีย_เปิดไม่ได้.iProject` are script-saved and fail to open; `_test_*.iProject` are junk — delete only if user agrees.
- Next: ท่อน3 in a NEW chat (rule: 2 clips per chat). Scene ฉาก for ท่อน3 = ? (father whispers, Suda's boyfriend) — pick in iClone. Save ONLY via File > Save Project As (never RFileIO.SaveProject).
