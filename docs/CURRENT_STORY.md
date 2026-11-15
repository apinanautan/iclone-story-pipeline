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
- ท่อน2 v3 (2026-11-14, user: "script says sit; first villager is a WOMAN"): `ท่อน2_v3.iProject` (GUI Save As 20:06, 2.04 GB). Male villager avatar removed; speaker = `ชาวบ้านหญิง` (= nangyoi.iAvatar from `G:\ไดรฟ์ของฉัน\สระน้ำศักดิ์สิทธิ์\...\1.ชาวบ้าน หลายคน หลายวัย\`, story folder has no female villager). Family sits on 4 Chair_Wood (Reallusion template) in a row x≈3438, y 4130/4280/4430/4600, backs to the porch, facing -x; villager stands at (3020,4330) facing +x. Motions = MographMotion SitC01B_L_Happy / SitC01A_T_Happy01 (สมหวัง talks 13.3-21.2) / SitC01B (วารี) / StandTKI_T_Happy01 → StandTKI_Happy (villager). Smile keys via scripts/ic8_smile.py (สุดา .75, จีไล .6, สมหวัง .45). Lip: villager 0.3-8.4, สมหวัง 13.5-20.8. 8 shots Cam_A/Cam_B, viewport = Switch.
- ท่อน2 DONE: motions slowed to 0.15-0.30 (user OK on preview), GUI-saved over ท่อน2_v3 20:37, rendered `E:\Video\รักลำเอียง\2.mp4` (1080p60, 67.33 s, Switch, audio OK) 21:25. ท่อน1.mp4 is still single-camera + old fast motion → needs re-render/rework if the user asks.
- Next: ท่อน3 in a NEW chat (rule: 2 clips per chat). Scene ฉาก for ท่อน3 = ? (father whispers, Suda's boyfriend) — pick in iClone. Save ONLY via File > Save Project As (never RFileIO.SaveProject).
- ท่อน3 (2026-11-15), split by scene:
  - **ท่อน3.1** `ท่อน3.1.iProject` (GUI Save As 01:46): scene ออฟฟิศที่ทำงานในบริษัท, 0–12.6 s (narration "สุดาทำงานบริษัท…พาแฟนมา"). สุดา sits at desk (528,-358,z+17 so hands reach the keyboard) with Office_Desk_Computer_Idle (Mocap Online LIFE Office Desk, copied local) speed .30; พิชัย stands at (612,-430) arms crossed Stand03_L_Agree01 .15 + Look front.iTalk + Look At สุดา head + smile. Cam_A Suda+Pichai 0–6.6, Cam_B Pichai 6.6–12.6, Switch. Preview 21.6 px/s.
  - **ท่อน3.2** `ท่อน3.2.iProject` (recovered after iClone closed, GUI Save As 01:28): บ้านนายสมหวัง, uses 12.6–45.8 s. จีไล/สมหวัง/สุดา/พิชัย on chairs; lip สมหวัง 20.5–28.6, สุดา 33.25–38.0; 7 shots (first two = 0–12.6, superseded by 3.1). Preview 40 px/s. ท่อน3.wav not yet on Project Sound in either project (previews muxed with ffmpeg).
  - DONE 2026-11-15: user approved; rendered `E:\Video\รักลำเอียง\3.mp4` (1080p60, 45.8 s) = 3.1 render 0–12.6 + 3.2 render 12.6–45.8 joined with ffmpeg + ท่อน3.wav. ท่อน3.2 reopen OK. Not done: ท่อน3.1 reopen test; ท่อน3.wav not on Project Sound in the .iProject files.
- Next: ท่อน4 in a NEW chat (2 clips per chat).
- ท่อน4 (2026-11-15), split by scene; both projects use the full ท่อน4.wav timeline (Sound row = ท่อน4 at frame 0):
  - **ท่อน4.1** `ท่อน4.1.iProject` (03:49): บ้านนายสมหวัง, 0–17.4 s, father talks (SitC01A_T_Explain01 .22, lip 0.8–16.45), others listen; new angles (dirty single father, Suda close from far side, high father, low Pichai). User OK.
  - **ท่อน4.2** `ท่อน4.2.iProject` (03:55): office, uses 17.4–47.5 s (+tail to 52.6): วารี at the desk (528,-358,z+17), Office_Desk_Computer_L_Idle → Computer_Idle .30, Look front + smile .5; 4 shots 17.4/25/33.9/41.6 (Cam_A 0–17.4 = wide filler, not used). Side/back contact OK. User OK.
  - Final 4.mp4 = 4.1 render 0–17.4 + 4.2 render 17.4–48.1, muxed with ท่อน4.wav.
  - DONE 2026-11-15: 4.1 recut so every shot shows the speaking father (shot 1 tightened to 100 mm: no cut-off mother). Rendered E:\Video\รักลำเอียง\4.mp4 (1080p60, 52.6 s, audio OK).
- Next: ท่อน5 in a NEW chat (this chat did ท่อน3 + ท่อน4).
- **ท่อน5** `ท่อน5.iProject` (2026-11-15 06:4x, GUI): built from ท่อน4.1 (house, 4 seated). 0–3.7 สุดา "พ่อก็อย่าเอาเงินไปช่วยวารีหมด จนลืมหนูล่ะ" (lip), 6.7–20.6 สมหวัง splits land money (lip), 21.8–67.8 narration: สุดา displeased (sour face keys from 21–23.5, SitC01B_L_disagree01), แม่ SitC01B_L_Sad. 8 shots (speaker on screen while talking; narration = Suda close/Pichai/father). Sound = ท่อน5 at frame 0. Waiting for user Play check. Last ~5 s (67.9–) is "ไม่นานนัก สุดาก็แต่งงาน…" = start of ท่อน6 wedding narration, still in the house.
- **ท่อน6** `ท่อน6.iProject` (GUI, 10:46): งานเลี้ยงเปิดกิจการ; บ่าวสาวยืนซบไหล่มองกล้อง, พ่อแม่วารีนั่งโต๊ะ, พานทอง/พานเงินบนโต๊ะเปล่า z=76; 5 ช็อต; ไฟ fill ตามกล้อง. ยังไม่เรนเดอร์ (รอผู้ใช้ Play).
- **ท่อน7** `ท่อน7.iProject` (GUI, 11:38): ฉากบ้านพิชัย (โซฟา) สุดา+พิชัย นั่งขอบโซฟา; 6 ช็อต (กล้อง 2 คีย์ ทิศเดียว 15–20 cm); เสียง ท่อน7 อยู่แถว Sound; viewport=Switch. ยังไม่เรนเดอร์.
- **ท่อน7 DONE 2026-11-15:** user approved; rendered `E:\Video\รักลำเอียง\7.mp4` (1080p60, 61.3 s, mean -21.3 dB). ท่อน7 = camera reference (7 shots, alternate cams, 2-key single-axis moves). ท่อน6 still not rendered (saved, waiting Play). Next: ท่อน8-10; ท่อน6 render.
- (2026-11-15) ท่อน8.2 (village exterior, 24.8-36 s, 2 cameras) was built but iClone crashed before saving; rebuild from scratch/p82 job h8_k.py if needed.

- **ท่อน9 INCOMPLETE / failure report (2026-11-15):** มี checkpoint `E:\ไฟล์งาน\ไฟล์ Save\นิทาน\รักลำเอียง\ท่อน9.iProject` เวลา 15:19. Project Sound ท่อน9 ตรวจด้วย RenderAudio แล้วว่า 64.8s/48kHz/stereo/ไม่เงียบ; live scene มี สมหวัง+วารี+สุดา+นางจีไล และมี stage/motion/expression เบื้องต้น. กล้อง 4 บทบาท/8 switch shots ถูกสร้างใน memory แต่ contact sheet ใช้ไม่ได้ (ติดผนัง/มืด/จับเป้าผิด) และ live project ยังมี `*` ไม่ได้ Save หลังแก้. ห้ามเรียกว่าเสร็จหรือ render. อ่าน `docs/part9_codex_failure_report_20261115.md` ก่อนทำต่อ.
- ท่อน9 (cont., 2026-11-15): must continue from `วีดีโอ\เว่น\1 เงินทองเป็นของนอกกายนะพ่อ.mp4` (see rules). Live fixes (NOT saved yet): room = x -712..-69, y 465..1005 (old cams were outside it). P9_Family cam at (-600,600,170)→(-585,612) 35mm. Father: SitG03 (CC MixMove_Male) .25, root (-230,1005,70) yaw -90 = sitting up on bed facing its foot. Wari root (-175,672) yaw 180. Scripts: ic8_rak_part9_cam_test.py (p9cam.json), ic8_rak_part9_father_bed.py (p9father.json), ic8_rak_part9_shift.py (p9shift.json). Next: other 3 cameras, ending shot of Wari alone by the trolley, GUI Save As.
- ท่อน9 cams v2 (not saved): Suda yaw 137, mother yaw 120 (face father). P9_Father (-330,880,148)→head, P9_Suda (-305,720,158), P9_Wari (-265,830,160); switch 0/7/14/20/30/38/44/55 = Family/Father/Family/Suda/Family/Suda/Wari/Family. Contact sheet OK (all faces visible). Open issues: father's arms sink into mattress, Family shot repeats 4×, no Wari-alone ending yet.
- ท่อน9 v3 (not saved): father root z 82 (arms on mattress). New cam P9_High (-680,490,265)→(-230,830,90) 24mm = high corner like the เว่น clip. Visibility: Suda off at 44 s, mother off at 55 s → ending 55–64.8 P9_High = Wari alone by the trolley with father. Switch 0 Family/7 Father/14 High/20 Suda/30 Family/38 Suda/44 Wari/55 High. Contact sheet OK. Next: user Save As ท่อน9_working + Play check; no render yet.
- ท่อน9 v3 GUI-saved over ท่อน9.iProject 16:19 (893 MB). Waiting for user Play check; not rendered.
- ท่อน9 father v4 (live, NOT saved): SitG03 looked like a statue (head back, eyes shut 0.92 from stage script). Now MographMotion 01_Male SitC01B_L_Sad .25 sitting on the bed's family side, root (-200,880,25) yaw 0, face keys re-done with eyes open. P9_Father cam (-262,712,142)→(-202,850,130). Bed side rail sits in front of his chest.
- ท่อน9 v5 (live, NOT saved): father = MographMotion 01_Male SitC01B .25, root (-118,915,25) yaw -90: sits upright with back to headboard/wall like teacher clip (legs hidden in mattress). P9_Father (-320,905,150)→(-110,916,140) 80mm MCU. P9_Family over mother's shoulder (-440,690,168)→(-150,880,138) 40mm. Switch 0 Family/7 Father/14 Family/20 Suda/30 Father/38 Suda/44 Wari/55 High.
- ท่อน9 father v6 (live, NOT saved): user rejected v5 (body/legs sink into mattress, position not like teacher clip). Tried SitG03+pitch (-14° tilt back, root (-196,1005,80)) = knees touch top but shins still go into mattress; SitG01 = zombie; Lie_on_Bed = 3 s clip with big offset into wall. No legs-straight long-sit motion found. Best path: copy father pose from G:\...\รักลำเอียง (นิทาน 3D)\01.iProject (likely the teacher clip project) — needs user OK to open it.
- Lesson: always render a SIDE view at mattress height before calling a bed pose done.
- ท่อน9 v7 (live, NOT saved): user: "no need to match exactly, just sit on the bed and use camera angles". Father = SitC01B .25 root (-118,915,25) yaw -90 (upright at bed head, back to wall). No wide/high shots. Switch 0 Family(OTS mother 50mm)/7 Father(80mm MCU)/14 Family/20 Suda/30 Father/38 Suda/44 Wari/55 Father. Contact sheet OK.
- ท่อน9 v8 (live, NOT saved): father back at (-118,915,25) yaw -90. P9_Father 95mm target z150, P9_Family 135mm OTS target (-130,900,150): no mattress visible in any shot (checked 0.5/10.5/17/34/64 s). Switch unchanged (0 Fam/7 Fa/14 Fam/20 Suda/30 Fa/38 Suda/44 Wari/55 Fa).
- ท่อน9 v8 GUI-saved over ท่อน9.iProject 16:39:53 (893.8 MB). Reopen test not done. Not rendered. Note: a big save takes ~30 s to land on disk; re-check mtime before saying the save failed.
- ท่อน9 sound: ท่อน9.wav imported via Ctrl+I at frame 0, Ctrl+S 16:43:44, file +12.4 MB (=wav). Sound row not seen on screen (timeline off-screen). Rule breaks found after reading rules.md: per-part scripts ic8_rak_part9_*.py, duplicate P9_* cameras, SitC01B arms-crossed clips, no Look front/Look At on listeners, viewport left on a camera (not Switch) when saved, play range unchecked, cameras = one push over whole timeline instead of 2 keys per shot, no reopen test.
- **ท่อน9 FIXED + saved 2026-11-15 16:50:29 (938.7 MB), reopen OK 16:52:** Sound row = ท่อน9 (100%) at frame 0 (seen on screen). Father SitC04B_L_Agree01 → Agree02 at .20 (covers 0–77 s), root (-118,915,25) yaw -90, back to wall. Wari/mother/Suda: Look front + Look At father. Only Cam_A/Cam_B: 8 shots 0/7/14/20/30/38/44/55 (OTS mother→father 135mm, father 95, Wari 45, Suda 45, father 85, Suda 60, Wari 55, father 85), 2 keys/shot ±12–15 cm; stills start/mid/end checked (faces, no mattress). Viewport = Switch at frame 0. Not rendered. Per-part scripts ic8_rak_part9_*.py → Recycle Bin; use ic8_pose_place.py / ic8_cams.py.
- **ท่อน9 DONE 2026-11-15 17:09:** user approved; rendered E:\Video\รักลำเอียง\9.mp4 (1920x1080 60fps, 64.82 s, ท่อน9.wav muxed, mean -21.1 dB), one frame per shot checked (8 shots, different cams). 9_raw → Recycle Bin.
- **Popup guard (2026-11-15 17:16):** scripts/ic8_startup_popup_guard.ps1 rewritten (Win32 EnumWindows + UIA, always on, logon task "iClone Startup Popup Guard" restarted). Closes: offline OK, signup No thanks, plugin-not-compatible OK, FBX Import Settings → Convert All (tested OK 17:15), render Reminder → Discard. NOT auto: "Unsaved project data found" (may need restore). Log %LOCALAPPDATA%\iCloneStartupGuard\guard.log.
- **DONE 2026-11-15 (was TODO):** iCloneStoryBridge plugin = watcher auto-loader (do NOT delete). Its "not compatible" popup goes away by adding `rl_plugin_info = { "ap": "iClone", "ap_version": "8.0" }` to Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\iCloneStoryBridge\main.py (needs admin/UAC; backup of original in scratch). Not done yet.
- ท่อน9 project renamed to ท่อน9.iProject (final). ท่อน10.iProject = Save As from ท่อน9 17:18.
- **ท่อน10 (2026-11-15 17:25, GUI-saved, reopen OK):** `ท่อน10.iProject` = Save As from ท่อน9 (hospital). Sound = ท่อน10 (100%) at frame 0, length 53.2. Suda (-300,700) yaw 140 StandTKI_T_Explain01 .25 + Look At father, visible all through (ท่อน9 hide keys cancelled). Lip: AccuLips via GUI Create Script > Audio File (full ท่อน10.wav) for สุดา + นายสมหวัง, trimmed: Suda 0.53–19.18 (151 keys), father "ไม่เป็นไรลูก" 35.47–36.37 (9 keys; time from silencedetect, check by ear). 6 shots Cam_A/B: 0 two-shot Suda+mother / 9 Suda close / 19.6 father / 32 OTS mother→father (his line) / 40 two-shot / 49 father close. Viewport Switch. Waiting for user Play. Note: Create Script also puts the wav on each speaker's voice track, so Play in iClone may sound doubled; the final mp4 is muxed with the clean wav.
- ท่อน10 fix (user: Suda+mother too far apart, empty middle): Suda moved to (-342,733) next to mother; two-shot target (-364,754,152) from (-175,870,165); Suda close 75mm push-in (no mother sliver, head not cut). GUI-saved 17:32:05, reopen OK, Switch at 0. Waiting for Play.
- **ท่อน10 DONE 2026-11-15 17:46:** E:\Video\รักลำเอียง\10.mp4 (1080p60, 53.2 s, ท่อน10.wav muxed, -21.3 dB, 6 shots checked). 1–10.mp4 (8 = 8.mp4) copied to G:\...\วีดีโอ\บีม. Next chat: ท่อน11+ (2 parts per chat rule). Paused TODO: StoryBridge plugin compat fix (admin).
- Plugin fix applied 2026-11-15 with scripts/fix_ic8_plugin_compat.ps1 (UAC): rl_plugin_info added, backup main.py.bak. Not yet verified on an iClone restart.
- Restart test 2026-11-15 18:11–18:13: NO plugin-compat popup (fix works), watcher STARTED 18:12:07, guard auto-closed offline (OK) + signup (fixed match: button text 'Sign me up'). iClone left on DefProject, clean.
