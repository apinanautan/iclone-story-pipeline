---
name: acting
description: Body motion placement and facial expression for iClone characters - which library motion, how slow, blending clip joins, nods, blink, smile/angry/sad expressions. Use when setting a character's motion or mood in a part.
---
# Acting = slow body motion + living face

## Body motion (set in the part spec `cast`, applied by `ic8_part.py pose`)
- Library first: standing `Stand00.iMotion` (MixMove Male/Female); Female Stand01 (sometimes Stand00) has a raised-hand gesture, Stand02 = hand on hip, **Stand03/Stand04 are quiet**. Conversation mocap: MixMoves Communication / Studio Mocap Conversation.
- **SLOW is mandatory:** ONE clip stretched over its segment, `speed` 0.15-0.30 (talkers <= 0.30, listeners ~0.15). Never loop short clips at 0.7-1.0.
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
