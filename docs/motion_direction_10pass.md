# Motion Direction: 10-Pass Human Performance and Editorial QA
Updated 2026-11-10. Applies to iClone 8 / Duang Mianoi and later productions.

## Principle
The user means flaws in acting, animation and editorial continuity, NOT software errors.
Direct action in dramatic beats: thought/eyeline -> anticipation -> weight transfer/pivot -> first step -> travel -> reaction -> resolution.
Do NOT force standing, turning, walking and exit into a single long wide shot. Use MCU/CU, three-quarter angles, OTS, cutaways and reaction shots as editorial coverage.
Cutting into three shots is GOOD when it serves drama and hides an unnatural transition, but do NOT simply split source motion into three disconnected clips. Prefer a continuous character animation in iClone while cutting between camera shots. If separate takes/clips are necessary, match root world position, yaw, speed, foot phase, pose, eyeline, screen direction and time. Inspect overlaps and foot sliding.
Focal length 80/100 mm does not guarantee a close-up: subject-to-camera distance and frame composition must also be verified.
Avoid an overcut sequence; every cut must advance a beat or solve a real editorial need.

## 10 rounds: detect -> locate time -> diagnose -> repair -> recheck
1. DRAMATIC INTENT: Why does the character move, now? Bad: random gaze or walk. Fix: motivation, eyeline and reaction beat before motion.
2. ANTICIPATION: Bad: instant walk or spin from idle. Fix: subtle gaze/breath/weight shift, then move.
3. BODY MECHANICS: Bad: head/torso/hips rotate as one rigid block; unnatural shoulders. Fix: staged head/shoulder/hip turning and planted foot.
4. TRANSITION: Bad: Stand-to-Walk snap, jump, incorrect first step. Fix: matched foot plant, smooth acceleration, careful blend; review before/after join frame by frame.
5. ROOT MOTION AND PATH: Bad: teleport, reset, foot sliding, collision, actor walks away from intended blocking. Fix: uninterrupted path and verified actor coordinates; no repeated root reset.
6. RHYTHM: Bad: kids move in sync, all turn at once, wrong emotional speed. Fix: individually offset timing/gait and add purposeful pauses.
7. EYELINE, REACTION, SPEECH: Bad: child looks into empty space, speaker mouth inactive, reaction mistimed. Fix: look targets and sound-aligned close-ups with correct speaking/lip-sync windows.
8. HANDS, CONTACT AND WEIGHT: Bad: stiff hands, fake hug, arm intersections and floating foot. Fix: proper relaxed hand pose, physical distance/contact and camera occlusion for unfixable contact.
9. CAMERA COVERAGE: Bad: full-body wide, long rear view, dominant shop shelves, actors drifting off-screen. Fix: 80/100mm MCU/CU/OTS/reaction framing with deliberate small camera movement; check actor occupies image adequately throughout shot.
10. EDITORIAL CONTINUITY AND PAYOFF: Bad: abrupt screen-direction reversal, phase mismatch at cut, character exits without story resolution. Fix: match-on-action, maintain axis/eyeline, give ending a purposeful emotional beat.

## Example for Part 3, 48-72.4 s (illustrative, sync to actual narration before editing)
Beat A 48-55: father and mistress decide and step away; keep faces visible rather than long back view.
Beat B 55-60: insert reaction of mother/children watching the departure; skip unnecessary walking distance.
Beat C 60-65: mother turns gaze to children, pauses, shifts weight, prepares to move; cut from face to three-quarter two/three-shot.
Beat D 65-69: first steps with kids at natural staggered offsets; match screen direction across shots.
Beat E 69-72.4: emotional departure resolution, frame follows characters and ends intentionally. No large shop shelf replacing people at the end.

## QC evidence requirements
For EACH pass record scene/timestamp, character, directly observed defect (or clear PASS evidence), probable cause, repair, retest and final pass/fail. Use actual moving video at 30fps+ plus iClone animation keys. Static contact sheets only verify still framing. Frame-difference peaks are candidates and often cuts, not proof of bad acting. Repeat the full 10-pass check after changes to detect regressions. A final sequence does not pass if action, face, eyelines or frame outcome feel wrong even if script API calls succeed.
Do not render 480p without asking the user to choose render-preview or self-check-in-iClone; do not render 1080p without explicit approval.

## Event boundary clarification (2026-11-11)
Coverage must not be interpreted as keeping the whole chapter in one timeline.
Production unit is now: complete event -> QA -> save -> render/check -> next event.

For Part 3:
- 3.1 conversation may use many cameras/reactions but is one rendered event.
- 3.2 leaving/walking is a new rendered event because main action changes.
- 3.3 aftermath/comfort is a new rendered event.
- 3.4 walk-home is separate only if it is a distinct new movement event.

Do not create a new event number solely for reaction/camera/speaker change.
Do not force fixed audio-time boundaries.
