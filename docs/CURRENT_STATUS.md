> ⚠ ไฟล์นี้เก่า (2026-11-11) สถานะปัจจุบันอยู่ที่ `docs/WHAT_WORKS.md`

# CURRENT PROJECT STATUS — Clone Story Pipeline

Updated: 2026-11-11T03:20:13+07:00
Machine: DESKTOP-F1PJT4S
Current story: ดวงเมียน้อย
Current production target: Part 3 rebuilt as event clips (3.1 -> 3.2 -> 3.3 -> optional 3.4), then assembled into one Part 3 master.

## Overall status

**IN PROGRESS — event-clip rebuild. NOT READY FOR FINAL RENDER.**

The previous long-timeline Part 3 approach is rejected by the user and superseded.
Canonical workflow:
- docs/event_clip_workflow.md
- docs/part3_event_clip_plan.md
- data/part3_event_clips.json

The rejected structure was one ~72-second timeline containing dialogue, leaving, reactions and walk-home movement. Do not continue that structure as the final production method.

## Live iClone state

Verified at update time:
- iClone is running and responsive.
- Main window: iClone 8 - 3.1.iProject
- Current event project on disk:
  {SAVE}\3.1.iProject
- File size: 2,379,053,085 bytes
- Saved: 2026-11-11 03:13:05
- No pending watcher queue jobs at the earlier live status check.
- Fresh inspect_scene and inspect_timeline jobs completed successfully.

### Current scene inventory
- Avatars: 5 — สุนีย์, ปรีชา, เมียน้อยปรีชา, นาวีวัยประถม, นิวัตน์ป2
- Props: 83
- Cameras: 1 (Camera)
- Camera transform keys: 18
- Switch-camera keys: 0
- Lights: 4

## Event 3.1 — CURRENT WORK

**Status: IN_PROGRESS / NOT YET A CLEAN EVENT-ONLY PROJECT / NOT READY TO CALL COMPLETE.**

Verified:
- 3.1.iProject exists and is currently open in iClone.
- Father lip-sync exists.
- Latest father viseme cleanup: 1 clip, 225 keys, active range about 15.09–40.09 s.
- Camera was cleaned to 18 transform keys.
- Camera transitions were changed to step cuts rather than unwanted interpolation.
- Observed camera cut positions: about 7.05, 16.05, 26.35, 28.90, 31.40, 36.60, 38.30, 40.40 s.
- Focal length verified at 100 mm except an 80 mm insert around 36.6–38.3 s.
- Reaction-camera and mother facial reaction work exists from prior passes.

### Critical problem still present
3.1.iProject still inherits animation/timeline material from the old long Part 3 build.

Fresh timeline inspection:
- timeline end: **64.15 s**
- face clips on all five avatars still report **72.4 s** length
- inherited body clip counts:
  - สุนีย์: 6
  - ปรีชา: 6
  - เมียน้อยปรีชา: 6
  - นาวีวัยประถม: 7
  - นิวัตน์ป2: 4

Therefore 3.1 is **not yet isolated to only the standing-conversation event**. It is not complete merely because the file is named 3.1.iProject.

### Still unverified before 3.1 can pass
- Exact event end boundary from real story action/audio.
- Project Sound Track presence/audibility for the 3.1 event.
- Removal/trimming of inherited post-3.1 body/face motion.
- Continuous moving-video QA for the whole 3.1 event.
- Speaker mouth timing and listener reactions in moving playback, not only stills/logs.
- First/last frame of the event.
- 10-pass human-motion/editorial QA.
- Current event-specific preview video.

## Event 3.2 — father + mistress leave

**Status: NOT STARTED AS A SEPARATE EVENT PROJECT.**
No 3.2.iProject exists.

## Event 3.3 — mother + children aftermath/comfort

**Status: NOT STARTED AS A SEPARATE EVENT PROJECT.**
No 3.3.iProject exists.

## Event 3.4 — mother leads children home

**Status: NOT STARTED / CONDITIONAL.**
No 3.4.iProject exists.
Create only if walk-home is confirmed as a distinct movement event after 3.3.

## Historical / superseded Part 3 files

Exist but are NOT current desired event-clip deliverables:
- 3.iProject — original historical Part 3
- 3_rebuild_v1.iProject — long-timeline rebuild attempt
- 3_rebuild_v2.iProject — long-timeline rebuild attempt
- 3_master_full_20261111.iProject — full-timeline master/reference, not final event workflow
- ดวงเมียน้อย_3_rebuild_v2_preview480.mp4 — previous long-timeline preview; user rejected it as still broken / not following event-clip instruction

An old {VIDEO}\3.1.mp4 also exists, dated 2026-10-31. It predates the current event-clip rebuild and must NOT be treated as the current 3.1 review output.

## Current event project existence

- 3.1.iProject: EXISTS
- 3.2.iProject: NOT CREATED
- 3.3.iProject: NOT CREATED
- 3.4.iProject: NOT CREATED

## Required next production action

Do NOT start 3.2 yet.

First make 3.1 a true event-only project:
1. Determine real end of standing-conversation event from script/audio/action.
2. Trim/set 3.1 timeline to that event only.
3. Remove or trim inherited post-event body/face animation.
4. Verify Project Sound Track and lip-sync for only this event.
5. Inspect facial reactions/eyelines and camera coverage as moving video.
6. Run 10-pass QA for 3.1.
7. Save cleaned 3.1.iProject.
8. Ask user whether to inspect in iClone or render 480p event preview unless render permission already exists.
9. If rendered, review actual 3.1_preview480.mp4.
10. Only after 3.1 passes, begin a new 3.2.iProject.

## Non-negotiable interpretation

- One numbered clip = one complete dramatic event.
- Camera change != new numbered clip.
- Reaction inside same event != new numbered clip.
- Speaker change inside same conversation != new numbered clip.
- Main event/action change = new numbered clip.
- Audio timestamps are sync information, not event boundaries.
- Each event is completed/reviewed before the next event is built.

## 3.1 CAMERA DESIGN UPDATE — 2026-11-11

**Dedicated multi-camera redesign saved and static-frame QA passed.**

Current camera project:
{SAVE}\3.1_multicam_v3.iProject
Size: 2,379,078,106 bytes.

Camera objects (6):
- Cam_Mom_CU — 100mm
- Cam_Dad_CU — 100mm
- Cam_Dad_Mistress — 90mm
- Cam_Kids — 70mm, two-child reaction
- Cam_OTS_MomToDad — 75mm, mother shoulder foreground
- Cam_Mom_Profile — 85mm, clean mother profile reaction

Switcher cuts (10):
0.00 Mom CU → 7.05 Dad+Mistress → 15.05 Dad CU → 18.70 Mom Profile → 21.70 Kids → 24.10 OTS Mom-to-Dad → 28.80 Mom CU → 31.40 Dad+Mistress → 36.60 Dad CU → 40.15 Mom CU.

This supersedes the single-camera hard-step/teleport camera approach for 3.1.
Static QA stills all rendered successfully. Moving playback/audio/lip-sync/motion QA is still pending, so 3.1 as a whole is not yet marked complete. No video render has been performed.

Camera manifest: data/part3_3.1_camera_plan.json.

## 3.1 GAZE / OCCLUSION UPDATE — 2026-11-11

Saved project:
{SAVE}\3.1_gaze_multicam_v4.iProject
Size: 2,379,096,691 bytes. Timeline end: 43.00 s.

Actual iClone Look At was added to Head-bone targets:
- สุนีย์ -> ปรีชา (1.00)
- ปรีชา -> สุนีย์ (1.00)
- เมียน้อยปรีชา -> สุนีย์ (0.85)
- นาวีวัยประถม -> ปรีชา (0.95)
- นิวัตน์ป2 -> ปรีชา (0.95)

Camera layout was re-designed AFTER gaze was locked. The old Cam_OTS_MomToDad was removed because the mother's shirt/shoulder could move into and block the father's face. It is replaced with Cam_Dad_3Q_Mid, a clean gaze-aware 3/4 shot with no foreground occluder.

Dynamic occlusion QA sampled multiple frames throughout risky shots:
- Dad+mistress depth: face clear across sampled motion
- Kids reaction: both faces readable across sampled motion
- Dad mid 24.1-28.8: no foreground obstruction
- Mom/Dad close cameras: gaze correct and faces readable across sampled motion

Camera set now:
Cam_Mom_CU, Cam_Dad_CU, Cam_Dad_Mistress, Cam_Kids, Cam_Dad_3Q_Mid, Cam_Mom_Profile.

Switcher remains 10 cuts at:
0.00, 7.05, 15.05, 18.70, 21.70, 24.10, 28.80, 31.40, 36.60, 40.15 s.

This passes gaze-aware static framing and sampled moving-occlusion QA. Full playback/audio/lip-sync/10-pass event QA is still pending. No video render was performed.

## 3.1 FINAL RENDER UPDATE — 2026-11-11

User accepted the gaze-aware multi-camera camera version and ordered direct 1080p render without further QA.

Canonical project:
{SAVE}\3.1.iProject

Rendered video:
{VIDEO}\3.1.mp4

Render settings: 1920x1080, 30fps, MP4, audio export enabled, 0–43 s event range.
Render job completed successfully and output file exists (about 24.88 MB).

Cleanup completed before final render:
- deleted 3.1_camera_v2.iProject
- deleted 3.1_multicam_v2.iProject
- deleted 3.1_multicam_v3.iProject
- deleted 3.1_gaze_multicam_v4.iProject after saving canonical 3.1.iProject
- deleted old 3.1 video preview files
- deleted generated p31 QA preview still images
- kept only canonical 3.1.iProject for this event

Per explicit user instruction, no additional visual/audio QA was performed on the final 1080p file after render.

## LATEST PART 3 AUDIO / FRAME CONTINUITY CORRECTION — 2026-11-11

**Authoritative correction to stale status sections above.**

- Original Part 3 WAV is 67.40s, 48kHz, stereo, 3,235,200 sample frames; never split its audio for the final master.
- Target master video is 2022 frames at 30fps, exactly 67.40s. Visual clips only are joined; their individual audio tracks are discarded and original WAV is laid once over full master.
- Existing {VIDEO}\3.1.mp4 is 2173 video frames / 72.433333s (NOT the intended 1290 frames / 43s). Preserve it, but select only source frames 0..1289 when assembling the master.
- Current approved visual 3.1 time window [0,1290) at 30fps.
- Source narration 43.00–52.94s was previously accidentally omitted in the proposed 3.2 walk-only version. This must never be omitted.
- Corrected working event 3.2 now covers global 43.00–59.133s [1290,1774), starting with children's expectation, mother's acceptance, father's response, then father+mistress walking near 52.94s.
- Corrected iClone WIP project saved at {SAVE}\3.2_continuity_wip.iProject. Seven dedicated cameras and seven Switcher keys. **NOT yet approved or rendered.**
- Full 30fps / every-frame non-video still QA of all 484 frames of event 3.2 is being performed; 30 consecutive frames per internal storyboard sheet.
- Candidate 3.3 [1774,1910), 3.4 [1910,2022); no new render authorized.
- Main references: docs/part3_audio_continuity.md, data/part3_frame_edl.json, scripts/part3_continuity_guard.py, scripts/ic8_dense_frame_review.py.

Current 3.2 WIP must be visually rechecked; not call it complete and do not render unless the user specifically approves 3.2.

## 3.2 SAVED FOR REVIEW — 2026-11-11 06:10

The current 3.2 iClone project is SAVED and OPEN:
{SAVE}\3.2.iProject
File size 2,379,177,223 bytes. Scene responds.
Global window 43.000–59.133 seconds; 7 independent cameras / 7 Switcher keys.
Father–mistress spatial correction measured head separation approximately 40–58 cm in reviewed walk samples (was 65–104 cm). Body walk clips remain intact. Cam32_Walk / Cam32_Exit use tracking movement to hold both characters, and 6 representative final stills were reviewed.
Older 3.2 versions stored under {SAVE}\_archive.
NOT rendered, explicitly pending user's iClone playback approval. Original 67.40s WAV source remains the master audio for complete Part 3.
## ACTION-SPLIT CORRECTION 3.2 / 3.3 — 2026-11-11

LATEST and authoritative; earlier "3.2 43–59" plan is superseded.
- 3.2.iProject: global [43.000,54.200) = frame [1290,1626), static looking / response / decision, ends on mother reaction hiding the start of departure. Saved successfully, 2,379,151,975 bytes.
- 3.3.iProject: global [54.200,59.1333) = frame [1626,1774), WALK ONLY. Both dad and mistress head positions changed by ~29.4cm/~32.1cm in first 0.4s. Two dedicated moving cameras track both; no static reaction interruption in the walk. Saved successfully, 2,379,153,559 bytes.
- Legacy 3.2 mixed look→turn→walk project moved into _archive, preserved only for recovery.
- Existing 3.1 approved MP4 remains untouched, but its excessive 72.433s encoded length still must be frame-trimmed to intended 43s during final master assembly.
- 3.4 aftermath and 3.5 walk-home are prospective next events (previous numbers shifted one position).
- NO new 1080p video rendered. Await event-specific user preview approval. Full original 67.40s WAV is required as ONE uninterrupted master soundtrack.
- Master draft EDL: data/part3_frame_edl.json.

## PART 3 ALL FIVE ACTION PROJECTS SAVED — 2026-11-11

Latest authoritative checkpoint. Earlier 3.2-as-mixed-look-turn-walk and 3.4/3.5 pending plans are superseded.

Action EDL at 30fps:
- 3.1 [0,1290): standing dialogue, saved and previously user-approved video.
- 3.2 [1290,1626): standing decision / reaction; saved, unrendered.
- 3.3 [1626,1774): father and mistress walk starting from first frame; saved, unrendered.
- 3.4 [1774,1910): mother tears / actual child-hug mocap, two cameras; saved, unrendered.
- 3.5 [1910,2022): mother and both children walk starting first frame; saved, unrendered.

All iProjects are saved in {SAVE}/3.1.iProject ... 3.5.iProject.
3.4 used Hug Kid 01_M retargeted to mother and Hug Kid 01_K on first child; second child repositioned alongside. Camera cut at 62.30s avoids cropped mother face. Real textures verified after iClone completed async streaming.
3.5 walk: within first 0.4s actual travel 33.90cm,31.43cm,20.55cm. Camera tracks group throughout and final camera holds last 0.15s to avoid wall. Verified final stills 67.26–67.40 all good.

Original audio is single 67.40s WAV source, 3,235,200 sample frames @48kHz. Final video target 2022 visual frames @30fps, no gap/overlap; video from event clips only, original WAV once as master audio. Existing 3.1.mp4 has excess tail; select first 1290 frames during master assembly. No 3.2–3.5 video renders or master assembly completed because event-specific user approval is not recorded. Never claim final Part 3 MP4 complete.
Canonical frame plan: data/part3_frame_edl.json.

**STALE VIDEO 3.MP4 CAUTION — 2026-11-11:** {VIDEO}/3.mp4 is an OLD unrelated/incomplete render: ffprobe says 77.824 seconds @60fps (4669 video frames, 32kHz AAC). It is NOT the 67.40s / 30fps Part3 master. Do not confuse file existence with finished current part. 3.2–3.5 event videos are still missing awaiting user review/render approval.

## LATEST PART 4.1+4.2 VERIFIED UPDATE — 2026-11-11

This supersedes stale Part 3-only overall/current status above.

- iClone is open at iClone 8 - 4.1.iProject and responsive.
- Current file {SAVE}/4.1.iProject, 1,775,772,305 bytes, saved 2026-11-11 18:22:24.
- 4.1 + 4.2 are intentionally ONE factory working event. Local source audio 0.0–30.3s, iClone working tail through 35.3s. 4.2 corresponds to 15.3–30.3s and should not become a duplicate iProject.
- Read-only live scene/timeline succeeded: real Sunee red-floral blouse, hidden placeholder Sunee, 28 props including bowls, 2 cameras Cam41_A/B, 6 Switcher keys (0,6,11.5,17.5,23.5,29s), 4 lights, 60fps and 35.3s timeline end.
- 18 actual iClone sample stills of 4.2 captured at 15.3–30.2s; chronological contact sheet checked, calm working hands and bowl/counter visible. QA report docs/part4_2_qa_20261111.md.
- Project Sound row visible but exact current WAV clip start/name was not independently read from GUI; old worklog records Part4 WAV imported at frame 0.
- NO new video rendered or authorized, and 4.1 project was not altered during this read-only 4.2 QA.
- NEXT unfinished independent action 4.3: Sunee worried about two children and school costs; final Sunee spoken phrase needs real lip-sync.
- Important Part3.4 correction still outstanding: latest user wants camera-suggested static comfort/fake hug with slight head motion, no actual elaborate hug mocap or Look At. Old project is not approved under the latest rule.
