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

## 4. cam_check (mandatory step after cams, user 2026-11-23)
`ic8_part.py <spec> cam_check` (or `Ai-iclone do`) puts ALL shots in ONE image `ic8_jobs/part_cams_all.jpg` and writes
`progress/<story>_<N>_camcheck.json`. Open the image, then per shot fill `see` (what is REALLY in the frame) and true/false for
subject_face, framing, clean, differs. Any false -> write `fix`, change the spec, `cams --shot <N>`, run cam_check again.
The step does not pass until every shot is filled and true. Never copy the plan into `see`.

## Reusable production rules

- When cutting between shots of the same person or group, change the subject size visibly in the frame. Choose lens, camera distance and composition together, then compare the actual stills side by side. A reverse angle at the same scale does not satisfy this rule. Matching shot sizes are allowed when focus cuts between different people.
- For a bright lightweight folk-tale interior, use modular floor and wall pieces with a small window opening, soft daylight, and restrained background blur. Keep the performance and faces clear. Use generated geometry for structure and reserve image-to-3D for small optional props. Check dimensions, apertures, materials and performance in the target editor before accepting generated assets.
- Save iClone projects only through the visible File > Save Project or File > Save Project As menu. Never use a script, watcher, CLI or keyboard shortcut to save. Reopen through File > Open to verify the saved project before final delivery.
- When the user adds a reusable production rule, update the installed skill and the corresponding skill or rules in the canonical GitHub repository. Publish the scoped change and verify it appears upstream. Keep story assets, media, local paths and progress out of the commit.

## Project Sound / Preview — 2026-11-27
- Cast → Sound → Pose → Lip → Cams. Import Project Sound only once per loaded project; inspect the clip name and full part range at frame 0. Repair Pose/Motion/face/camera or add cast without importing it again. Re-import only when a different project/audio is loaded or sound is confirmed missing/wrong. Lip Sync uses the original full part audio per speaker and retains the Project Sound track.
- Save/reopen only via the visible iClone File menu. No automatic script save, and no render before approval.
- For the locally installed Chrome Preview Bridge and Goal Tracker, read docs/CHROME_PREVIEW_GUIDE.md; check actual installation and exact authorized conversation before use.
