"""video_to_bvh.py - video of one person -> body motion .bvh. Runs on ANY PC: CPU, or any GPU through DirectML
(NVIDIA / AMD / Intel; user 2026-11-23: PCs are mid-range, one is AMD). Free for commercial use (Apache-2.0 models).
  python video_to_bvh.py <clip.mp4> <out.bvh> [check.mp4]
1. RTMPose (rtmlib, Halpe-26 points incl. feet) finds the 2D body in every frame.
2. MotionBERT-lite (ONNX, 243-frame window) lifts the whole clip to 3D at once: steady depth, no jitter
   (MediaPipe guessed 3D per frame = rejected by the user as too poor).
check.mp4 = the clip with the 2D points | the BVH replayed (front, side), to SEE it works."""
import sys, os, math
import numpy as np, cv2


class L:   # MediaPipe 33-point layout kept, so targets()/offsets() stay the same
    NOSE, LEFT_EAR, RIGHT_EAR, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW, LEFT_WRIST, RIGHT_WRIST = 0, 7, 8, 11, 12, 13, 14, 15, 16
    LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE, LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX = 23, 24, 25, 26, 27, 28, 31, 32


HEAD_LIFT = 0.0   # MediaPipe needed 0.21 rad (nose below the ears); here the head point is built level
MB_ONNX = os.environ.get("MOTIONBERT_ONNX") or os.path.join(os.path.dirname(os.path.dirname(sys.executable)), "motionbert_lite_243.onnx")
HALPE_LINES = [(5, 7), (7, 9), (6, 8), (8, 10), (5, 6), (11, 12), (5, 11), (6, 12), (11, 13), (13, 15), (12, 14), (14, 16),
               (15, 20), (15, 24), (16, 21), (16, 25), (0, 17), (17, 18)]


def providers():
    import onnxruntime as ort
    have = ort.get_available_providers()
    return [p for p in ("DmlExecutionProvider", "CUDAExecutionProvider") if p in have] + ["CPUExecutionProvider"]


# joint: (parent, rest direction (unit, T-pose, facing +Z, Y up, character's left = +X), length key)
J = {
 "Hips": (None, None), "Spine": ("Hips", (0, 1, 0)), "Neck": ("Spine", (0, 1, 0)), "Head": ("Neck", (0, 1, 0)),
 "LeftArm": ("Spine", (1, 0, 0)), "LeftForeArm": ("LeftArm", (1, 0, 0)), "LeftHand": ("LeftForeArm", (1, 0, 0)),
 "RightArm": ("Spine", (-1, 0, 0)), "RightForeArm": ("RightArm", (-1, 0, 0)), "RightHand": ("RightForeArm", (-1, 0, 0)),
 "LeftUpLeg": ("Hips", (0, -1, 0)), "LeftLeg": ("LeftUpLeg", (0, -1, 0)), "LeftFoot": ("LeftLeg", (0, -1, 0)),
 "RightUpLeg": ("Hips", (0, -1, 0)), "RightLeg": ("RightUpLeg", (0, -1, 0)), "RightFoot": ("RightLeg", (0, -1, 0)),
}
ORDER = list(J)
ENDS = {"Head": (0, 12, 0), "LeftHand": (8, 0, 0), "RightHand": (-8, 0, 0), "LeftFoot": (0, -6, 12), "RightFoot": (0, -6, 12)}


def unit(v):
    n = np.linalg.norm(v); return v / n if n > 1e-9 else v


def rot_between(a, b):
    a, b = unit(a), unit(b); v = np.cross(a, b); c = float(np.dot(a, b))
    if c < -0.9999:
        ax = unit(np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0]))
        return 2 * np.outer(ax, ax) - np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + c)


def frame(x, y):   # rotation whose columns are x (left), y (up), z (forward)
    x = unit(x); y = unit(y - np.dot(y, x) * x); return np.column_stack([x, y, np.cross(x, y)])


def euler_zxy(R):   # NOW X-Y-Z: R = Rx @ Ry @ Rz -> degrees (x, y, z). Knees/elbows bend on X (first), lock only at twist 90.
    y = math.asin(max(-1, min(1, R[0, 2])))
    return math.degrees(math.atan2(-R[1, 2], R[2, 2])), math.degrees(y), math.degrees(math.atan2(-R[0, 1], R[0, 0]))


def Rzxy(x, y, z):
    z, x, y = map(math.radians, (z, x, y))
    Rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    return Rx @ Ry @ Rz


def halpe2h36m(x):   # MotionBERT's own mapping (lib/data/dataset_wild.py)
    y = np.zeros((len(x), 17, x.shape[2]), np.float32)
    for d, src in enumerate([19, 12, 14, 16, 11, 13, 15, None, 18, 0, 17, 5, 7, 9, 6, 8, 10]):
        y[:, d] = (x[:, 18] + x[:, 19]) * 0.5 if src is None else x[:, src]
    return y


def lift(k2d):
    """2D Halpe (T,26,3: x, y, score) -> 3D H36M (T,17,3) camera space (x right, y down, z away), MotionBERT-lite."""
    import onnxruntime as ort
    sess = ort.InferenceSession(MB_ONNX, providers=["CPUExecutionProvider"])   # small; DirectML cannot load it (tested)
    x = halpe2h36m(k2d)
    v = x[x[..., 2] > 0][:, :2]; lo, hi = v.min(0), v.max(0); sc = max(hi - lo)   # crop_scale: whole clip, [-1, 1]
    x[..., :2] = ((x[..., :2] - (lo + hi - sc) / 2) / sc - 0.5) * 2
    T, W = len(x), 243
    flip = lambda d: np.concatenate([d[..., :1] * -1, d[..., 1:]], -1)[..., [0, 4, 5, 6, 1, 2, 3, 7, 8, 9, 10, 14, 15, 16, 11, 12, 13], :]
    out, wsum = np.zeros((T, 17, 3), np.float32), np.zeros((T, 1, 1), np.float32)
    starts = list(range(0, max(1, T - W + 1), W - 60)); starts += [max(0, T - W)] if starts[-1] + W < T else []
    for s0 in starts:
        idx = np.clip(np.arange(s0, s0 + W), 0, T - 1); seg = x[idx][None]
        y = (sess.run(None, {"kp2d": seg})[0][0] + flip(sess.run(None, {"kp2d": flip(seg[0])[None]})[0][0])) / 2   # + mirror pass
        n = min(W, T - s0); w = np.minimum(1, np.minimum(np.arange(1, n + 1), np.arange(n, 0, -1)) / 30.0)[:, None, None]
        out[s0:s0 + n] += y[:n] * w; wsum[s0:s0 + n] += w
    return out / np.maximum(wsum, 1e-6)


def detect(path):
    from rtmlib import BodyWithFeet, PoseTracker
    from rtmlib.tools import base
    prov = providers()[0]; dev = {"DmlExecutionProvider": "dml", "CUDAExecutionProvider": "cuda"}.get(prov, "cpu")
    base.RTMLIB_SETTINGS["onnxruntime"]["dml"] = "DmlExecutionProvider"
    track = PoseTracker(BodyWithFeet, det_frequency=8, tracking=False, mode="performance" if dev != "cpu" else "balanced",
                        backend="onnxruntime", device=dev)
    print("DEVICE", prov, flush=True)
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames, k2d = [], []; tot = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1; nxt = 0
    while True:
        ok, im = cap.read()
        if not ok: break
        if len(frames) >= nxt: print("PCT body %d/%d" % (len(frames), tot), flush=True); nxt += max(1, tot // 10)
        frames.append(im); kp, sc = track(im)
        if len(kp):
            i = int(np.argmax([(np.ptp(k[:, 0]) * np.ptp(k[:, 1])) for k in kp]))   # the biggest person
            k2d.append(np.concatenate([kp[i], sc[i][:, None]], 1))
        else: k2d.append(k2d[-1] if k2d else None)
    first = next(k for k in k2d if k is not None)
    K = np.array([k if k is not None else first for k in k2d], np.float32)
    H = lift(K.copy())
    H = np.stack([H[..., 0], -H[..., 1], -H[..., 2]], -1)   # Y up, +Z to the camera (as before)
    k = 3; pad = np.pad(H, ((1, 1), (0, 0), (0, 0)), mode="edge"); H = np.mean([pad[i:i + len(H)] for i in range(k)], axis=0)
    P = np.zeros((len(H), 33, 3), np.float32)
    for mp_i, h in ((L.LEFT_HIP, 4), (L.RIGHT_HIP, 1), (L.LEFT_KNEE, 5), (L.RIGHT_KNEE, 2), (L.LEFT_ANKLE, 6), (L.RIGHT_ANKLE, 3),
                    (L.LEFT_SHOULDER, 11), (L.RIGHT_SHOULDER, 14), (L.LEFT_ELBOW, 12), (L.RIGHT_ELBOW, 15),
                    (L.LEFT_WRIST, 13), (L.RIGHT_WRIST, 16), (L.NOSE, 9)):
        P[:, mp_i] = H[:, h]
    # head centre = the nose projected on the neck->head-top line (level look direction, no ear guessing)
    neck, top = H[:, 8], H[:, 10]; ax = top - neck; t = np.sum((H[:, 9] - neck) * ax, 1, keepdims=True) / np.sum(ax * ax, 1, keepdims=True)
    P[:, L.LEFT_EAR] = P[:, L.RIGHT_EAR] = neck + t * ax
    for side, hip, kn, an, toe in (("L", L.LEFT_HIP, L.LEFT_KNEE, L.LEFT_ANKLE, L.LEFT_FOOT_INDEX),
                                   ("R", L.RIGHT_HIP, L.RIGHT_KNEE, L.RIGHT_ANKLE, L.RIGHT_FOOT_INDEX)):
        shin = P[:, an] - P[:, kn]; shin /= np.linalg.norm(shin, axis=1, keepdims=True)
        lr = P[:, L.LEFT_HIP] - P[:, L.RIGHT_HIP]; lr -= np.sum(lr * shin, 1, keepdims=True) * shin
        fwd = np.cross(shin, lr); fwd /= np.linalg.norm(fwd, axis=1, keepdims=True) + 1e-9
        P[:, toe] = P[:, an] + fwd * 0.08   # foot at 90 deg to the shin (no 3D toes from 2D)
    thigh = np.median(np.linalg.norm(P[:, L.LEFT_KNEE] - P[:, L.LEFT_HIP], axis=1))
    P *= 42.0 / max(thigh, 1e-6)   # -> cm (thigh 42 cm)
    vis = np.zeros(33); hv = K[:, :, 2].mean(0)
    for mp_i, hp in ((L.LEFT_ELBOW, 7), (L.LEFT_WRIST, 9), (L.RIGHT_ELBOW, 8), (L.RIGHT_WRIST, 10)): vis[mp_i] = hv[hp]
    return P, fps, frames, K, vis


def targets(p):
    """global rotation of every joint for one frame of landmarks p (33x3)."""
    mid = lambda a, b: (p[a] + p[b]) / 2
    hip, sh = mid(L.LEFT_HIP, L.RIGHT_HIP), mid(L.LEFT_SHOULDER, L.RIGHT_SHOULDER)
    head = mid(L.LEFT_EAR, L.RIGHT_EAR)
    G = {"Hips": frame(p[L.LEFT_HIP] - p[L.RIGHT_HIP], sh - hip),
         "Spine": frame(p[L.LEFT_SHOULDER] - p[L.RIGHT_SHOULDER], sh - hip)}
    # head: look direction only (nose - ears), NO roll from the ears (the hidden ear is a guess -> head fell sideways)
    up = G["Spine"][:, 1]; f = unit(p[L.NOSE] - head)
    f = unit(np.cos(HEAD_LIFT) * f + np.sin(HEAD_LIFT) * up)
    hx = unit(np.cross(up, f)); G["Head"] = np.column_stack([hx, np.cross(f, hx), f])
    cx = G["Spine"][:, 0]; up_t = G["Spine"][:, 1]
    ua = lambda a, b, s: (p[b] - p[a]) + s * 0.18 * np.linalg.norm(p[b] - p[a]) * cx   # arms a bit wider: CC thighs are thicker
    want = {"Neck": unit(head - sh) + up_t,   # half way to the chest's up: a soft neck, not a broken one
            "LeftArm": ua(L.LEFT_SHOULDER, L.LEFT_ELBOW, 1), "LeftForeArm": p[L.LEFT_WRIST] - p[L.LEFT_ELBOW],
            "LeftHand": p[L.LEFT_WRIST] - p[L.LEFT_ELBOW],   # hand in line with the forearm (finger points are noise)
            "RightArm": ua(L.RIGHT_SHOULDER, L.RIGHT_ELBOW, -1), "RightForeArm": p[L.RIGHT_WRIST] - p[L.RIGHT_ELBOW],
            "RightHand": p[L.RIGHT_WRIST] - p[L.RIGHT_ELBOW],
            "LeftUpLeg": p[L.LEFT_KNEE] - p[L.LEFT_HIP], "LeftLeg": p[L.LEFT_ANKLE] - p[L.LEFT_KNEE],
            "LeftFoot": p[L.LEFT_FOOT_INDEX] - p[L.LEFT_ANKLE],
            "RightUpLeg": p[L.RIGHT_KNEE] - p[L.RIGHT_HIP], "RightLeg": p[L.RIGHT_ANKLE] - p[L.RIGHT_KNEE],
            "RightFoot": p[L.RIGHT_FOOT_INDEX] - p[L.RIGHT_ANKLE]}
    for j in ORDER:
        if j in G: continue
        par = G[J[j][0]]
        # the bone's own rest direction is ITS CHILD's direction; for end bones use the joint's want direction
        child = next((c for c in ORDER if J[c][0] == j), None)
        d = want[j] if j in want else None
        rest = np.array(J[child][1] if child else ENDS[j], float)
        cur = par @ rest
        G[j] = rot_between(cur, d) @ par
    return G


def offsets(P):
    m = lambda a, b: np.median(np.linalg.norm(P[:, a] - P[:, b], axis=1))
    sh, hp = (P[:, L.LEFT_SHOULDER] + P[:, L.RIGHT_SHOULDER]) / 2, (P[:, L.LEFT_HIP] + P[:, L.RIGHT_HIP]) / 2
    torso = float(np.median(np.linalg.norm(sh - hp, axis=1)))
    hw, sw = m(L.LEFT_HIP, L.RIGHT_HIP) / 2, m(L.LEFT_SHOULDER, L.RIGHT_SHOULDER) / 2
    up, uarm, farm, hand = m(L.LEFT_HIP, L.LEFT_KNEE), m(L.LEFT_SHOULDER, L.LEFT_ELBOW), m(L.LEFT_ELBOW, L.LEFT_WRIST), 8
    shin = m(L.LEFT_KNEE, L.LEFT_ANKLE)
    return {"Hips": (0, 0, 0), "Spine": (0, 0, 0), "Neck": (0, torso, 0), "Head": (0, 12, 0),
            "LeftArm": (sw, torso, 0), "LeftForeArm": (uarm, 0, 0), "LeftHand": (farm, 0, 0),
            "RightArm": (-sw, torso, 0), "RightForeArm": (-uarm, 0, 0), "RightHand": (-farm, 0, 0),
            "LeftUpLeg": (hw, 0, 0), "LeftLeg": (0, -up, 0), "LeftFoot": (0, -shin, 0),
            "RightUpLeg": (-hw, 0, 0), "RightLeg": (0, -up, 0), "RightFoot": (0, -shin, 0)}, up + shin
# note: the Spine joint is at the hips; its child arms/neck sit at shoulder height (torso offset)


def write_bvh(out, P, fps, copy_arm=None):
    off, leg = offsets(P)
    kids = {j: [c for c in ORDER if J[c][0] == j] for j in ORDER}
    ends = {"Head": (0, 12, 0), "LeftHand": (8, 0, 0), "RightHand": (-8, 0, 0), "LeftFoot": (0, -6, 12), "RightFoot": (0, -6, 12)}
    s = ["HIERARCHY"]
    def rec(j, d):
        t = "  " * d
        s.append(t + ("ROOT " if d == 0 else "JOINT ") + j); s.append(t + "{")
        s.append(t + "  OFFSET %.3f %.3f %.3f" % (tuple(off[j]) if d else (0, leg, 0)))
        s.append(t + "  CHANNELS " + ("6 Xposition Yposition Zposition " if d == 0 else "3 ") + "Xrotation Yrotation Zrotation")
        for c in kids[j]: rec(c, d + 1)
        if j in ends:
            s.append(t + "  End Site"); s.append(t + "  {"); s.append(t + "    OFFSET %.3f %.3f %.3f" % ends[j]); s.append(t + "  }")
        s.append(t + "}")
    rec("Hips", 0)
    s += ["MOTION", "Frames: %d" % len(P), "Frame Time: %.6f" % (1 / fps)]
    prev, rows = {}, []
    def near(a, b): return a + 360 * round((b - a) / 360)
    for p in P:
        G = targets(p); row = [0, leg, 0]
        for j in ORDER:
            par = J[j][0]; Lr = G[j] if par is None else G[par].T @ G[j]
            x, y, z = euler_zxy(Lr)
            if j in prev:   # same rotation, written the way closest to the last frame (no 360/180 jumps = no pops)
                px, py, pz = prev[j]
                c = [(near(x, px), near(y, py), near(z, pz)), (near(x + 180, px), near(180 - y, py), near(z + 180, pz))]
                x, y, z = min(c, key=lambda e: abs(e[0] - px) + abs(e[1] - py) + abs(e[2] - pz))
            prev[j] = (x, y, z); row += [x, y, z]
        if copy_arm:   # hidden arm = mirror of the visible one (mirror across X: x, -y, -z)
            src, dst = copy_arm
            for part in ("Arm", "ForeArm", "Hand"):
                a, d = 3 + 3 * ORDER.index(src + part), 3 + 3 * ORDER.index(dst + part)
                row[d:d + 3] = [row[a], -row[a + 1], -row[a + 2]]
        rows.append(row)
    # hips height: the lowest foot point stands on the floor (y 0). Before, the hips stayed at standing height, so a
    # sitting body floated and iClone's foot contact pulled the feet down = body tipped back (user 2026-11-23)
    low = []
    for row in rows:
        pos, tip = fk(row, off, leg)
        low.append(min(pos["LeftFoot"][1], pos["RightFoot"][1], tip["LeftFoot"][1], tip["RightFoot"][1]))
    k = 9; low = np.array(low); pad = np.pad(low, k // 2, mode="edge"); low = np.mean([pad[i:i + len(low)] for i in range(k)], axis=0)
    for row, lo in zip(rows, low):
        row[1] = leg - lo
        s.append(" ".join("%.4f" % v for v in row))
    open(out, "w").write("\n".join(s) + "\n")
    return off, leg


def fk(row, off, leg):   # replay the BVH row -> joint positions (to check the file, not the landmarks)
    pos, rot, i = {}, {}, 3
    for j in ORDER:
        R = Rzxy(*row[i:i + 3]); i += 3; par = J[j][0]
        if par is None: rot[j] = R; pos[j] = np.array([0, row[1], 0.0])
        else: rot[j] = rot[par] @ R; pos[j] = pos[par] + rot[par] @ np.array(off[j], float)
    tips = {"Head": (0, 12, 0), "LeftHand": (8, 0, 0), "RightHand": (-8, 0, 0), "LeftFoot": (0, -6, 12), "RightFoot": (0, -6, 12)}
    return pos, {k: pos[k] + rot[k] @ np.array(v, float) for k, v in tips.items()}


def check_video(out, bvh, off, leg, frames, img2d, fps):
    rows = [list(map(float, l.split())) for l in open(bvh).read().split("Frame Time:")[1].splitlines()[1:] if l.strip()]
    h, w = frames[0].shape[:2]; side = np.zeros((h, w, 3), np.uint8)
    vw = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w * 3, h))
    sc = h / 260.0
    for im, lm, row in zip(frames, img2d, rows):
        a = im.copy()
        for i, j in HALPE_LINES:
            if lm[i, 2] > 0.3 and lm[j, 2] > 0.3:
                cv2.line(a, tuple(int(v) for v in lm[i, :2]), tuple(int(v) for v in lm[j, :2]), (0, 255, 0), 4)
        pos, tip = fk(row, off, leg); views = []
        for name, (u, sgn) in (("front", (0, 1)), ("side", (2, -1))):
            b = side.copy(); cv2.putText(b, "BVH " + name, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            P2 = lambda v: (int(w / 2 + sgn * v[u] * sc), int(h - 60 - v[1] * sc))
            for j in ORDER:
                if J[j][0]: cv2.line(b, P2(pos[J[j][0]]), P2(pos[j]), (0, 220, 255), 6)
            for k, v in tip.items(): cv2.line(b, P2(pos[k]), P2(v), (0, 255, 0), 6)
            views.append(b)
        vw.write(np.hstack([a] + views))
    vw.release()


if __name__ == "__main__":
    P, fps, frames, img2d, vis = detect(sys.argv[1])
    vl, vr = (vis[L.LEFT_ELBOW] + vis[L.LEFT_WRIST]) / 2, (vis[L.RIGHT_ELBOW] + vis[L.RIGHT_WRIST]) / 2
    copy = ("Right", "Left") if vl < 0.25 and vr > 0.6 else ("Left", "Right") if vr < 0.25 and vl > 0.6 else None   # MotionBERT already guesses hidden arms from time
    print("arm visibility L %.2f R %.2f%s" % (vl, vr, "  -> %s arm hidden: mirror of the %s arm" % (copy[1], copy[0]) if copy else ""))
    off, leg = write_bvh(sys.argv[2], P, fps, copy)
    print("BVH %s: %d frames @ %.0f fps" % (sys.argv[2], len(P), fps))
    if len(sys.argv) > 3: check_video(sys.argv[3], sys.argv[2], off, leg, frames, img2d, fps); print("CHECK", sys.argv[3])
