# Contact sheet: stills side by side so the whole shot list is checked at once.
# Usage:  python scripts/contact_sheet.py "<glob of PNGs>" <out.jpg>
# Standard (user 2026-11-17): stills named cam_NN_* (ic8_cams "per_sec": 1 = ~1 still per second, 3-8 per shot)
# -> ONE ROW PER SHOT, tiles 384x216 (big enough to read faces/motion), max 8 shots per page:
#    out.jpg, out_p2.jpg, ... Other names -> 3 per row as before.
import glob, os, re, sys
from collections import OrderedDict
from PIL import Image, ImageDraw

files = sorted(glob.glob(os.path.expandvars(sys.argv[1])))
out = sys.argv[2]
rows = OrderedDict()
for f in files:
    m = re.match(r"(cam_\d+)_", os.path.basename(f))
    rows.setdefault(m.group(1) if m else len(rows) // 3, []).append(f)
if not all(isinstance(k, str) for k in rows):            # not cam_NN names: plain grid, 3 per row
    rows = OrderedDict((i, files[i:i + 3]) for i in range(0, len(files), 3))
W, H, PER_PAGE = 384, 216, 8
keys = list(rows)
cols = max(len(v) for v in rows.values()) if rows else 1
for p in range(0, max(len(keys), 1), PER_PAGE):
    page = keys[p:p + PER_PAGE]
    sheet = Image.new("RGB", (W * cols, H * len(page)), "black")
    for r, k in enumerate(page):
        for c, f in enumerate(rows[k]):
            im = Image.open(f).convert("RGB").resize((W, H))
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, W, 16), fill="black"); d.text((4, 2), os.path.basename(f)[:-4], fill="yellow")
            sheet.paste(im, (c * W, r * H))
    o = out if p == 0 else out[:-4] + "_p%d.jpg" % (p // PER_PAGE + 1)
    sheet.save(o, quality=88)
    print(o, sum(len(rows[k]) for k in page), "images")
