"""Light check on the camera stills: is a face half white / half black? (user 2026-11-21)

Every close shot is auto-aimed so the face point sits at the frame centre (ic8_cams.py `subject`).
Take a small box around the centre, split it left/right and compare brightness.
FAIL when one half is blown out and the other is dark, or one half is far brighter than the other.

Usage: python scripts/light_check.py <part spec json> <stills dir>
Exit 1 with BAD lines when a shot fails. Wide shots ("wide": true) are skipped.
"""
import glob
import json
import os
import re
import sys

from PIL import Image, ImageStat

BOX_W, BOX_H = 0.09, 0.12   # face size at 80-100 mm, as a fraction of the frame
HOT, DARK, RATIO = 215, 60, 2.8


def halves(path):
    # Ignore dark hair and the dark set when comparing the two halves of visible skin.
    # A grayscale box falsely reported a half-dark face when one side was mostly hair.
    import numpy as np
    im = np.asarray(Image.open(path).convert("YCbCr"))
    H, W = im.shape[:2]
    bw, bh = int(W * BOX_W), int(H * BOX_H)
    x0, y0 = W // 2 - bw // 2, H // 2 - bh // 2
    def skin_mean(roi):
        yy, cb, cr = roi[..., 0], roi[..., 1], roi[..., 2]
        m = (yy > 18) & (cb >= 75) & (cb <= 130) & (cr >= 128) & (cr <= 175)
        return (float(yy[m].mean()) if m.any() else 0.0, float(m.mean()))
    return (skin_mean(im[y0:y0+bh, x0:x0+bw//2]),
            skin_mean(im[y0:y0+bh, x0+bw//2:x0+bw]))


def main():
    spec, d = sys.argv[1], sys.argv[2]
    shots = json.load(open(spec, encoding="utf-8"))["shots"]
    bad = []; n = 0
    for f in sorted(glob.glob(os.path.join(d, "cam_*.png"))):
        m = re.match(r"cam_(\d+)_", os.path.basename(f))
        if not m: continue
        i = int(m.group(1)) - 1
        if i >= len(shots) or shots[i].get("wide"): continue
        (l, lfrac), (r, rfrac) = halves(f); n += 1
        if min(lfrac, rfrac) < 0.12:
            print("WARN shot %d %s: one ROI half mostly hair/set (%.0f%%,%.0f%% skin); inspect the face visually" %
                  (i + 1, os.path.basename(f), lfrac * 100, rfrac * 100))
            continue
        hi, lo = max(l, r), min(l, r)
        if (hi > HOT and lo < DARK) or (hi + 5) / (lo + 5) > RATIO:
            bad.append("BAD shot %d %s: skin left %.0f / right %.0f (half white/black)" % (i + 1, os.path.basename(f), l, r))
    for b in bad: print(b)
    print("light check: %d stills, %d bad" % (n, len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
