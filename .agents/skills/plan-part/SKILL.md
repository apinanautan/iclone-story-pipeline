---
name: plan-part
description: Write the part spec parts/<story>_<N>.json (lines, cast, shots) and make `python scripts/ic8_part.py <spec> check` pass. Use before any iClone work on a part.
---
# Plan a part = write the spec, pass the check

1. Copy `parts/_example.json` -> `parts/<story>_<N>.json`. Full format: docstring at the top of `scripts/ic8_part.py`.
2. `wav` = the cut wav from `cut-audio`. The last shot must end at the wav length.
3. `lines`: who speaks when, from the cut json (`"who": "บรรยาย"` for narration).
4. `cast`: a spot from `stories/<story>.json` or pos/yaw; library motions (`.iMotion`), `lookfront`, `lookat` (listeners look at the speaker).
5. `shots` - camera rules (the check enforces them):
   - Character shots: focal **80 or 100** only, chest-up: visible height = distance x 24 / focal <= **100 cm** (<= 333 cm away at 80 mm, <= 416 cm at 100 mm). **No full bodies, no knees.**
   - At most ONE `"wide": true` view shot per part, and it must NOT aim at the cast (scenery / house only).
   - About 5 s per shot, cut in pauses, alternate angles. Two people -> OTS or single close-ups, not side-by-side two-shots.
   - Aim so the BACKGROUND has trees / houses / props - never open empty ground, bare sky or the unbuilt edge of the scene.
   - Same person twice in a row -> change size AND angle.
6. `python scripts/ic8_part.py parts/<spec>.json audio` gives silences for cut points.
7. `python scripts/ic8_part.py parts/<spec>.json check` - fix every FAIL. WARN "not approved" means: show the user stills first.
