---
name: review-stills
description: Make and check the camera stills (contact sheet) of a part before the user sees anything. Mandatory after every cams run.
---
# Review stills (mandatory before the user sees anything)

## 1. Make them ONLY with `ic8_part.py <spec> cams`
- Never with your own stage/camera/trial script (e.g. `ic8_trial_*_stage.py`) or a hand-written RenderImage job.
  Stills from such scripts skip `check` (lens 80/100, chest-up, no side-by-side two-shot) and show cameras the spec never had
  (user 2026-11-20: the กรงกตัญญู trial sheet `docs/t1_cams_p1.jpg` = full bodies side by side, made by `ic8_trial_krong_stage.py`).
- What `cams` captures, per shot, from THAT shot's camera (Cam_A / Cam_B, same as the Switcher):
  ~1 still per second, 3-8 per shot, from shot start+0.2 s to end-0.2 s -> `ic8_jobs/cam_NN_KK_TTT.Ts.png`.
  Before each still: SetCurrentCamera + settle (Qt events + ForceViewportUpdate x2), then the camera position is compared
  with the planned one (`cams.log.txt` line `still S03 ... err=0.4cm`; > 3 cm = `STILL_MISMATCH` = cams FAILS).
- Then `scripts/still_check.py` compares neighbouring stills of each shot (the camera moves only 5-20 cm, so framing must
  barely change). JUMP / FLIP (A-B-A) is a QA alert, not proof of a bad capture or jumping real camera; compare camera keys/log and actor motion. cams FAILS pending review. Never show such stills; re-run `cams --from`.
- Pages: `ic8_jobs/part_cams.jpg` (+ `_p2.jpg`...), 1920x1080, 3x3 tiles 640x360, yellow borders, label `S03-02  12.4s` = shot-still-time,
  each shot starts a new row. Rebuild by hand only if needed:
  `python scripts/contact_sheet.py "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\cam_*.png" "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\part_cams.jpg"`

Before building the sheet, still_check.py must verify exactly the expected number of files in each shot. Empty/missing/unreadable images are FAIL, even if image-shift metrics would otherwise pass. The camera capture loop must abort before RenderImage when its actual position differs by more than 3 cm or the active camera is wrong. A PASS on camera/image consistency does not mean the shot framing or acting passes.

## 2. Look at EVERY page, row by row (a row = one shot moving in time)
Fix in the spec, then `cams --from`, for any shot with:
- full body / knees / legs / mattress; side-by-side two-shot (use OTS or singles)
- back of head or profile only, hair over the eyes, unreadable expression, dark face
- head cut at the top, a person sliced by the frame edge, blocked view, big empty wall, off-centre face
- EMPTY BACKGROUND (open ground, bare sky, unbuilt scene edge, glitchy/missing models)
- during a line: the speaker's face is not the subject
- two shots in a row that look the same (same angle, only nearer/farther)
- seated/leaning people: also a side + back still at mid-time (body through chair, floating, hands inside the desk)
Write the shot list you SEE (not what you planned): `S01 0-7s Cam_A MCU สมจิต 3/4 ซ้าย พูด`. If it differs from the plan, the stills win: fix.

## 3. Send and STOP
Send the page images to the user with one Thai line per shot. **STOP.** No lip-sync, save or render until the user answers.
