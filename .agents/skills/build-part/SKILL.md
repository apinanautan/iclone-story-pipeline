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
- After fixing a number in the spec: `python scripts/ic8_part.py <spec> <step> --from`.
- `cams` adds a face light per avatar. If the log says `WARNING NO FACE LIGHT`, the scene has no point/spot light: tell the user; do not fake it by cranking the directional light.
- Directional light colour uses normalized RRgb(1.0,0.92,0.84); the 255 scale washes out.
- Never use your own stage/camera scripts. Never save by script.
Next: `review-stills`.
