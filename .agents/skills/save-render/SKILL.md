---
name: save-render
description: Save the part through the GUI, prove it reopens, and render 1080p60 with the Switch camera and clean audio. Render ONLY after the user explicitly approves.
---
# Save + render

Save (only through the visible iClone menu):
- Run Preview `ready` once to prepare Switch and frame 0. It pauses at `AI WORK` for the manual save gate.
- Manually click iClone `File > Save Project` or `File > Save Project As` in the live UI. Never use a script, helper, CLI, watcher or simulated shortcut to trigger saving.
- Reopen the same `.iProject` with iClone `File > Open`, confirm it loads with the expected title and no `*`, then run Preview `do` again so `ready` verifies the changed file time and completes.
Render - **only when the user says ผ่าน / เรนเดอร์**:
```
python scripts/ic8_part.py parts/<spec>.json render --approved
```
- Uses `ic8_gui.ps1 render`: viewport camera = Switch, 1920×1080 at 60 fps, clean wav muxed with ffmpeg, checks fps/length/volume, one frame per shot.
- Preview is the controller: inspect `Ai-iclone status` and `Ai-iclone rules render`; render only when the current Preview step is `render` and its approval gate is satisfied. Advance with `Ai-iclone do` in order. Never invoke the Python renderer or GUI helper independently to bypass Preview.
- Follow the live render card. The current card specifies **1920×1080 (1080p), 60 fps**. If the card changes, follow it; never guess a size from an older video.
- Resolve `{VIDEO}` from the active project's `paths.local.json`. Output exactly `{VIDEO}\<story>\<part>.mp4` (for example `1.1.mp4`); inspect the destination before writing. Do not save the final video to the project checkout or an arbitrary folder.
- Complete Preview's `video_check` and verify the exact path, width, height, frame rate, duration, and audio with ffprobe. Treat any mismatch as a failed render and repair through Preview; never move or rename a wrong render to disguise it.
- Output `{VIDEO}\<story>\<N>.mp4`. Copying it to the publish folder in {DRIVE} is the only write allowed there.
- `scripts/ic8_gui.ps1 save/saveas` and `scripts/ic8_save.py` are disabled/removed. Never RFileIO.SaveProject, never RGlobal.RenderAudio. Check the video with ffprobe (60 fps, right length).
