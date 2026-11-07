# User's rules (add every new instruction here immediately)

## Working style
- Do one step at a time as the user says. Don't render until told to.
- Every instruction the user gives → write it here right away.
- Script everything you can (watcher). Avoid screenshots/mouse; they waste credits.
- **Save often** to `E:\FileSave\N.iProject` after each big step (iClone can crash).
- Ask before overwriting a file that already exists from another story.

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

## Placement
- The user drops a marker block where things should go. Read its position by script, place around it,
  record it in `scene_anchors.md`, then delete the marker (or keep it hidden, but never put audio on it).

## Render
- Script render: `ic8_render2.py` (1920×1080, **60 fps**), then trim with ffmpeg to audio + 5 s, output `E:\Video\N.mp4`.
