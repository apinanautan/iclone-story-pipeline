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
6. After the user approves: lip-sync -> skill `lip-sync`, then Preview `ready` to prepare Switch/frame 0. At its `AI WORK` gate, save manually from iClone's `File` menu, keep it open, then run Preview `do` again to verify and complete `ready`.
7. **Render only when the user says ผ่าน / เรนเดอร์** -> skill `save-render`.

Hard rules (break none):
- Never write into {DRIVE} (the shared Google Drive, read only), except copying the finished video to the publish folder.
- **Saving rule (user 2026-11-26):** save only by clicking iClone `File > Save Project` / `File > Save Project As` in the live UI. Never use Python/RLPy, CLI, watcher, PowerShell helper, or simulated keyboard shortcuts to save. The `ic8_gui.ps1 save/saveas` commands are disabled and `ic8_save.py` is removed. Do not reopen merely to test the save.
- Never call RGlobal.RenderAudio or RAudio.LoadAudioToObject (hang/crash).
- Use the live UI to manually click File > Save Project / Save Project As without reopening; use helpers for other chores. Never delete iCloneStoryBridge.
- Max 2 parts per chat. Library motions first; Motion AI only after the user says yes (skill `motion-ai`).
- Do not write your own stage/camera scripts to bypass `ic8_part.py`. If a shared script lacks a feature, fix the shared script.
- Every new user instruction -> append to `docs/rules.md` immediately.
- Do not spend long on one step: if blocked (missing file, rule conflict), tell the user in Thai what blocks you and ask.
- 2026-11-27: Both New Story and Continue Part prompts must contain the same detailed reusable project/tool handbook, live Script Catalog, plugin instructions and Skills. Continue adds active story and current progress only. Never rely on chat memory for tool availability. Use installed plugin, Preview and existing scripts before writing new ones. Goal tracker interval 90 seconds; preserve preview priority, busy/draft guards and completion stop.


## Current integrated runtime
Follow docs/CINEMATIC_SLEEP.md and live Preview cards. New camera and evidence rules supersede old 80/100-only and fixed-cut rules. Preserve sound and actual manual File-menu save without reopen. Normal and Sleep share QA; Sleep requires explicit scoped activation. Do not bypass real checks.


## Current save/render rule (2026-11-27)
Switch -> frame zero -> native File > Save Project -> Render the current open scene. Do not reopen merely to test saving. If save cannot be verified and the user authorizes live rendering, use Ai-iclone do --render-live at Ready, then Ai-iclone do to Render. The save remains pending; verify video separately. Preserve the live scene and do not advance to another part until saved. Never use scripted project save or mark a failed save complete. This supersedes earlier mandatory reopen instructions.
