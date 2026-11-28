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

## 2026-11-27 — Mandatory shot-size rhythm (user)
- Plan the entire shot sequence by visible framing and narrative function, not lens or left/right angle alone. For each shot record subject, size (contextual chest-up / MCU / CU / OTS / insert / establishing), purpose, and the visible difference from adjacent shots. 80/100 mm is a lens constraint, NOT a shot-size category. Change distance and target to vary the actual composition while keeping established framing constraints.
- FAIL a sequence dominated by same-scale face-only shots (including 80 mm left, 80 mm right, other faces at the same size). Small angle shifts, switching Camera_A/B, or changing 80 to 100 without a visible size change do not count as diversity. Same-subject cuts require visibly different scale AND meaningful angle; matching reverse shots of different speakers are allowed for a motivated dialogue pair, not as the entire sequence.
- Use a wider contextual chest-up/OTS composition to establish relationship or action, MCU for normal storytelling, CU for emotional emphasis, and a relevant insert/reaction when the script and existing framing rules permit. Do not force a wide/full-body shot, insert, or arbitrary cut. Preserve screen direction, speaker coverage, continuity and slow motion. A close-up is a storytelling accent, not the default for every shot.
- At cam_check inspect the full actual contact sheet as a sequence, not isolated thumbnails. Label each shot's actual framing and compare the visible head/body size, composition and purpose. If the sequence reads as repeated faces with minor left/right changes, mark the affected differs=false and describe the framing repair; do not pass until revised fresh images visibly solve it. Compare previous part's last shot and current first shot. In future Sleep Mode, repeat this review independently as director/editor before render; score cannot override a repetitive sequence. This is a visual QA rule, not a demand to alternate focal lengths.


## Current integrated runtime
Follow docs/CINEMATIC_SLEEP.md and live Preview cards. New camera and evidence rules supersede old 80/100-only and fixed-cut rules. Preserve sound and actual manual File-menu save without reopen. Normal and Sleep share QA; Sleep requires explicit scoped activation. Do not bypass real checks.


## Current save/render rule (2026-11-27)
Switch -> frame zero -> native File > Save Project -> Render the current open scene. Do not reopen merely to test saving. If save cannot be verified and the user authorizes live rendering, use Ai-iclone do --render-live at Ready, then Ai-iclone do to Render. The save remains pending; verify video separately. Preserve the live scene and do not advance to another part until saved. Never use scripted project save or mark a failed save complete. This supersedes earlier mandatory reopen instructions.
