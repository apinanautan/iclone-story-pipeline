---
name: review-stills
description: Check every shot with start/mid/end stills combined into one contact sheet, fix bad framing, send the sheet to the user and stop. Use after poses and after every camera pass.
---
# Review stills (mandatory before the user sees anything)

1. Stills come from the `cams` step (`ic8_jobs/cam_*.png`). Combine them:
   `python scripts/contact_sheet.py "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\cam_*.png" "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\<story>_<N>_sheet.jpg"`
2. LOOK at the sheet. Fix (in the spec, then `cams --from`) any shot with:
   full body / knees / legs, dark face, back of head only, blocked view, big empty wall, off-centre face,
   two shots in a row that look the same, side-by-side two-shot.
3. Re-make the sheet until clean. Send it to the user (the image) with one Thai line per shot.
4. **STOP.** No lip-sync, save or render until the user answers.
