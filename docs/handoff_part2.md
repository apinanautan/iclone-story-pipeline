# Handoff prompt: continue มหาอกหัก part 2 (paste to GPT / another AI)

You are continuing an iClone 8 animation job on the user's Windows PC. Answer the user in Thai.
Project folder: `C:\Users\Apinan\Documents\iClone Story Pipeline`. **Read first:** `AGENTS.md`, `docs/rules.md`,
`docs/part2_plan.md`, `docs/scene_anchors.md`, `docs/accupose_presets.md`. Follow every rule in rules.md, and add any
new instruction from the user to rules.md immediately. Do one step at a time; don't render unless the user says so.

## Current state (2026-11-07 10:05)
- iClone is open with `E:\FileSave\2.iProject` (scene: temple interior, floor z = 25774). Saved.
- Audio `C:\Users\Apinan\Downloads\audio_output\2.mp3` (81.5 s) is on the Project **Sound** track. Timeline = 86.5 s (audio + 5 s).
- 6 characters (`p2_monk, p2_im, p2_old, p2_young, p2_woman, p2_commf`) placed: villagers in two rows facing each other,
  monk at the head of the table (`scripts/ic8_part2_layout.py` has the coordinates).
- Body poses done with AccuPOSE (GUI): men + monk = Sit Ground Cross Legs, women = Kneel Seiza. **All other animation was
  cleared**, so no face clip, blink or lip sync yet.
- Each character has a face light `FaceLight_<id>` (multiplier 0.04). Cameras `Camera`, `Camera_0` exist but aren't keyed.
- The watcher (`scripts/ic8_watch.py`) is loaded in iClone: drop a `.py` into
  `%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\run\` → it runs → becomes `.done`/`.err` + `.log`.

## Next steps (in order, one at a time, report to the user after each)
1. **Face + blink + lip sync**, WITHOUT touching the body pose. Per character:
   - Load face clip `G:\คอมพิวเตอร์เครื่องอื่นๆ\คอมพิวเตอร์ของฉัน\โมชั่น\Digital Soul 100+\1.Watch\Look front.iTalk`
     (select avatar, SetTime(0), `RFileIO.LoadFile`), set speed so it spans 86.5 s; it's 20.4 s, so speed 0.5 and chain copies
     (rule: slowest possible, min ~0.5).
   - `GetFaceComponent().SetAutoBlinkName('Normal')`.
   - Lip sync on speakers only: `RAudio.LoadAudioToObject(avatar, wav, RTime start)` with the wavs already cut in `ic8_jobs`:
     p2_old ← p2_old.wav @1.4 s, p2_im ← p2_im.wav @13.4 s, p2_woman ← p2_woman.wav @31.7 s, p2_young ← p2_young.wav @40.8 s.
   - Reuse code from `scripts/ic8_part2_build.py` (face/blink/lips part only; USE_BODY_MOTION stays False). **Do NOT call
     RemoveAllAnimations** (it would wipe the AccuPOSE poses) and **never load .rlDikPreset by script** (crashed iClone).
   - Check: render a still (`RGlobal.RenderImage`) from a camera ~3.5 m from the group; poses must still be seated.
   - Save (Ctrl+S).
2. **Cameras last**, per the shot list in `docs/part2_plan.md`: lenses 80/100 mm only; this interior = blur front and back
   (DOF on) but characters and their poses readable; cut on the listed times with `RScene.AddSwitchCameraKey`.
   Stills first → show the user → fix. Then set the viewport camera to **Switcher**. Save.
3. Render only when the user says: `scripts/ic8_render2.py` (1920×1080 **60 fps**), trim with ffmpeg to 86.5 s → `E:\Video\2.mp4`.

## Watch out
- Mouse/GUI only for what RLPy can't do (AccuPOSE, creating cameras/lights, File > Import audio, Save As). Bring iClone to
  the front first; Chrome often steals focus.
- A "python script not compatible" popup → Cancel.
- If iClone crashes: on restart choose OK to restore unsaved data, save it to `E:\FileSave\2.iProject`.
- Never write into the G: story folder. Only `E:\FileSave\2.iProject` and `E:\Video\2.mp4`.
