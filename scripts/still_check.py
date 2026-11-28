# Check review stills for capture glitches (user 2026-11-20: stills of ONE shot jumped between two framings).
# Usage:  python scripts/still_check.py "<glob of cam_NN_KK_TTT.Ts.png>"      exit 1 + "FAIL ..." lines on problems
# Inside one shot the camera moves only 5-20 cm, so neighbouring stills must look almost the same.
#  - JUMP: a neighbour differs far more than the shot's typical step. This is a QA alert, not proof of a stale camera.
#  - FLIP: still k looks like k-2 but not like k-1 (A-B-A) = stale frame captured, not a real camera move.
import argparse, glob, os, re, sys
from collections import defaultdict
import numpy as np
from PIL import Image

JUMP_ABS = 4.0      # framing shift in % of frame width between neighbours: above this = jump
JUMP_REL = 3.0       # and this many times the shot's median step
FLIP_RATIO = 0.4     # shift(k-2,k) < 40% of shift(k-1,k) -> A-B-A
TW, TH, R = 160, 90, 16


def thumb(f):
    g = np.asarray(Image.open(f).convert("L").resize((TW, TH)), dtype=np.float32)
    gx = np.abs(np.diff(g, axis=1))[:-1, :]; gy = np.abs(np.diff(g, axis=0))[:, :-1]
    return gx + gy                                       # edges: walls/furniture lines, not flat brightness


def diff(a, b):
    """Framing shift between two stills in % of frame width (best x/y translation of the edge map)."""
    h, w = a.shape; best, bd = None, (0, 0)
    for dy in range(-R // 2, R // 2 + 1):
        for dx in range(-R, R + 1):
            A = a[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)]
            B = b[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
            e = float(np.abs(A - B).mean())
            if best is None or e < best: best, bd = e, (dx, dy)
    return 100.0 * (bd[0] ** 2 + bd[1] ** 2) ** 0.5 / w


def stable_background(a, b):
    """Separate character gestures from a camera jump using visible scenery at the edges.
    The capture job also verifies actual iClone camera coordinates against planned keys."""
    h, w = a.shape
    shifts = []
    for xa, xb in ((0, int(w * .22)), (int(w * .78), w)):
        x, y = a[:, xa:xb], b[:, xa:xb]
        if min(np.count_nonzero(x > 5), np.count_nonzero(y > 5)) >= 100:
            shifts.append(diff(x, y) * (xb - xa) / w)
    return bool(shifts) and min(shifts) < 2.0


def check(files, expected_counts=None):
    """Return failures. A clean run requires every expected still, in order, with no duplicate indices."""
    shots = defaultdict(list)
    fails = []
    for f in files:
        m = re.fullmatch(r"cam_(\d+)_(\d+)_0*([\d.]+)s\.png", os.path.basename(f))
        if not m:
            fails.append("FAIL unrecognised still filename: " + os.path.basename(f))
            continue
        shots[int(m.group(1))].append((int(m.group(2)), float(m.group(3)), f))
    if not shots:
        return fails + ["FAIL no still images (capture did not produce review frames)"]
    if expected_counts is not None:
        if any(c < 1 for c in expected_counts):
            return ["FAIL invalid expected still counts"]
        if set(shots) != set(range(1, len(expected_counts) + 1)):
            fails.append("FAIL missing/unexpected shots: found %s, expected 1..%d" %
                         (sorted(shots), len(expected_counts)))
    for s, items in sorted(shots.items()):
        items.sort()
        indices = [i for i, _, _ in items]
        if indices != list(range(1, len(items) + 1)):
            fails.append("FAIL S%02d duplicated/missing still indices: %s" % (s, indices))
        if expected_counts is not None and 1 <= s <= len(expected_counts):
            if len(items) != expected_counts[s - 1]:
                fails.append("FAIL S%02d captured %d/%d expected stills" %
                             (s, len(items), expected_counts[s - 1]))
        elif expected_counts is None and len(items) < 3:
            fails.append("FAIL S%02d only %d stills; need at least 3 for a motion check" % (s, len(items)))
        try:
            ims = [thumb(f) for _, _, f in items]
        except Exception as e:
            fails.append("FAIL S%02d unreadable image: %s" % (s, e))
            continue
        steps = [diff(ims[k - 1], ims[k]) for k in range(1, len(ims))]
        if not steps:
            continue
        med = float(np.median(steps))
        for k, d in enumerate(steps, 1):
            if d > JUMP_ABS and d > JUMP_REL * max(med, 1.0):
                if stable_background(ims[k - 1], ims[k]):
                    print("WARN S%02d subject moved %.1f%% but background stayed fixed at %.1fs" % (s, d, items[k][1]))
                else:
                    fails.append("FAIL S%02d JUMP %.1fs->%.1fs shift %.1f%% (shot median %.1f%%)" %
                                 (s, items[k - 1][1], items[k][1], d, med))
        for k in range(2, len(ims)):
            d1, d2 = steps[k - 1], diff(ims[k - 2], ims[k])
            if d1 > JUMP_ABS and d2 < FLIP_RATIO * d1:
                if stable_background(ims[k - 1], ims[k]) and stable_background(ims[k - 2], ims[k]):
                    print("WARN S%02d performer reverses gesture %.1fs; background unchanged" % (s, items[k][1]))
                else:
                    fails.append("FAIL S%02d FLIP %.1fs similar to %.1fs, not %.1fs (inspect capture)" %
                                 (s, items[k][1], items[k - 2][1], items[k - 1][1]))
        print("S%02d %d stills, estimated shifts %s" %
              (s, len(ims), " ".join("%.1f%%" % d for d in steps)))
    return fails


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline framing-shift checks for iClone stills")
    parser.add_argument("pattern", help="Glob of cam_NN_KK_TTT.Ts.png files")
    parser.add_argument("--expected-counts", default=None,
                        help="Comma-separated expected frame counts per shot (required by ic8_part.py cams)")
    args = parser.parse_args()
    counts = None
    if args.expected_counts is not None:
        try:
            counts = [int(c) for c in args.expected_counts.split(",")]
        except ValueError:
            parser.error("--expected-counts must be comma-separated integers")
    fs = check(sorted(glob.glob(os.path.expandvars(args.pattern))), counts)
    for fail in fs:
        print(fail)
    print("OK stills" if not fs else "STILLS NOT VALID: inspect and recapture; do not show these to the user")
    sys.exit(1 if fs else 0)
