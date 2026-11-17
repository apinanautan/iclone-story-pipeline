---
name: motion-ai
description: Generate a NEW motion from text with Toyxyz Motion AI (Kimodo) and import it onto a CC character. Only when no library motion fits AND the user said yes. Installs itself if missing.
---
# Motion AI (last resort)

1. Search library motions first. If one is truly missing, PROPOSE in Thai ("ท่านี้ไม่มีในคลัง ใช้ Motion AI สร้างไหม") and wait for yes.
2. Not installed (no `C:\MotionAI`)? Install it yourself, the user should not:
   `powershell -ExecutionPolicy Bypass -File tools\motion_ai\install.ps1` (needs NVIDIA GPU, Blender 5.2+, gh).
3. Generate: write `C:\MotionAI\gen.json`, run Blender with `tools\motion_ai\drive_gen.py`, then `tools\motion_ai\retarget.py`
   (it copies CC3_Base_Plus .fbxkey + .3dxProfile next to the FBX; without them the body is hunched).
4. Import onto the selected avatar: `powershell -File tools\motion_ai\ic_imp2.ps1 <fbx>` (keyboard + window messages, no mouse).
5. iClone may crash on repeated imports: save first.
