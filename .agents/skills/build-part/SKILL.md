---
name: build-part
description: Build a checked part spec in iClone - open/save-as the project, place the cast with motions, project sound, cameras with face light and DOF. Use after plan-part passes.
---
# Build a part in iClone

Prereq: iClone open with `scripts/ic8_watch.py` loaded (skill `iclone-control`), spec passes `check`.

```
python scripts/ic8_part.py parts/<spec>.json open     # opens project, or `from` + Save As (GUI) to a NEW file
python scripts/ic8_part.py parts/<spec>.json cast
python scripts/ic8_part.py parts/<spec>.json pose
python scripts/ic8_part.py parts/<spec>.json sound
python scripts/ic8_part.py parts/<spec>.json cams     # Cam_A/B, switcher, auto face light, DOF, stills
```
- If the target project does not exist yet, open the source in iClone and use `File > Save Project As` manually before continuing. Do not trigger Save As with a script or shortcut.
- After fixing a number in the spec: `python scripts/ic8_part.py <spec> <step> --from`.
- `cams` adds a face light per avatar. If the log says `WARNING NO FACE LIGHT`, the scene has no point/spot light: tell the user; do not fake it by cranking the directional light.
- Directional light colour uses normalized RRgb(1.0,0.92,0.84); the 255 scale washes out.
- Never use your own stage/camera scripts. Save only through the visible iClone File menu; never save by script, helper, CLI, watcher or simulated shortcut.
Next: `review-stills`.

## Attach after pose — mandatory (2026-11-27)
For a prop intended to remain on a body part, fit the pose and prop contact first; use Attach (permanent parent to the correct sub-node, e.g. hand for held trophy, head for glasses/hair). Preserve world placement, scale and orientation at attach time; inspect parent and parent node, check relative transform at start/middle/end and actual contact. Do not use repeated world-position tracking as a substitute for Attach when the prop must stay on the body. Use a timed Link only when the story requires handoff/release. For hair, parenting a prop to head does not convert it into a skinned hair asset; distinguish the two. Save the same main file via the authorized visible File > Save Project workflow at the approval gate; no duplicate files or render before approval. If the attachment API or GUI is not verified, stop and report the actual blocker rather than marking success.
- 2026-11-27: Cast → Sound → Pose → Lip → Cams. ใส่ Project Sound ครั้งเดียวหลังวางตัวละคร ตรวจชื่อคลิปและช่วงเวลา Timeline ที่เฟรม 0. การแก้ Pose/Motion/สีหน้า/กล้องหรือเพิ่มตัวละครในฉากเดิมไม่ต้องนำเสียงเข้าซ้ำ. ใส่ใหม่เมื่อเปิดโปรเจกต์ใหม่ เปลี่ยนไฟล์เสียง หรือยืนยันว่าเสียงผิด/หาย. Lip Sync หลัง Pose เฉพาะผู้พูด ไม่ใช่ใส่ Project Sound ซ้ำ. ไม่ข้ามจุดอนุมัติ.


## Current integrated runtime
Follow docs/CINEMATIC_SLEEP.md and live Preview cards. New camera and evidence rules supersede old 80/100-only and fixed-cut rules. Preserve sound and actual manual File-menu save/reopen. Normal and Sleep share QA; Sleep requires explicit scoped activation. Do not bypass real checks.
