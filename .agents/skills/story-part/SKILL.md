---
name: story-part
description: Make one part (ท่อน) of a Thai folk-tale video in iClone from a story name and a time range, e.g. "ทำเรื่องรักลำเอียง ช่วง 4:15 ถึง 5:15". Master skill - runs the other skills in order and stops for the user.
---
# Make one story part (master flow)

Answer the user in simple Thai. Show the plan in Thai before touching iClone.

1. **Plan in Thai first.** Read `docs/CURRENT_STORY.md` (overwrite it for a new story) and `stories/<story>.json` (scenes, spots, approved cams). Tell the user: scene, cast, time range, and the save path (a NEW file - never overwrite an existing .iProject).
2. **Cut the audio** -> skill `cut-audio`.
3. **Write + check the part spec** -> skill `plan-part`. `ic8_part.py check` must print OK.
4. **Build in iClone** -> skill `build-part` (open, cast, pose, sound, cams). Motion + expressions -> skill `acting`; adjusting a pose / lean / arms -> skill `pose-bones`.
5. **Review stills** -> skill `review-stills`. Send the contact sheet. **STOP and wait** for the user.
6. After the user approves: lip-sync -> skill `lip-sync`, then `ic8_part.py <spec> ready`.
7. **Render only when the user says ผ่าน / เรนเดอร์** -> skill `save-render`.

Hard rules (break none):
- Never write into {DRIVE} (the shared Google Drive, read only), except copying the finished video to the publish folder.
- Never save with RFileIO.SaveProject; save only through the GUI (`ic8_gui.ps1 save/saveas`), then prove it reopens.
- Never call RGlobal.RenderAudio or RAudio.LoadAudioToObject (hang/crash).
- Never use the mouse or screen coordinates; never delete iCloneStoryBridge.
- Max 2 parts per chat. Library motions first; Motion AI only after the user says yes (skill `motion-ai`).
- Do not write your own stage/camera scripts to bypass `ic8_part.py`. If a shared script lacks a feature, fix the shared script.
- Every new user instruction -> append to `docs/rules.md` immediately.
- Do not spend long on one step: if blocked (missing file, rule conflict), tell the user in Thai what blocks you and ask.

## Project Sound / Preview — 2026-11-27
- Cast → Sound → Pose → Lip → Cams. Import Project Sound only once per loaded project; inspect the clip name and full part range at frame 0. Repair Pose/Motion/face/camera or add cast without importing it again. Re-import only when a different project/audio is loaded or sound is confirmed missing/wrong. Lip Sync uses the original full part audio per speaker and retains the Project Sound track.
- Save/reopen only via the visible iClone File menu. No automatic script save, and no render before approval.
- For the locally installed Chrome Preview Bridge and Goal Tracker, read docs/CHROME_PREVIEW_GUIDE.md; check actual installation and exact authorized conversation before use.
