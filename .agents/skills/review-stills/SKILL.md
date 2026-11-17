---
name: review-stills
description: Check every shot with start/mid/end stills combined into one contact sheet, fix bad framing, send the sheet to the user and stop. Use after poses and after every camera pass.
---
# Review stills (mandatory before the user sees anything)

1. Standard: ~1 still per second per shot (3-8 per shot), made by the `cams` step (`ic8_jobs/cam_NN_KK_TTT.Ts.png`) and already combined into `ic8_jobs/part_cams.jpg` (+ `_p2.jpg`...): 1920x1080 pages of 3x3 tiles (640x360), yellow borders, labels `S03-02  12.4s` = shot-frame-time; each shot starts a new row. Zoom/crop a tile when unsure. To rebuild by hand:
   `python scripts/contact_sheet.py "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\cam_*.png" "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\<story>_<N>_sheet.jpg"`
2. LOOK at every page, left to right per row (= the motion through the shot). Fix (in the spec, then `cams --from`) any shot with:
   full body / knees / legs, EMPTY BACKGROUND (open ground, bare sky, unbuilt scene edge, glitchy/missing models - the background must show trees, houses, fences or props), dark face, back of head only, blocked view, big empty wall, off-centre face,
   two shots in a row that look the same, side-by-side two-shot.
3. Re-make the sheet until clean. Send it to the user (the image) with one Thai line per shot.
4. **STOP.** No lip-sync, save or render until the user answers.
