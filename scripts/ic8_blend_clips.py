# Blend chained clips (face Look front copies, body Stand00 copies) so the pose is mixed across the join
# instead of snapping (head down -> head up). Sets TransitionRange on every clip after the first.
import RLPy, os
J = os.path.join(os.environ['LOCALAPPDATA'], 'Tidmunz Studio', 'snapgen_data', 'ic8_jobs')
SEC_FACE = 8.58  # user's own example (p3_commf face clip 1): long X crossfade, no snap at the join
SEC_BODY = 3.0
T = lambda s: RLPy.RTime.FromValue(int(round(s * 6000)))
out = []
for a in RLPy.RScene.GetAvatars():
    n = a.GetName()
    for label, comp in (('face', a.GetFaceComponent()), ('body', a.GetSkeletonComponent())):
        if not comp:
            continue
        for i in range(1, comp.GetClipCount()):
            c = comp.GetClip(i)
            try:
                c.SetTransitionRange(T(SEC_FACE if label == 'face' else SEC_BODY))
                out.append('%s %s clip %d trans -> %.2f' % (n, label, i, c.GetTransitionRange().ToFloat() / 6000.0))
            except Exception as e:
                out.append('%s %s clip %d ERR %r' % (n, label, i, e))
open(os.path.join(J, 'blend_clips.txt'), 'w').write('\n'.join(out))
