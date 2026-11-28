---
name: ai-iclone-preview
description: Operate the Ai-iclone Preview story pipeline on the Codex Windows machine. Use for Thai iClone 8 folk-tale work when the user asks to start a story, make or resume a part, inspect progress, fix a failed Preview step, review shots, or render an approved part.
---

# Ai-iclone Preview for Codex

The executable is the workflow controller. It reads the same state as the Preview window. Use the current executable's step, rules card, and output to decide what happens next. Reply in short, everyday Thai.

This skill adapts the [GPT plugin instructions](https://github.com/apinanautan/iclone-story-pipeline/blob/2217e54d97fecdd000930dfa2e7f46be553a8b3f/plugin/INSTRUCTIONS.md) from the canonical [GitHub main branch](https://github.com/apinanautan/iclone-story-pipeline/tree/main/plugin). The transport is local PowerShell on the Codex Windows host. The GPT plugin's MyComp Bot, tunnel, and MCP installation instructions belong to its remote deployment.

## Start or resume

1. Find the active installation. On this PC the working project is `%USERPROFILE%\Documents\iClone Story Pipeline`. If the user selected another local installation, use that one. The original standalone launcher defaults to `%USERPROFILE%\Downloads\Ai-iclone.exe` and installs files under `%LOCALAPPDATA%\Ai-iclone`. Use the executable's reported project root for all work files.
2. Run the selected executable with no arguments from its project directory. When the user refers to the Preview window, inspect the live window before selecting or editing a story. Its selected story can differ from the command-line selection. Match the CLI to the visible story and part with the use command, then read the next step. Tell the user briefly where work is and what the program shows next. If the program fails to start, report its actual error. The program manages its own updates.
3. For an instruction about the production, append a dated entry to the active project's `docs/rules.md`. Select the exact numbered story part requested by the user from the Preview part list. When the active selection differs, use the program to select the requested part and confirm the new title before running any production step. When the named story is unclear, use the active story if it uniquely fits. Get the range from the user when the program requires one.

For the working checkout, set the shell working directory to the project root and run:

```powershell
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
& .\Ai-iclone.exe
```

Run one Ai-iclone command at a time and read its result before acting.

## Map the user's request

| User request | Ai-iclone command |
| --- | --- |
| วันนี้ทำเรื่อง X | `use X`. Use `new-story X` when the user requests a new story and it does not exist. |
| ทำช่วง 7:14 ถึง 9:00 | `range 7:14-9:00` |
| ทำท่อน 2 | `use X 2`, then `do`. Confirm that Preview displays part 2 before starting work. |
| ต่อเลย | `do` |
| ผ่าน / อนุมัติ | At the applicable Preview approval gate, use `approve --said "<exact user words>"`. Approval is scoped to that gate. |
| ถึงไหน / ค้าง / FAIL | `status` and `log` |
| ลบไฟล์ขยะ | `clean` |
| เครื่องมือของโปรแกรมมีปัญหา | `update`, then `doctor`, and follow the reported diagnosis. |
| แปลงคลิปเป็นท่า | `video2motion <file>`. If the program stops to request installation approval, obtain it before using `--allow-install`. Verify and show the returned check video. Use the returned CC FBX with Convert All as directed by the program. |

## Run the Preview loop

For part production, own every AI and program step through the successful Switch camera step. After reviewing shots, continue through camera, motion, lighting, face and Switch checks in the live order. Verify that Preview shows Switch complete before presenting the part at the user review gate. A genuine program STOP is handled using the rules below.

- Run `do` for the current step. On `OK`, run the next `do`. On `AI WORK`, read the printed card or `rules <step>`, do the named work, then run `do` again. The launcher may report a generic nonzero code for `AI WORK` or `STOP`, so use the printed result and the live step along with the exit code.
- For iClone steps, verify iClone 8 and the project's `ic8_watch.py` watcher are available. If iClone is closed, follow the project's startup procedure. When a step is running, poll the same command to completion. If the shell times out, inspect `status` and `log` before taking any further action. Report measured progress or the actual wait condition.
- On `FAIL`, use `log` and the card to diagnose the earliest cause. Fix the named input using the recovery directed by the program or its card, then retry once. If a camera check exposes an earlier pose or motion failure, resolve that earlier issue through the project's workflow before rechecking camera framing. After a second failure, report the exact blocker. Resume a stopped retry only when the user directs it, using the program's displayed recovery command.
- When cutting between consecutive shots of the same person or the same group, make the subject visibly larger or smaller in the frame. A left-to-right angle change at the same image scale is insufficient. Choose lens, camera distance and framing together for a clear change, such as a two-shot that shows the holding pose followed by a tight shot on the child's expression. Compare the actual stills side by side and reshoot if the scale looks the same. Matching shot sizes are allowed when the focus changes to a different person, such as a dialogue reverse shot.
- At the camera review, inspect the actual required stills. Describe what is visible, mark failures truthfully, and use the card's reshoot procedure. The quality check includes the story action, age, wardrobe, venue, framing and visible contact, such as the supporting arm in a carrying pose. Show the reviewed images at the Preview user gate.
- On `STOP`, explain the actual gate or blocker. Continue after the user responds when the gate requires their input. Use Preview's `ready` step to prepare Switch and frame 0; save and reopen manually through iClone's File menu before rendering. Render only after the user explicitly passes the appropriate gate. Verify the final result through the program's video check.

## iClone project saving — mandatory user rule (2026-11-26)

- **Save projects only by manually clicking the visible iClone `File > Save Project` or `File > Save Project As` menu in the live app.** Never save an `.iProject` with Python/RLPy, a watcher job, CLI, PowerShell helper, `ic8_gui.ps1 save/saveas`, a Preview `ready` auto-save, or simulated `Ctrl+S` / `Ctrl+Shift+S`.
- The direct save script `scripts/ic8_save.py` is removed. The helper's `save` and `saveas` commands must refuse without saving.
- Preview `ready` first prepares Switch and frame 0, then stops at `AI WORK`. The operator must save through the visible File menu, reopen the same project through `File > Open`, confirm it loads and the title matches, then run Preview `do` again to verify the file timestamp and complete `ready`.
- For a new project, use the live `File > Save Project As` menu before continuing any work that needs the new project path. If Preview would trigger any scripted save, stop before that action and use the menu instead.

Use the program's standard commands and any existing helper explicitly directed by the live rules card. Preserve completed project data. Keep story and approval state tied to the program's verified results. Work in the local project and treat shared Google Drive story assets as read-only, except for an authorized finished-video publication through the project workflow.

## Diagnose iClone click and Play freezes

1. Measure iClone private/working memory, free physical RAM, pagefile use, and whether the timeline frame advances. Do this before blaming a motion or treating the project file as damaged.
2. If memory pressure is severe, preserve the current scene through the visible iClone File > Save Project As menu only. Restart iClone; if the old process has no window after a completed menu save, close only that iClone process.
3. Test Play in the empty scene. Then reopen the same saved project through File > Open and test its playback. This is the recovery order in project `docs/rules.md`.
4. Incident verified 2026-11-26: the old session reached 35.5–36.1 GB private memory, <0.5 GB free RAM, and >22 GB pagefile use; Play stalled. After restart, the empty scene and original `ท่อน1.1.iProject` played, and the original file opened successfully. The failure was session memory pressure; no project reset was needed.
5. If the clean-session project still stalls with adequate free RAM, isolate the scene/asset that causes it. Keep Preview completion and approval state intact; stop at the current user gate.

## Keep reusable rules in GitHub

When the user adds a reusable production rule, update the installed skill and the corresponding skill or rules in the canonical GitHub repository. Publish the scoped change and verify it appears upstream. Keep story assets, media, local paths and progress out of the commit.

## Lightweight sets and project saving

- For a bright lightweight folk-tale interior, use modular floor and wall pieces with a small window opening, soft daylight, and restrained background blur. Keep the performance and faces clear. Use generated geometry for structure and reserve image-to-3D for small optional props. Check dimensions, apertures, materials and performance in the target editor before accepting generated assets.
- Save iClone projects only through the visible File > Save Project or File > Save Project As menu. Never use a script, watcher, CLI or keyboard shortcut to save. Reopen through File > Open to verify the saved project before final delivery.

## Texture-only PBR

For texture-only PBR work, keep the mesh and UVs. Generate or extract one Base Color / Normal / Roughness / Metallic / Height set per material, with AO when supported. Keep plaster and ordinary wood nonmetallic. Supply separate maps for iClone and an ORM pack when using glTF. Use the normal convention required by the destination renderer. For an open window, leave the hole open so the scene artist can place their own exterior. Verify under neutral and angled light; identify approximate maps separately from model-derived or scanned maps.
