---
name: pose-bones
description: Pose a CC character's bones by Python in iClone (= Edit Motion Layer) - lean, head tilt, nod, arm/hand position - and look at a person or camera. Use when a library motion is close but the pose needs adjusting, or for a still pose.
---
# Pose bones by Python (Edit Motion Layer)

```python
import RLPy, math
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
sk = avatar.GetSkeletonComponent()
bones = {b.GetName(): b for b in sk.GetSkinBones()}     # e.g. 'CC_Base_Head', 'CC_Base_L_Upperarm'
clip = sk.GetClip(0) if sk.GetClipCount() else sk.AddClip(T(0))
db = clip.GetControl('Layer', bones['CC_Base_Head']).GetDataBlock()
rx, ry, rz = [db.GetControl('Rotation/Rotation' + a) for a in 'XYZ']   # values in RADIANS
for t0 in (start, end):                                 # key at START and END so the pose holds the whole clip
    rz.SetValue(T(t0), math.radians(10))                # tilt head 10 deg toward the shoulder
avatar.Update()
```
(Proven in `scripts/ic8_pose_face.py`. Set the other axes to 0. to reset a layer.)
- Bone names: CC_Base_Head, CC_Base_NeckTwist01, CC_Base_Spine02, CC_Base_L_Upperarm, CC_Base_L_Forearm, CC_Base_L_Hand (R_ for right). Print `list(bones)` if unsure.
- CC bone local axes: **X = nod**, **Y = turn**, **Z = sideways tilt** (head toward the shoulder).
- Proven soft lean: Spine02 8 deg, NeckTwist01 10 deg, Head 10 deg. Keep angles small (<= 15 deg); slow folk-tale style.
- Arms/hands: after rotating, CHECK the hand position: `b.WorldTransform().T()` (z = height, cm). Before reading bones or rendering, settle: `RLPy.RGlobal.SetTime(T(s)); QtWidgets.QApplication.processEvents(); RLPy.RGlobal.ForceViewportUpdate()`. Bone world reads can be garbage (0 / thousands) if not settled - re-read.
- Look at a person: `sk.GetLookAtComponent().AddLookAtKey(T(0), T(1), <other avatar's Head skin bone>, 1.0, 0.0)`. The HEAD turns 50-80 deg toward the target whatever the body yaw, so put the camera on the side the actor looks toward. Look at camera: `AddLookAtKey(T(0), cameraObject)`.
- Sitting poses: AccuPOSE through the GUI panel only (scripted AccuPOSE crashed iClone). Clear animation -> frame 0 -> pose -> then face/blink/lip.
- Always check with stills (skill `review-stills`). Never save by script.
More: `docs/iclone-key-SKILL.md` ("Posing bones by Python"), `docs/rlpy_lessons.md`.

## AccuPOSE-first — mandatory for static contact/holding (2026-11-27)
Before choosing any body motion, consult docs/accupose_presets.md (420 poses) and docs/motion_catalog.md. For static holding, handing, seated or supported/contact poses, choose a suitable existing AccuPOSE preset first (e.g. Basic Stand for upright trophy holding), then adapt wrists, elbows and fingers. Do not layer an incompatible idle clip on top of the pose. Preserve the base pose; use subtle head motion and blink. Inspect actual contact through the shot. Gesture .iHand library: resolve the installed Reallusion Templates/Animation/Gesture folder on this PC; inspect suitable hand presets, not just filenames. For complex existing motion, inspect DataLink connection and linked avatar identity; send the current pose/motion to Blender, adjust the existing animation and send back only the intended actor/range. DataLink roundtrip is not yet verified in this story. Never invoke RFileIO.LoadFile on .rlDikPreset (known crash); use the AccuPOSE panel. Do not render before approval. If a relevant reference already exists, read and reuse it before writing a new helper. Do not treat this rule as evidence a pose was applied.

## Attach after pose — mandatory (2026-11-27)
For a prop intended to remain on a body part, fit the pose and prop contact first; use Attach (permanent parent to the correct sub-node, e.g. hand for held trophy, head for glasses/hair). Preserve world placement, scale and orientation at attach time; inspect parent and parent node, check relative transform at start/middle/end and actual contact. Do not use repeated world-position tracking as a substitute for Attach when the prop must stay on the body. Native Link is also acceptable for ordinary held props, including continuous holding; use time keys for handoff/release. For hair, parenting a prop to head does not convert it into a skinned hair asset; distinguish the two. Save the same main file via the authorized visible File > Save Project workflow at the approval gate; no duplicate files or render before approval. If the attachment API or GUI is not verified, stop and report the actual blocker rather than marking success.
- 2026-11-27: Once grip or head alignment is visually correct, Attach or Link the intended prop to the exact hand/head bone (not just avatar root); verify actual parent and stable local offset over time, then save only at authorized menu-save gate. Do not use repeated world keys as a substitute for verified Attach or Link. A hair prop attached to head follows head but is not automatically converted to native skinned hair.
- 2026-11-27 (user clarification): Ordinary handheld props may use native Link instead of Attach; no need to convert to Accessory. Prefer exact hand sub-node and preserve world alignment. Attach for permanent accessories only when useful. Verify link target at start/middle/end and actual grip before save; use the visible existing Modify controls for small position fixes rather than rerunning Pose. No render before approval.
- Before Attach/Link a held prop, clear the avatar Look At target pointing to that same prop using Modify > Look at > Set Free; zero weights alone leave a dependency cycle. Verified in iClone 8.71: Pick Parent on avatar, Link ... > search exact CC_Base_R_Hand > Align None > OK. Verify actual sub-node and relative offset across the clip. Do not rerun pose for small prop changes.
