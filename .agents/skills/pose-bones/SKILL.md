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
