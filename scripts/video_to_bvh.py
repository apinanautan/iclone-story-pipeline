"""video_to_bvh.py - local, light (CPU) video -> body motion .bvh with MediaPipe Pose.
  python video_to_bvh.py <clip.mp4> <out.bvh> [check.mp4]
check.mp4 = the clip with the detected skeleton | the BVH replayed as a stick figure (side view), to SEE it works."""
import sys, math
import numpy as np, cv2, mediapipe as mp

L = mp.solutions.pose.PoseLandmark
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


def detect(path):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    pts, img2d, frames, vis = [], [], [], []
    with mp.solutions.pose.Pose(model_complexity=2, smooth_landmarks=True) as pose:
        while True:
            ok, im = cap.read()
            if not ok: break
            r = pose.process(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)); frames.append(im)
            if r.pose_world_landmarks:
                w = np.array([[p.x, -p.y, -p.z] for p in r.pose_world_landmarks.landmark]) * 100   # cm, Y up, +Z to camera
                pts.append(w); img2d.append(r.pose_landmarks); vis.append([q.visibility for q in r.pose_landmarks.landmark])
            else:
                pts.append(pts[-1] if pts else None); img2d.append(None)
    first = next(p for p in pts if p is not None)
    P = np.array([p if p is not None else first for p in pts])
    k = 5; pad = np.pad(P, ((k // 2, k // 2), (0, 0), (0, 0)), mode="edge")   # light smoothing (less jitter)
    P = np.mean([pad[i:i + len(P)] for i in range(k)], axis=0)
    k = 11; pad = np.pad(P[:, :11], ((k // 2, k // 2), (0, 0), (0, 0)), mode="edge")   # face points: smooth more
    P[:, :11] = np.mean([pad[i:i + len(P)] for i in range(k)], axis=0)
    return P, fps, frames, img2d, np.mean(vis, axis=0)


def targets(p):
    """global rotation of every joint for one frame of landmarks p (33x3)."""
    mid = lambda a, b: (p[a] + p[b]) / 2
    hip, sh = mid(L.LEFT_HIP, L.RIGHT_HIP), mid(L.LEFT_SHOULDER, L.RIGHT_SHOULDER)
    head = mid(L.LEFT_EAR, L.RIGHT_EAR)
    G = {"Hips": frame(p[L.LEFT_HIP] - p[L.RIGHT_HIP], sh - hip),
         "Spine": frame(p[L.LEFT_SHOULDER] - p[L.RIGHT_SHOULDER], sh - hip)}
    # head: look direction only (nose - ears), NO roll from the ears (the hidden ear is a guess -> head fell sideways)
    up = G["Spine"][:, 1]; f = unit(p[L.NOSE] - head)
    f = unit(np.cos(0.21) * f + np.sin(0.21) * up)      # nose sits below the ears: lift ~12 deg so rest = level
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
    prev = {}
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
        s.append(" ".join("%.4f" % v for v in row))
    open(out, "w").write("\n".join(s) + "\n")
    return off, leg


def fk(row, off, leg):   # replay the BVH row -> joint positions (to check the file, not the landmarks)
    pos, rot, i = {}, {}, 3
    for j in ORDER:
        R = Rzxy(*row[i:i + 3]); i += 3; par = J[j][0]
        if par is None: rot[j] = R; pos[j] = np.array([0, leg, 0.0])
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
        if lm: mp.solutions.drawing_utils.draw_landmarks(a, lm, mp.solutions.pose.POSE_CONNECTIONS)
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
    copy = ("Right", "Left") if vl < 0.4 and vr > 0.7 else ("Left", "Right") if vr < 0.4 and vl > 0.7 else None
    print("arm visibility L %.2f R %.2f%s" % (vl, vr, "  -> %s arm hidden: mirror of the %s arm" % (copy[1], copy[0]) if copy else ""))
    off, leg = write_bvh(sys.argv[2], P, fps, copy)
    print("BVH %s: %d frames @ %.0f fps" % (sys.argv[2], len(P), fps))
    if len(sys.argv) > 3: check_video(sys.argv[3], sys.argv[2], off, leg, frames, img2d, fps); print("CHECK", sys.argv[3])
