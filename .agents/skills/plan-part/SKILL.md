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

## How to choose shots (think like an editor, user 2026-11-19)
Start from the timed transcript (`brief` prints it). For each line ask: who speaks, or for narration, who is it ABOUT?
- Speaker on screen while they talk. Narration -> the person it describes ("about"); both -> one shot holding both.
- Same angle twice in a row = one shot with a slow zoom, not a cut. A return to a wide must come from a new angle.
- **The part END:** after the last line, do NOT cut to someone new. Hold the last line's subject to the end of the part
- **Last shot must be 6 s or longer.** If the last-mentioned person's shot (from its cut to the part end) would be under 6 s, do not cut to them at all: delete that shot and stretch the previous shot to the part end. `ic8_part.py check` fails otherwise.
  (the tail is silence; a 2-3 s new shot right before the next part looks like a jump when parts are joined).
  Then look at the NEXT part's first line: the next part should open on a different angle/person, not the same shot.
- No shot under ~3 s unless it is a quick reaction the story needs.
- Close-ups: aim at eye height, full head with a little room above (check every still).

## Current candidate workflow (1.7.8)
Read docs/CINEMATIC_SLEEP.md and current Preview cards. Scene-aware replan, prop review, editorial/final review use identical standards in BOTH modes. Old 80/100-only and five-second-cut rules are superseded. Sleep changes approval and handoff only. Use Ai-iclone repair <step> and do, not direct ic8_part calls. Motion Analyzer requires verified transfer and explicit bone map; no invented evidence. Do not claim live pass before verification.
