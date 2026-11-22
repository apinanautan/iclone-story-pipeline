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
    im = Image.open(path).convert("L"); W, H = im.size
    bw, bh = int(W * BOX_W), int(H * BOX_H); x0, y0 = W // 2 - bw // 2, H // 2 - bh // 2
    left = ImageStat.Stat(im.crop((x0, y0, x0 + bw // 2, y0 + bh))).mean[0]
    right = ImageStat.Stat(im.crop((x0 + bw // 2, y0, x0 + bw, y0 + bh))).mean[0]
    return left, right


def main():
    spec, d = sys.argv[1], sys.argv[2]
    shots = json.load(open(spec, encoding="utf-8"))["shots"]
    bad = []; n = 0
    for f in sorted(glob.glob(os.path.join(d, "cam_*.png"))):
        m = re.match(r"cam_(\d+)_", os.path.basename(f))
        if not m: continue
        i = int(m.group(1)) - 1
        if i >= len(shots) or shots[i].get("wide"): continue
        l, r = halves(f); hi, lo = max(l, r), min(l, r); n += 1
        if (hi > HOT and lo < DARK) or (hi + 5) / (lo + 5) > RATIO:
            bad.append("BAD shot %d %s: face left %.0f / right %.0f (half white/black)" % (i + 1, os.path.basename(f), l, r))
    for b in bad: print(b)
    print("light check: %d stills, %d bad" % (n, len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
