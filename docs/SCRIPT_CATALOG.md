# Script catalog / สารบัญสคริปต์ iClone Story Pipeline

ตรวจรายการ 2026-11-27: GitHub main `4762d6bc` (116 ไฟล์) + working tree Windows (133 ไฟล์) = 134 รายการไม่ซ้ำ (Python, PowerShell, JS, CMD, C#) ไม่รวม backup, cache, generated jobs, dependencies, ข้อมูลและคีย์ส่วนตัว

**ก่อนสร้างสคริปต์ใหม่:** เปิด Ai-iclone.exe แบบไม่มีอาร์กิวเมนต์ อ่านสถานะและ rules card ขั้นปัจจุบัน ค้นสารบัญนี้ อ่านซอร์สจริงและตรวจไฟล์บนเครื่องก่อนใช้ เลือก generic scripts ที่มีอยู่ผ่าน Preview/CLI ที่อนุญาตเท่านั้น หากจำเป็นแก้ของเดิมเฉพาะจุดตามที่ผู้ใช้อนุญาต ไม่สร้างระบบซ้ำ ไม่ข้าม gate ไม่เรนเดอร์ก่อนอนุมัติ ตรวจผลจริงก่อนยืนยัน

**ทั้งสอง** = พบใน main และเครื่อง (เนื้อหาอาจต่างกัน), **เครื่อง** = พบเฉพาะ working tree ยังไม่รับรองการเผยแพร่หรือผลทดสอบ, **main เท่านั้น** = ไม่พบในเครื่อง ห้ามเรียกโดยอัตโนมัติ. ชื่อไฟล์ไม่รับประกันการใช้งาน ให้ตรวจ arguments, dependencies, side effects และ rules card. สารบัญเป็นดัชนี ไม่ใช่สิทธิเรียกทุกสคริปต์.

## เส้นทางเลือกใช้
- จัดท่า/กระดูก/prop: motion_pool → ic8_part ขั้น pose → ic8_pose_place. Blender: ตรวจ retarget / ic_imp2 ก่อนเขียนตัวใหม่. การ import FBX ล่าสุดยังไม่ผ่าน อย่าอ้างสำเร็จ.
- กล้อง/แสง/ภาพ: ic8_cams → contact_sheet → cam_check / light_check / still_check ตาม Preview. ให้คิวภาพมาก่อน Goal Tracker.
- เสียง/ปาก: cut_audio → sound/lip ตาม Preview → ic8_lip_check, ic8_mouth_check. รักษาเสียงเต็มตามกฎ.
- บันทึก: File > Save Project และ reopen ตรวจจริง; หนึ่งไฟล์หลักต่อท่อน. สำรองชั่วคราวเมื่อจำเป็นใน scratch เดียว ล้างเมื่อผ่าน ไม่สร้าง backup/recovery กระจาย.
- ทดสอบ/ซ่อม: ailog, progress, watcher logs, tests. ไม่ใช้สคริปต์เฉพาะฉากเก่าหรือไฟล์ทดลองแทน flow.

## ตัวควบคุมหลักและระบบ

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `Ai-iclone.cmd` | ตัวเรียก CLI | ทั้งสอง |
| `launcher/AiIclone.cs` | ซอร์ส C# ตัวเปิด Ai-iclone.exe | ทั้งสอง |
| `launcher/build.ps1` | คอมไพล์ตัวเปิดโปรแกรม | ทั้งสอง |
| `mcp_server/server.py` | MCP server เรียกคำสั่ง Preview/CLI | ทั้งสอง |
| `mcp_server/install_openplugin.cmd` | ตัวเรียกติดตั้ง OpenPlugin | ทั้งสอง |
| `mcp_server/install_openplugin.ps1` | ติดตั้งตัวโหลด watcher อัตโนมัติ | ทั้งสอง |
| `mcp_server/openplugin/main.py` | โหลด watcher ตอนเปิด iClone | ทั้งสอง |
| `scripts/ai_iclone.py` | CLI หลัก เลือกเรื่อง ท่อน ขั้นงาน ตรวจผลและอนุมัติ | ทั้งสอง |
| `scripts/ailog.py` | บันทึก progress จริง เวลา และ FAIL REPORT | ทั้งสอง |
| `scripts/ic8_story.py` | จัดการข้อมูลเรื่อง แผนท่อน และ brief | ทั้งสอง |
| `scripts/ic8_part.py` | ประมวลผลท่อนตามสเปกและ Preview | ทั้งสอง |
| `scripts/paths.py` | แปลงตัวแปร MOTION/DRIVE/SAVE/VIDEO/DESKTOP | ทั้งสอง |
| `scripts/progress_app.py` | หน้าต่าง Preview และสถานะ | ทั้งสอง |
| `scripts/progress_board.py` | คำนวณสถานะขั้นจากผลและไฟล์จริง | ทั้งสอง |
| `scripts/preview_gate.py` | ควบคุม dispatch lease ป้องกันขั้นซ้อนและนอก flow | เครื่อง |
| `scripts/selfupdate.py` | อัปเดตโปรแกรมจาก GitHub release | ทั้งสอง |
| `scripts/ic8_gui.ps1` | GUI helper เปิดงาน เสียง lip-sync Switch และ render ตาม Preview | ทั้งสอง |
| `scripts/ic8_watch.py` | watcher ใน iClone รัน Python ทีละ job เขียน log และ done/error | ทั้งสอง |
| `scripts/ic8_watch.ps1` | ตรวจความพร้อมและ popup ตามกฎ | ทั้งสอง |
| `scripts/ic8_ui.ps1` | UI Automation ของ iClone | ทั้งสอง |
| `scripts/ic8_open.ps1` | กรอก path ในกล่องเปิดไฟล์ด้วย Win32 | ทั้งสอง |
| `scripts/ic8_select.ps1` | เลือก avatar ผ่าน watcher และไปต้นคลิป | ทั้งสอง |
| `scripts/IG.Win32.cs` | ซอร์ส Win32 interop สำหรับหน้าต่างและ input | เครื่อง |
| `scripts/fix_ic8_plugin_compat.ps1` | แก้ popup แจ้งปลั๊กอิน Python ไม่เข้ากับ iClone | ทั้งสอง |
| `scripts/ic8_startup_popup_guard.ps1` | จัดการ popup เปิดโปรแกรมที่รู้จัก | ทั้งสอง |
| `scripts/install_ic8_startup_popup_guard.ps1` | ติดตั้ง startup popup guard | ทั้งสอง |
| `scripts/ocr.ps1` | อ่านตัวอักษรจากภาพด้วย Windows OCR | ทั้งสอง |

## ฉาก ตัวละคร กล้อง เสียง และโมชั่นทั่วไป

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `scripts/cut_audio.py` | ตัด master audio ตามช่วงและจุดเงียบ พร้อมถอดเสียง | ทั้งสอง |
| `scripts/glb2fbx.py` | แปลง GLB เป็น FBX prop จัดขนาด จุดวาง texture | ทั้งสอง |
| `scripts/ic8_pose_place.py` | จัด avatar โหลด motion ท่ากระดูก สีหน้า มอง และ prop tracking ตามสเปก | ทั้งสอง |
| `scripts/ic8_cams.py` | กล้อง การเคลื่อนกล้อง สลับช็อต แสงเสริมและภาพนิ่ง | ทั้งสอง |
| `scripts/ic8_scene_scan.py` | สำรวจวัตถุ ตัวละคร ตำแหน่ง bounds แบบอ่านอย่างเดียว | ทั้งสอง |
| `scripts/ic8_scene_overview.py` | สำรวจภาพรวมฉาก ไม่ใช่ขั้นจัดกล้องจริง | ทั้งสอง |
| `scripts/ic8_survey.py` | สำรวจ prop/avatar/camera/light และตำแหน่ง/ขนาด | ทั้งสอง |
| `scripts/ic8_survey2.py` | สำรวจ prop/avatar/camera และพิกัดอีกรูปแบบ | ทั้งสอง |
| `scripts/ic8_place.py` | จัดตำแหน่ง avatar ที่มีอยู่และซ่อนตัวอื่น | ทั้งสอง |
| `scripts/ic8_lip_apply.py` | ใส่ viseme keys จากข้อมูลที่สร้างไว้ | ทั้งสอง |
| `scripts/ic8_lip_trim.py` | ตัด viseme ให้ตรงช่วงพูดหลังนำเข้าเสียงเต็ม | ทั้งสอง |
| `scripts/ic8_lip_restore.py` | คืน viseme keys จากข้อมูลสำรอง | ทั้งสอง |
| `scripts/motion_pool.py` | ค้นหาและจัด tag คลัง motion ตามบริบท | ทั้งสอง |
| `scripts/video2motion.py` | แปลงวิดีโอคนเป็น BVH และ CC FBX ผ่าน Blender | ทั้งสอง |
| `scripts/video_to_bvh.py` | สกัด body motion ด้วย RTMPose/MotionBERT เป็น BVH | ทั้งสอง |
| `tools/transcribe.py` | ถอดเสียงไทยด้วย faster-whisper เป็นข้อความและช่วงเวลา | ทั้งสอง |
| `tools/lip_from_audio.py` | สร้างคีย์ปากจากระดับเสียงเพื่อทดลอง ไม่แทน AccuLips | ทั้งสอง |
| `tools/hair_training_kit.py` | สร้างโมเดลสถานีฝึกทำผมสำหรับ prop loader | เครื่อง |

## ตรวจคุณภาพและวิเคราะห์

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `scripts/cam_check.py` | ตรวจภาพกล้องแต่ละช็อตและคำตอบ QA ตาม Preview | ทั้งสอง |
| `scripts/contact_sheet.py` | รวมภาพนิ่งเป็น contact sheet | ทั้งสอง |
| `scripts/still_check.py` | ตรวจความสม่ำเสมอและข้อผิดปกติภาพนิ่ง | ทั้งสอง |
| `scripts/light_check.py` | ตรวจแสงบนใบหน้าจากภาพนิ่ง | ทั้งสอง |
| `scripts/ic8_dense_frame_review.py` | เก็บภาพ/ข้อมูลทีละเฟรมใน iClone ไม่เรนเดอร์หนัง | ทั้งสอง |
| `scripts/build_dense_storyboard.py` | รวมภาพตามเวลาเป็น storyboard 30 เฟรมต่อแผ่น | ทั้งสอง |
| `scripts/analyze_dense_storyboard.py` | วิเคราะห์ภาพต่อเนื่องประกอบการตรวจจริง | ทั้งสอง |
| `scripts/analyze_p52_motion_qa.py` | ตรวจระยะ/การชนประมาณจากกระดูกและ AABB prop | ทั้งสอง |
| `scripts/ic8_lip_check.py` | นับ viseme keys และช่วงเวลาของ avatar | ทั้งสอง |
| `scripts/ic8_mouth_check.py` | เก็บภาพปากช่วงพูด/เงียบเพื่อตรวจ lip-sync | ทั้งสอง |
| `scripts/ic8_speed_probe.py` | อ่านช่วง ความยาว ความเร็ว body clip และ API | ทั้งสอง |
| `scripts/ic8_probe.py` | ตรวจข้อมูลเวลา iClone | ทั้งสอง |
| `scripts/ic8_motion_check_job.py` | สุ่มตำแหน่ง bounds วัด drift/jump; ช่วงเวลาคงที่ต้องตรวจ | ทั้งสอง |
| `scripts/review_video_motion.py` | ตรวจเฟรมกระโดด/ความต่อเนื่องของวิดีโอ | ทั้งสอง |
| `tools/motion_meter.py` | วัด optical flow ต่อช็อตไม่นับรอยตัด | ทั้งสอง |

## Blender และ Motion AI

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `tools/motion_ai/install.ps1` | ติดตั้ง Toyxyz Motion AI/Kimodo เมื่อได้รับอนุญาต | ทั้งสอง |
| `tools/motion_ai/drive_gen.py` | ขับ Blender/Kimodo สร้างและ export motion | ทั้งสอง |
| `tools/motion_ai/bvh2blend.py` | นำเข้า BVH ตั้งชื่อกระดูก บันทึก blend | ทั้งสอง |
| `tools/motion_ai/retarget.py` | แปลง motion เป็น CC_Base FBX พร้อม profile/key | ทั้งสอง |
| `tools/motion_ai/ic_imp2.ps1` | นำ External Motion FBX ใส่ avatar ที่เลือก; แก้ล่าสุดยังไม่ผ่านครบวงจร | ทั้งสอง |
| `tools/motion_ai/prev2.py` | สร้างวิดีโอตรวจท่า Blender Workbench | ทั้งสอง |
| `tools/motion_ai/restvar.py` | ทดลอง export ท่าพักและแกน/scale FBX | ทั้งสอง |
| `tools/motion_ai/trophy_pose_13/inspect.py` | อ่าน rig และพิกัดกระดูกสำหรับท่าถือถ้วย | เครื่อง |
| `tools/motion_ai/trophy_pose_13/pose.py` | สร้างท่าถือถ้วย FBX/Blend/ภาพตรวจ; ยังไม่ยืนยัน import จริง | เครื่อง |

## Chrome Preview Bridge และ Goal Tracker (เฉพาะเครื่อง)

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `tools/chrome_preview_bridge/background.js` | service worker ส่งภาพเข้าแชตที่ผูกไว้และตรวจใบตอบรับ | เครื่อง |
| `tools/chrome_preview_bridge/queue_preview.py` | จัดคิวภาพสดจากขั้นกล้อง | เครื่อง |
| `tools/chrome_preview_bridge/capture_preview.py` | จับภาพหน้าต่าง iClone และเลือกส่งเข้าคิว | เครื่อง |
| `tools/chrome_preview_bridge/relay.py` | HTTP relay ในเครื่องสำหรับคิวภาพ phase และใบตอบรับ | เครื่อง |
| `tools/chrome_preview_bridge/start-relay.cmd` | เปิด relay | เครื่อง |
| `tools/chrome_preview_bridge/test_relay.py` | ทดสอบ relay ภาพและการเข้าถึง | เครื่อง |
| `tools/chrome_preview_bridge/goal_tracker.js` | ติดตามบริบททุก 150 วินาทีและหยุดตาม Achievement Key | เครื่อง |
| `tools/chrome_preview_bridge/achievement_observer.js` | เฝ้าตรวจ/ปลุก tracker ในแชต | เครื่อง |
| `tools/chrome_preview_bridge/goal_panel.js` | กล่องลอยสถานะ นับถอยหลัง เริ่ม/พัก | เครื่อง |
| `tools/chrome_preview_bridge/popup.js` | ปุ่มและสถานะเมนูส่วนขยาย | เครื่อง |

## เฉพาะงานเดิม/ทดลอง — ห้ามใช้แทน generic Preview

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `scripts/ic8_angry.py` | ทำสีหน้าโกรธให้ตัวละครเฉพาะฉากเดิม | ทั้งสอง |
| `scripts/ic8_audio_clip_probe.py` | ตรวจ API และเวลาคลิปเสียง/viseme | ทั้งสอง |
| `scripts/ic8_audio_clip_probe2.py` | ตรวจ viseme พระฉากเก่า | ทั้งสอง |
| `scripts/ic8_audio_clip_probe3.py` | ตรวจ length/start offset/speed ของ viseme | ทั้งสอง |
| `scripts/ic8_blend_clips.py` | ผสมคลิป body/face ต่อกันในฉากเดิม | ทั้งสอง |
| `scripts/ic8_cameras.py` | สร้างกล้อง MCU 8 ช็อตสำหรับท่อน 9 เดิม | ทั้งสอง |
| `scripts/ic8_cast.py` | โหลดสุนีย์และจัดการแสดงท่อน 8 เดิม | ทั้งสอง |
| `scripts/ic8_head_nod.py` | ใส่คีย์ก้มเงยศีรษะในฉากเดิม | ทั้งสอง |
| `scripts/ic8_key_shot.py` | จัดนักแสดงรอบ anchor และ motion จาก shot JSON แบบเก่า; ห้ามใช้วิธี save เดิม | ทั้งสอง |
| `scripts/ic8_look.py` | เก็บภาพมุมสูงบ้านเฉพาะฉาก | ทั้งสอง |
| `scripts/ic8_motion_speed.py` | วัด/ปรับความเร็ว motion ในช่วงเก่า | ทั้งสอง |
| `scripts/ic8_mouth_check4.py` | เก็บภาพตรวจปากพระท่อน 4 เดิม | ทั้งสอง |
| `scripts/ic8_part10_inspect.py` | ตรวจ bounds prop ท่อน 10 เดิมและลบ animation avatar เฉพาะตัว ไม่ใช่ read-only | ทั้งสอง |
| `scripts/ic8_part10_scale.py` | ปรับสเกลตามขนาดจริงท่อน 10 เดิม | ทั้งสอง |
| `scripts/ic8_part2_cams.py` | กล้องและ DOF ท่อน 2 เดิม | ทั้งสอง |
| `scripts/ic8_part2_layout.py` | จัดคนสองแถวและพระหัวแถวท่อน 2 เดิม | ทั้งสอง |
| `scripts/ic8_part3_cams.py` | กล้องสองตัวสลับช็อตท่อน 3 เดิม | ทั้งสอง |
| `scripts/ic8_part4_cams.py` | กล้องสองตัวสลับช็อตท่อน 4 เดิม | ทั้งสอง |
| `scripts/ic8_part5_cams.py` | กล้องสองตัวสลับช็อตท่อน 5 เดิม | ทั้งสอง |
| `scripts/ic8_part5_setup.py` | ตั้งความยาวและเอา viseme พระออกท่อน 5 เดิม | ทั้งสอง |
| `scripts/ic8_part6_cams.py` | กล้องสองตัวสลับช็อตท่อน 6 เดิม | ทั้งสอง |
| `scripts/ic8_part6_extras_nod.py` | ท่าก้มเงยตัวประกอบท่อน 6 เดิม | ทั้งสอง |
| `scripts/ic8_part6_setup.py` | ตั้งความยาวท่อน 6 เดิม | ทั้งสอง |
| `scripts/ic8_part7_cams.py` | กล้องสองตัวสลับช็อตท่อน 7 เดิม | ทั้งสอง |
| `scripts/ic8_part7_cast_extras.py` | ท่าก้มเงยและมองตัวประกอบท่อน 7 เดิม | ทั้งสอง |
| `scripts/ic8_part7_setup.py` | ตั้งความยาวท่อน 7 เดิม | ทั้งสอง |
| `scripts/ic8_part8_cams.py` | กล้องสองตัวสลับช็อตท่อน 8 เดิม | ทั้งสอง |
| `scripts/ic8_part8_setup.py` | ตั้งความยาวท่อน 8 เดิม | ทั้งสอง |
| `scripts/ic8_part9_cams.py` | กล้องสองตัวสลับช็อตท่อน 9 เดิม | ทั้งสอง |
| `scripts/ic8_part9_move.py` | ย้ายคนทำงานไปหน้าโบสถ์ที่มีแสงท่อน 9 เดิม | ทั้งสอง |
| `scripts/ic8_part9_setup.py` | ตั้งความยาวท่อน 9 เดิม | ทั้งสอง |
| `scripts/ic8_pose_face.py` | ใส่ท่าแขน ก้มเงย กะพริบ ยิ้มท่อน 7 เดิม | ทั้งสอง |
| `scripts/ic8_render.py` | render เฟรมผ่าน API แบบเก่า; ห้ามเรียกตรง/ก่อนอนุมัติ | ทั้งสอง |
| `scripts/ic8_render2.py` | render จาก JSON แบบเก่า; ห้ามเรียกตรง/ก่อนอนุมัติ | ทั้งสอง |
| `scripts/ic8_render_preview480.py` | render ทดสอบ 480p แบบเก่า; ไม่ใช่ภาพนิ่ง ห้ามก่อนอนุมัติ | ทั้งสอง |
| `scripts/ic8_rental_mcu.py` | สำรวจจุดเช่าบ้านและภาพ MCU คืน avatar อ้างอิง | ทั้งสอง |
| `scripts/ic8_rental_survey.py` | สำรวจจุดเช่าบ้านโดยไม่ save | ทั้งสอง |
| `scripts/ic8_save.py` | สคริปต์ save เก่าคงอยู่บน GitHub แต่ถูกลบในเครื่อง ห้ามใช้ | main เท่านั้น |
| `scripts/ic8_shots.py` | คีย์มุมกล้องตาม avatar และ render แบบเก่า; ห้ามเรียกตรง | ทั้งสอง |
| `scripts/ic8_smile.py` | ใส่รอยยิ้มต่อเนื่องในฉากเดิม | ทั้งสอง |
| `scripts/ic8_solo.py` | จัดตัวละครเดี่ยว/motion จาก solo JSON แบบเก่า | ทั้งสอง |
| `scripts/ic8_stage.py` | จัดการแสดงในฉากที่มีคนและกล้องแล้วแบบเก่า | ทั้งสอง |
| `scripts/ic8_story_cams.py` | กล้องจากพิกัดและเวลาคงที่ของเรื่องเก่า | ทั้งสอง |
| `scripts/rental_mark_spots.py` | ฉายจุดพื้นโลกลงภาพจาก FOV | ทั้งสอง |
| `scripts/rental_package.py` | รวมหลักฐานสำรวจจุดเช่าบ้าน | ทั้งสอง |
| `scripts/validate_event_clip_plan.py` | ตรวจแผน event clips ท่อน 3 เดิม | ทั้งสอง |
| `scripts/zz_load_alt_scene.py` | ทดลองเปิดฉากสำรองเฉพาะเรื่อง path คงที่ | เครื่อง |
| `scripts/zz_load_wedding.py` | ทดลองเปิดฉากงานแต่งเฉพาะเรื่อง | เครื่อง |

## ทดสอบออฟไลน์

| ไฟล์ | หน้าที่โดยย่อ | แหล่ง |
|---|---|---|
| `tests/test_ai_iclone.py` | ทดสอบคำสั่งและ flow CLI | ทั้งสอง |
| `tests/test_mcp_server.py` | ทดสอบ MCP server โดยไม่เปิด iClone | ทั้งสอง |
| `tests/test_motion_pool.py` | ทดสอบ tag และค้น motion | ทั้งสอง |
| `tests/test_motion_variety.py` | ทดสอบความหลากหลายของท่า | ทั้งสอง |
| `tests/test_no_machine_paths.py` | ตรวจไฟล์เผยแพร่ไม่ฝัง path เครื่อง | ทั้งสอง |
| `tests/test_preview_gate.py` | ทดสอบ dispatch gate และการอนุญาต Preview | เครื่อง |
| `tests/test_still_check.py` | ทดสอบตัวตรวจภาพนิ่งออฟไลน์ | ทั้งสอง |


## Sound workflow release v1.7.7
- scripts/workflow_state.py - pure dependency invalidation and Project Sound source receipt; keep sound during cast/pose/motion repair, revalidate on new project or changed WAV.
- tests/test_sound_workflow.py - offline regression checks of real step order, one native import, sound retention and changed WAV.
- docs/CHROME_PREVIEW_GUIDE.md - local Chrome extension/relay usage and safe chat binding. Browser key and local binding stay off GitHub.

## 1.7.8 candidate additions
- scripts/cinematic_qa.py: scene, prop, replan, editorial, final evidence gates.
- scripts/ic8_scene_review.py: temporary survey camera, restores view/time.
- scripts/blender_prop_build.py / blender_prop_export.py: headless prop build + geometry QA + FBX.
- scripts/media_qa.py: independent stream lengths.
- scripts/sleep_session.py: approved plan and handoff state.
- scripts/motion_analyze.py / blender_motion_analyze.py: evaluated skeleton sample/cache; transfer not yet verified.
- tools/chrome_preview_bridge/sleep_mode.js: opt-in chat handoff, verification required.

## 1.7.9: Goal Tracker
- relay.py: /goal/status, /goal/check, /goal/resume: stop latch and real Preview approval/completion gates.
- goal_tracker.js: consumes relay stop, cancels alarm and disables session; Achievement remains supplemental.
