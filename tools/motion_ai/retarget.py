# blender -b --factory-startup --python retarget.py -- <soma.blend> <out.fbx>
# SOMA (Motion AI) motion -> CC3/CC4 CC_Base skeleton, export FBX with the CC mesh (iClone: Convert All).
import bpy, sys, mathutils, os
src_blend, out = sys.argv[sys.argv.index("--") + 1:][:2]
CC = os.environ.get("CC_BASE_FBX") or os.path.join(os.path.expanduser("~"), "Documents", "Reallusion", "DataLink", "CC4 - CC3_Base_Plus_2", "exports", "CC3_Base_Plus", "CC3_Base_Plus.fbx")
MAP = [("Hips", "CC_Base_Hip"), ("Spine1", "CC_Base_Waist"), ("Spine2", "CC_Base_Spine01"), ("Chest", "CC_Base_Spine02"),
       ("Neck1", "CC_Base_NeckTwist01"), ("Neck2", "CC_Base_NeckTwist02"), ("Head", "CC_Base_Head")]
for s in ("Left", "Right"):
    c = s[0]
    MAP += [(s + "Shoulder", "CC_Base_%s_Clavicle" % c), (s + "Arm", "CC_Base_%s_Upperarm" % c), (s + "ForeArm", "CC_Base_%s_Forearm" % c),
            (s + "Hand", "CC_Base_%s_Hand" % c), (s + "Leg", "CC_Base_%s_Thigh" % c), (s + "Shin", "CC_Base_%s_Calf" % c),
            (s + "Foot", "CC_Base_%s_Foot" % c), (s + "ToeBase", "CC_Base_%s_ToeBase" % c)]

bpy.ops.wm.open_mainfile(filepath=src_blend)
sc = bpy.context.scene
S = [o for o in sc.objects if o.type == "ARMATURE"][0]
f0, f1 = 1, int(os.environ.get("LAST", "151"))
bpy.ops.import_scene.fbx(filepath=CC)
T = [o for o in sc.objects if o.type == "ARMATURE" and o != S][0]
MAP = [(a, b) for a, b in MAP if a in S.pose.bones and b in T.pose.bones]
order = [b.name for b in T.data.bones]                      # parents before children
MAP.sort(key=lambda m: order.index(m[1]))
upd = bpy.context.view_layer.update

def wmat(o, n): return o.matrix_world @ o.pose.bones[n].matrix
def rot(m): return m.to_quaternion()

# 1) rest of both (SOMA rest = data bones; CC rest = data bones), then swing CC bones onto SOMA rest directions
sc.frame_set(f0)
for o in (S, T):
    for pb in o.pose.bones: pb.matrix_basis.identity()
    o.animation_data and setattr(o.animation_data, "action", o.animation_data.action)
saved_nla = []
if S.animation_data:
    for t in S.animation_data.nla_tracks: saved_nla.append((t, t.mute)); t.mute = True
    act = S.animation_data.action; S.animation_data.action = None
upd()
Rs0 = {a: rot(wmat(S, a)) for a, _ in MAP}
for a, b in MAP:
    if a == "Hips": continue
    # NOSWING_SPINE=1 (video_to_bvh motions): keep the CC spine/neck rest; swinging it tilts the whole chain above it
    # (user 2026-11-23: the body leaned back, hands did not reach the knees)
    if os.environ.get("NOSWING_SPINE") == "1" and b in ("CC_Base_Waist", "CC_Base_Spine01", "CC_Base_Spine02",
                                                         "CC_Base_NeckTwist01", "CC_Base_NeckTwist02", "CC_Base_Head"): continue
    pb = T.pose.bones[b]
    w = wmat(T, b); d_t = (w.to_3x3() @ mathutils.Vector((0, 1, 0))).normalized()
    sb = S.pose.bones[a]; ws = wmat(S, a); d_s = (ws.to_3x3() @ mathutils.Vector((0, 1, 0))).normalized()
    sw = d_t.rotation_difference(d_s)
    nw = mathutils.Matrix.Translation(w.to_translation()) @ sw.to_matrix().to_4x4() @ w.to_3x3().to_4x4()
    pb.matrix = T.matrix_world.inverted() @ nw; upd()
Mt0 = {b: rot(wmat(T, b)) for _, b in MAP}
hip_t0 = wmat(T, "CC_Base_Hip").to_translation()
hip_s0 = wmat(S, "Hips").to_translation()
ratio = hip_t0.z / max(hip_s0.z, 1e-4)
if os.environ.get("HIP_FROM_F0") == "1":   # mocap BVH (CMU): root rest is at the floor, so measure the hip at the first frame
    if S.animation_data: S.animation_data.action = act
    sc.frame_set(f0); upd(); hip_s0 = wmat(S, "Hips").to_translation(); ratio = hip_t0.z / max(hip_s0.z, 1e-4)
    S.animation_data.action = None; upd()

def hand_ik(f):
    """HAND_IK=1 (video_to_bvh motions): a hand near a knee in the clip stays at the same place on the CC knee
    (CC arms/legs have other lengths, so copied angles put the hand past the knee; user 2026-11-23)."""
    for c, s in (("L", "Left"), ("R", "Right")):
        if s + "Hand" not in S.pose.bones or s + "Shin" not in S.pose.bones: continue
        sw, sk = wmat(S, s + "Hand").to_translation(), wmat(S, s + "Shin").to_translation()
        d = (sw - sk).length / max(hip_s0.z, 1e-4)               # in hip heights (scale free)
        wgt = max(0.0, min(1.0, (0.45 - d) / 0.2))               # full when the hand is on the knee, none when far
        if wgt <= 0: continue
        ua, fa, hd = (T.pose.bones["CC_Base_%s_%s" % (c, n)] for n in ("Upperarm", "Forearm", "Hand"))
        hand_rot = rot(wmat(T, hd.name))
        S0, E0, H0 = (wmat(T, b.name).to_translation() for b in (ua, fa, hd))
        tgt = wmat(T, "CC_Base_%s_Calf" % c).to_translation() + (sw - sk) * ratio
        tgt = H0.lerp(tgt, wgt)
        a, b = (E0 - S0).length, (H0 - E0).length
        to = tgt - S0; dist = max(abs(a - b) + 1e-4, min(a + b - 1e-4, to.length)); dirn = to.normalized()
        pole = (E0 - S0) - dirn * (E0 - S0).dot(dirn)
        pole = pole.normalized() if pole.length > 1e-6 else dirn.orthogonal().normalized()
        x = (a * a - b * b + dist * dist) / (2 * dist); h = max(0.0, a * a - x * x) ** 0.5
        E1 = S0 + dirn * x + pole * h
        q = (E0 - S0).rotation_difference(E1 - S0); w = wmat(T, ua.name)
        ua.matrix = T.matrix_world.inverted() @ (mathutils.Matrix.Translation(S0) @ q.to_matrix().to_4x4() @ w.to_3x3().to_4x4()); upd()
        E, H = wmat(T, fa.name).to_translation(), wmat(T, hd.name).to_translation()
        q = (H - E).rotation_difference(S0 + dirn * dist - E); w = wmat(T, fa.name)
        fa.matrix = T.matrix_world.inverted() @ (mathutils.Matrix.Translation(E) @ q.to_matrix().to_4x4() @ w.to_3x3().to_4x4()); upd()
        H = wmat(T, hd.name)
        hd.matrix = T.matrix_world.inverted() @ (mathutils.Matrix.Translation(H.to_translation()) @ hand_rot.to_matrix().to_4x4()
                                                 @ mathutils.Matrix.Diagonal(H.to_scale()).to_4x4()); upd()
        for pb in (ua, fa, hd):
            pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=f)


# 2) bake
for t, m in saved_nla: t.mute = m
if S.animation_data: S.animation_data.action = act
for pb in T.pose.bones: pb.matrix_basis.identity()
T.animation_data_create(); T.animation_data.action = bpy.data.actions.new("p2_cc")
if os.environ.get("REST0", "1") == "1":   # iClone uses frame 0 as the reference (bind) pose
    for pb in T.pose.bones:
        pb.matrix_basis.identity(); pb.keyframe_insert("location", frame=f0 - 1)
        pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=f0 - 1)
for f in range(f0, f1 + 1):
    if (f - f0) % max(1, (f1 - f0) // 10) == 0: print("PCT bake %d/%d" % (f - f0, f1 - f0 + 1), flush=True)
    sc.frame_set(f)
    for pb in T.pose.bones: pb.matrix_basis.identity()
    upd()
    for a, b in MAP:
        q = rot(wmat(S, a)) @ Rs0[a].inverted() @ Mt0[b]
        cur = wmat(T, b)
        loc = cur.to_translation()
        if a == "Hips":
            loc = hip_t0 + (wmat(S, "Hips").to_translation() - hip_s0) * ratio
            if os.environ.get("HIP_YAW_ONLY") == "1":
                # iClone (HIK onto another character) drops the spine's counter-rotation: a tilted Hip bone tilts the whole
                # body back (user 2026-11-23 "ท่ายังเพี้ยน"). Hip keeps only its heading; waist/thighs get the tilt (world-space).
                fw = (rot(wmat(S, a)) @ Rs0[a].inverted()) @ mathutils.Vector((0, -1, 0)); fw.z = 0
                if fw.length > 1e-4: q = mathutils.Vector((0, -1, 0)).rotation_difference(fw.normalized()) @ Mt0[b]
        pb = T.pose.bones[b]
        pb.matrix = T.matrix_world.inverted() @ (mathutils.Matrix.Translation(loc) @ q.to_matrix().to_4x4() @
                                                 mathutils.Matrix.Diagonal(cur.to_scale()).to_4x4())
        upd()
        pb.keyframe_insert("rotation_quaternion", frame=f) if pb.rotation_mode == "QUATERNION" else pb.keyframe_insert("rotation_euler", frame=f)
        if a == "Hips": pb.keyframe_insert("location", frame=f)
    if os.environ.get("HAND_IK") == "1": hand_ik(f)
print("BAKED", f0, f1, len(MAP), "bones ratio %.3f" % ratio)

# 3) export CC armature + its meshes only
bpy.ops.object.select_all(action="DESELECT")
T.select_set(True)
for o in sc.objects:
    if o.type == "MESH" and o.parent == T: o.select_set(True)
sc.frame_start, sc.frame_end = (f0 - 1 if os.environ.get("REST0", "1") == "1" else f0), f1
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, bake_anim=True, bake_anim_use_nla_strips=False,
                         bake_anim_use_all_actions=False, add_leaf_bones=False, armature_nodetype="NULL")
bpy.ops.wm.save_as_mainfile(filepath=out.replace(".fbx", "_retarget.blend"))
import shutil   # iClone needs the CC profile files next to the FBX (same base name), else the body comes out hunched
for ext in (".fbxkey", ".3dxProfile"):
    shutil.copyfile(CC[:-4] + ext, out[:-4] + ext)
print("EXPORTED", out)
