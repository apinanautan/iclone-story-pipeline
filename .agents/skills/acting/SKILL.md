---
name: acting
description: Body motion placement and facial expression for iClone characters - which library motion, how slow, blending clip joins, nods, blink, smile/angry/sad expressions. Use when setting a character's motion or mood in a part.
---
# Acting = slow body motion + living face

## Where the motions are ({MOTION} is read only). Body and face are SEPARATE files.
Root `M = {MOTION}\` (find it: `python scripts/paths.py`). Full list of 1570 body motions: `M\motions.csv` (Name,Type,Folder,FullPath) - search it by keyword instead of walking folders.
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
