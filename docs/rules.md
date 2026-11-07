# User's rules (add every new instruction here immediately)

## Working style
- Do one step at a time as the user says. Don't render until told to.
- Every instruction the user gives → write it here right away.
- Script everything you can (watcher). Avoid screenshots/mouse; they waste credits.
- **Save often** to `E:\FileSave\N.iProject` after each big step (iClone can crash).
- Ask before overwriting a file that already exists from another story. (User OK'd overwriting the old 1.iProject, 1.mp4, 2.iProject from 31/10 for มหาอกหัก.)
- After an iClone crash, on restart choose **OK** to restore unsaved data, then save it as `E:\FileSave\N.iProject`.

## Files
- Project: `E:\FileSave\N.iProject` only (N = audio number). Video: `E:\Video\N.mp4` only.
- Open scenes from `<story>\ฉาก\`; never save into the G: story folder.

## Audio & timeline
- **First step of every part:** import `N.mp3` into the Project **Sound** track (File > Import) and make the Sound row
  visible (Project row ⌄ → tick Sound). Never hide the audio on another object.
- Extend the timeline to audio + **5 s tail (≈300 frames)**: `RGlobal.SetProjectLength(T)` **and** `SetEndTime(T)`
  (SetEndTime alone doesn't extend it). Check End Frames in the Project panel = seconds × 60.
- Motions and cameras also run through the tail, so the edit has slack.

## Motion
- Prefer ONE clip slowed so it spans the whole length (speed = clip_len / total). If that needs < ~0.5,
  use ~0.5 and chain 2–3 copies (by context). Don't loop at speed 1.
- Standing still: body `Stand00.iMotion` + face `Digital Soul 100+\1.Watch\Look front.iTalk` (looks ahead, head moves a little).
- **Sitting: AccuPOSE pose** (see accupose_presets.md). Order: clear ALL animation → frame 0 → apply pose (panel only,
  never by script; that crashed iClone) → then add face clip / blink / lip sync.
- No busy motion; small head movement from the face clip is enough. Speakers move their mouths on their lines
  (cut that line from the audio, `RAudio.LoadAudioToObject(avatar, wav, start)`).
- Every character: auto blink `GetFaceComponent().SetAutoBlinkName('Normal')`.

## Workflow ใหม่: นำเข้าเสียงเต็มให้ตัวละคร แล้วตัดช่วงที่ไม่พูดใน iClone
- **ห้ามนำ WAV ที่ตัดภายนอกมาใส่ตัวละครเพื่อทำปากพูด** ให้เลือก Avatar ผู้พูดทีละคน นำเข้า **N.mp3 ฉบับเต็ม** จากต้นฉบับด้วยเครื่องมือ Voice/AccuLips ของ iClone เพื่อสร้าง Voice + Viseme ก่อน
- วิเคราะห์ว่าใครพูดเวลาใด แล้วใช้ **เครื่องมือตัด/Split/Trim ใน Timeline iClone** ตัด/ลบช่วงที่ Avatar นั้น **ไม่ได้พูด** ออกให้เหลือเฉพาะประโยคของเขา **ตรงเวลาไฟล์ต้นฉบับ** ทำซ้ำกับผู้พูดคนอื่นโดยเริ่มจากไฟล์เต็มใหม่ทุกตัว
- **Project > Sound** เก็บเสียงต้นฉบับครบและเป็นแหล่งเสียงหลัก ตรวจไม่ให้ Voice บนตัวละครเกิดเสียงซ้อน/ก้อง; ห้ามลบ Sound หลักและห้ามลบ Viseme ที่ต้องใช้
- ก่อนถือว่างานเสร็จ ต้องตรวจ Viseme Clip/Keys และตรวจปากอย่างน้อยสองเวลาขณะพูดและหนึ่งเวลาขณะเงียบ **ห้ามถือว่า Look front, Blink หรือ LoadAudioToObject เท่ากับมีบทพูด**
- รักษาท่า AccuPOSE เดิม ไม่ใช้ RemoveAllAnimations/.rlDikPreset ไม่เรนเดอร์ก่อนตรวจปากครบ. กฎนี้ **แทนที่วิธีตัด WAV ภายนอก** ที่ระบุไว้ก่อนหน้า. วิธีละเอียดอยู่ใน docs/iclone-key-SKILL.md

- **วิธีที่ใช้ได้จริง (ทดสอบ 2026-11-07):** เลือกผู้พูด (`scripts/ic8_select.ps1 <name>`) → Animation > Create Script > **Audio File** → เลือก N.mp3 เต็ม → Open (สร้าง viseme 652 keys ตลอด 81.5 s) → รัน `scripts/ic8_lip_trim.py` ลบ viseme key นอกช่วงพูดของคนนั้น. `RAudio.LoadAudioToObject` ใส่แค่เสียง **ไม่สร้าง viseme**. ตอนเรนเดอร์ใช้เสียงจาก mp3 ด้วย ffmpeg กันเสียงซ้อน.

## บทพูด / Lip Sync (บังคับสำหรับทุกท่อน)
- **ฉากที่ตัวละครมีบทพูด ตัวละครนั้นต้องพูดตรงเนื้อหาและเวลาจริง ห้ามนั่งนิ่งหรือปากไม่ขยับขณะมีบทพูด**. ก่อนทำฉาก ให้วิเคราะห์ N.mp3 และบทถอดเสียง สร้าง speaker | dialogue | start | end | full MP3 imported | in-iClone trimmed | viseme verified โดยแยกเสียงผู้บรรยายกับบทพูด.
- นำเข้า MP3 เต็มให้ Avatar ผ่าน iClone แล้วใช้เครื่องมือตัดใน iClone ให้เหลือเฉพาะช่วงที่พูด และสร้าง/รักษา lip sync หรือ viseme ตั้งแต่ต้นถึงท้ายประโยค ไม่ให้คนอื่นขยับปากผิดเวลา. ต้องตรวจทั้งคลิปเงียบและช่วงพูด.
- **Look front.iTalk/Auto Blink ไม่ได้แทนการขยับปาก** และผลลัพธ์ RAudio.LoadAudioToObject / watcher OK ยังไม่ใช่หลักฐานว่าพูดจริง. ตรวจ track viseme หรือผลภาพปากอย่างน้อยสองจังหวะขณะพูดพร้อมเทียบเสียง และตรวจหนึ่งจังหวะเงียบ; หากไม่มีหลักฐานให้รายงานว่า 'ยังไม่ตรวจผ่าน' ไม่ Render เป็นงานสำเร็จ.
- เก็บเสียงต้นฉบับบน Project Sound track. เมื่อใส่ WAV เพื่อสร้างปากพูด ตรวจว่าเสียงจาก Avatar ไม่ถูกเล่นซ้ำจนก้อง; แก้เฉพาะเสียงซ้ำโดยไม่ลบ Sound ต้นฉบับ.
- คงท่า AccuPOSE และ Body Motion เดิมทุกครั้ง ห้าม RemoveAllAnimations หรือโหลด .rlDikPreset ทางสคริปต์เพื่อแก้ปาก. ข้อกำหนดละเอียดอยู่ที่ docs/iclone-key-SKILL.md หัวข้อ บทพูดและลิปซิงก์.

## Look
- Faces must not be dark: one soft spot light per character, front-left a bit above the face, warm white
  `RRgb(255,236,214)`, **multiplier 0.04**, range 700, no shadow.

## Camera
- Lens **80 or 100 mm only** (keep framing: distance = 270 cm × focal/50 for a half body).
- Character shots: **DOF on**, focus on the character, background blurred.
- Wide/establishing view shots of the scene: **no DOF** (except interior scenes where the user wants everything blurred:
  part 2 interior = blur front and back, characters and their poses readable).
- Half body / MCU / OTS; no full body unless it's a view shot.
- If an irrelevant object blocks a good angle: **hide it**, don't keep nudging the camera.
- Cut on pauses in the narration (`ffmpeg -af silencedetect=n=-30dB:d=0.25`).
- When finished: viewport camera → **Switcher** so the user can just press Play.
- Cameras are designed LAST, after audio, characters, poses.

- **Part 2 monk shots (7.0-13.45 s and 53.82-75.5 s): frame chest-up only (อกขึ้นไป); hide lower robes because the clothing is unattractive.**

- **Part 2 visual quality (user, 2026-11-07): NEVER use a wide shot or composition that reveals full bodies, seated legs, knees, or lower robes. Cinematic eye-level chest-up MCU/close-ups and carefully cropped OTS/reaction shots only. Reject previews showing full-body, large blank walls, or obstructing foreground.**

## AccuPOSE in the GUI (works, part 2)
- Per character: select it by script (`scripts/ic8_select.ps1 <name>`, also goes to frame 0) → Modify tab (1172,150) →
  Motion (1228,132) → AccuPOSE (1320,326) → wait 5 s → click the pose → Apply Pose (482,580). The panel closes when the
  selection changes, so repeat the whole sequence for each character. The scroll position is kept between openings.
- With the list scrolled to the "Sit Ground" row: Sit Ground Hands on Knees (290,228), Sit Ground Cross Legs (494,228).
- Part 2: men + monk = Sit Ground Cross Legs, women = Sit Ground Hands on Knees.

## Placement
- Meeting/discussion with a monk (user): villagers in **two rows facing each other**, monk at the **head of the table**
  (far end, centre) facing down the aisle. Script: `scripts/ic8_part2_layout.py`.
- The user drops a marker block where things should go. Read its position by script, place around it,
  record it in `scene_anchors.md`, then delete the marker (or keep it hidden, but never put audio on it).

## Render
- Script render: `ic8_render2.py` (1920×1080, **60 fps**), then trim with ffmpeg to audio + 5 s, output `E:\Video\N.mp4`.


## GPT / MCP workflow (2026-11-07)
- Prefer the typed tools in mcp_server/server.py via the existing authorized Dino Tunnel connection for project/status/job tasks. Do not bypass safeguards by injecting arbitrary scripts into the watcher.
- Queue read-only inspections freely when explicitly requested, but inspect watcher logs and the inner JSON result before claiming success.
- Stage/motion/camera changes require the user's instruction; do not render without direct instruction. The OpenPlugin auto-start is optional and requires the user's UAC approval; never restart iClone with potentially unsaved scene work.
