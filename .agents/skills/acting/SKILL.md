---
name: acting
description: Body motion placement and facial expression for iClone characters - which library motion, how slow, blending clip joins, nods, blink, smile/angry/sad expressions. Use when setting a character's motion or mood in a part.
---
# Acting = slow body motion + living face

## Where the motions are ({MOTION} is read only). Body and face are SEPARATE files.
Root `M = {MOTION}\` (find it: `python scripts/paths.py`). Search the acting clips: `python scripts/motion_pool.py find <words>` (index of the whole library; `M\motions.csv` is old and incomplete).
- **Body (.iMotion / .rlMotion)** -> spec `cast.<name>.motion`:
  - Standing idle: `M\โมชั่น\03_CC MixMove_Male\` and `04_CC MixMove_Female\` (Stand00-04).
  - Talking / listening: `M\Studio Mocap - Conversation\`, `M\Motion_-_TalkListen\` (Listener_Agree/Curious/Apologize_F/M, Breathing_F/M .rlMotion - this folder also has face .iTalk: Amused, Comfortable_F...).
  - Emotion gestures: `M\Studio Mocap-Emotes\`, `M\Scared Mocap Animations\`. Lovers/couples: `M\Lovers\Studio Mocap-Lovers\`, `M\คู่รัก\`.
  - Sitting / lying / sleep: `M\SitC01.iMotion`, `SitC02`, `MSitC01`, `M\Have A Rest - Laying Down Animation Pack\`, `M\Sleep Anim Pack iC7.92\`.
  - Thai: `ยืนไหว้`, `นั่งไหว้`, `นั่งไหว้พระ`, `นั่งสมาธิไหว้`, `ปฏิเสธ`, `อุ้มลูก` (.rlMotion in M), `ฟ้อนรำ.fbx`.
  - Daily life: `M\Home_life_Clean_\`, `M\Park Life - MoCap Pack iC7.93\`, `M\Studio Mocap-City Life\`, `M\Shopping_Clean vfxmed\`, `M\ทำงาน\`, `M\ปลูกผัก\`, `M\ขับรถ\`, `M\ขี่ม้า\`, `M\วิ่งหนี\`, `M\ผี\`. Kids: `M\Kids At School vfxmed\`, `M\Baby Motions\`.
  - Walk: `M\Walk.iMotion`, `M\Walk ชาย.iMotion` (root motion - one per shot).
- **Face (.iTalk / .italk)** -> spec `cast.<name>.lookfront`: `true` = `Digital Soul 100+\1.Watch\Look front.iTalk`, or a full PATH to a face clip that fits the line:
  - `M\Digital Soul 100+\<Emotion>\0N_<Emotion>_<Lo|Med|Hi|Max|Short>.italk` for Anger, Disgust, Fear, Happy, Neutral, Sad, Surprise (Lo = subtle - use Lo/Med for folk tales; Max is overacted).
  - Looking: `1.Watch\` (Look front, Look around_Nervous/Pleased/Relax, Look up_Happy/Interested, Size up_...).
  - Thinking: `2.Think\` (Considering_F, Day Dream_F, Planning, Scheming, Absent-minded). Reading: `3.Read\`.
  - Feelings: `4.Feel_Like\1.Pleased`, `2.Excited`, `3.Tender`. Looping versions: `Expression_Loop\<Emotion>\`.
  - Pick per character from the script: e.g. greedy daughter -> `Happy_Lo` while gifts are given, `Disgust_Lo` when disappointed; sad old parents -> `Sad_Lo`/`Sad_Med`.

## Pick motions from the WHOLE library, per line (user 2026-11-22 / 2026-11-23)
The user, angry: one folded-arms clip (Stand03 / StandTKI) came back in almost every part - "ซ้ำๆ ไม่ได้อรรถรส".
The old hand list of 25 clips was the cause. Do this instead, for every part:
1. Add `"mood"` to lines where the feeling is clear: `calm` (default), `sad`, `angry`, `happy`, `fear`. Optional cast `"mood"`, `"sex": "F"|"M"` (else read from the story character's voice/role), `"posture": "sit"`.
2. `Ai-iclone motions` (shows the plan) then `Ai-iclone motions --write`. It scans `{MOTION}` (~600 acting clips out of ~6000: MixMoves Communication 200, Motion_-_TalkListen, Studio Mocap Conversation, MixMove / Mograph Stand*/Sit*, Mocap Online LIFE Convos, City Life Chat, Mixamo talking/idle names) and, for each ~14 s a person is on screen, picks: speaks -> talk clip, someone else speaks -> listen clip, narrator -> idle clip, matching sex, posture and mood; least used in the story first; never a clip another person in this part has; never one already in 2 other parts; folded arms / hands on hips only for `angry` and 1 person per part.
3. Work clips (Brick Laying, Sawing, Market_*, Bench_Sit_Read ...) are kept as they are. Search by hand: `python scripts/motion_pool.py find sad stand F`.
- Folded arms / hands on hips = stubborn, angry, bossy ONLY, max 1 person per part (check FAILs otherwise).
- Anyone on screen > 20 s: list 2-3 DIFFERENT clips in `motions` (check FAILs otherwise). `pose` switches to the next clip at the first camera cut 8-20 s into a clip (the change hides in the cut), max 20 s per clip; a person who leaves the screen and comes back starts on the next clip.

## Body motion (set in the part spec `cast`, applied by `ic8_part.py pose`)
- Library first: standing `Stand00.iMotion` (MixMove Male/Female); Female Stand01 (sometimes Stand00) has a raised-hand gesture, Stand02 = hand on hip, **Stand03/Stand04 are quiet**. Conversation mocap: MixMoves Communication / Studio Mocap Conversation.
- **Speed 0.65-1.0 only (user 2026-11-19):** slower than 0.65 the pose updates ~12x/s and the video judders. Need calm? pick a calmer clip. Too short? list 2-3 clips (or the same one) - `ic8_pose_place.py` puts them back to back (never overlapping, user 2026-11-21) with a 2 s transition at the start of each next clip.
- **No two characters on the same clip + speed** (they move in sync): vary motion / speed / start offset.
- Chained clips must crossfade (X in the timeline): run `scripts/ic8_blend_clips.py` (face 8.58 s, body 3 s) after the cast is built.
- Walk clips carry ROOT motion that resets at each clip boundary: never chain Walk clips; one walk per shot, match on action.
- Stage from the SCRIPT (who sits/stands/where), not from the cast list. Sitting = AccuPOSE in the GUI (see `pose-bones`).
- Measure speed after a render: `python -I tools/motion_meter.py <mp4> <shot starts...>` (target ~30 px/s at 480p).

## Face
- Every character: `lookfront: true` (face clip `Digital Soul 100+\1.Watch\Look front.iTalk` = small natural head motion) and auto blink `GetFaceComponent().SetAutoBlinkName('Normal')`.
- Listeners `lookat` the speaker. Heads never still: slow nods with different period/phase per person (`scripts/ic8_head_nod.py`, Head_Turn_Down/Up, 4.5-7.5 s).
- Expressions = keys over the Look-front clip: `fc.AddExpressionKeys(RTime, [names], [weights], RTime transition)` inside BeginKeyEditing/EndKeyEditing. In the spec: `"face": {"Mouth_Smile_L": 0.3}`.
  - Happy / gentle smile: `scripts/ic8_smile.py` (Mouth_Corner_Up, Mouth_Corner_Pull, Eye_Cheek_Raise, Brow_Raise_Outer).
  - Stern / angry: `scripts/ic8_angry.py` (Brow_Down, Eye_Squint_Inner, Eye_Lid_Press, Nose_Wrinkle, Mouth_Corner_Depress, Mouth_Corner_Down, Jaw_Clench L/R). Ramp up toward the key moment.
  - Names like Brow_Drop / Mouth_Frown do NOT exist. List real ones: `fc.GetExpressionNames(group)` for Brows, Cheeks, MouthBase, MouthMove, EyeLid, Nose, Jaw.
- Mood must read in close-ups: check face stills (skill `review-stills`); 3/4-front angles, short profile shots.
- Mouths: only speakers, only in their line windows (skill `lip-sync`).
- A motion that the library truly lacks -> propose Motion AI (skill `motion-ai`), wait for yes.

## AccuPOSE-first — mandatory for static contact/holding (2026-11-27)
Before choosing any body motion, consult docs/accupose_presets.md (420 poses) and docs/motion_catalog.md. For static holding, handing, seated or supported/contact poses, choose a suitable existing AccuPOSE preset first (e.g. Basic Stand for upright trophy holding), then adapt wrists, elbows and fingers. Do not layer an incompatible idle clip on top of the pose. Preserve the base pose; use subtle head motion and blink. Inspect actual contact through the shot. Gesture .iHand library: resolve the installed Reallusion Templates/Animation/Gesture folder on this PC; inspect suitable hand presets, not just filenames. For complex existing motion, inspect DataLink connection and linked avatar identity; send the current pose/motion to Blender, adjust the existing animation and send back only the intended actor/range. DataLink roundtrip is not yet verified in this story. Never invoke RFileIO.LoadFile on .rlDikPreset (known crash); use the AccuPOSE panel. Do not render before approval. If a relevant reference already exists, read and reuse it before writing a new helper. Do not treat this rule as evidence a pose was applied.


## Current integrated runtime
Follow docs/CINEMATIC_SLEEP.md and live Preview cards. New camera and evidence rules supersede old 80/100-only and fixed-cut rules. Preserve sound and actual manual File-menu save without reopen. Normal and Sleep share QA; Sleep requires explicit scoped activation. Do not bypass real checks.


## Current save/render rule (2026-11-27)
Switch -> frame zero -> native File > Save Project -> Render the current open scene. Do not reopen merely to test saving. If save cannot be verified and the user authorizes live rendering, use Ai-iclone do --render-live at Ready, then Ai-iclone do to Render. The save remains pending; verify video separately. Preserve the live scene and do not advance to another part until saved. Never use scripted project save or mark a failed save complete. This supersedes earlier mandatory reopen instructions.
