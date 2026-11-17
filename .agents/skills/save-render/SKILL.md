---
name: save-render
description: Save the part through the GUI, prove it reopens, and render 1080p60 with the Switch camera and clean audio. Render ONLY after the user explicitly approves.
---
# Save + render

Save (safe any time):
```
python scripts/ic8_part.py parts/<spec>.json ready     # Switch, playhead 0, range, GUI save, reopen -> user presses Play
```
Render - **only when the user says ผ่าน / เรนเดอร์**:
```
python scripts/ic8_part.py parts/<spec>.json render --approved
```
- Uses `ic8_gui.ps1 render`: viewport camera = Switch, 1080p60, clean wav muxed with ffmpeg, checks fps/length/volume, one frame per shot.
- Output `{VIDEO}\<story>\<N>.mp4`. Copying it to the publish folder in {DRIVE} is the only write allowed there.
- Never RFileIO.SaveProject, never RGlobal.RenderAudio. Check the file with ffprobe (60 fps, right length).
