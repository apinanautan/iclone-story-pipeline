# Contact sheet: big stills joined into 4K pages so faces/motion can be zoomed and read (user 2026-11-17).
# Usage:  python scripts/contact_sheet.py "<glob of PNGs>" <out.jpg>
# Stills named cam_NN_KK_TTT.Ts.png (ic8_cams "per_sec": 1 = ~1 still per second, 3-8 per shot).
# Layout: 4K page 3840x2160 = 4 x 4 tiles of 960x540 (each tile = half of a 1080p frame, sharp).
#   Each shot starts on a new row; every tile has a yellow border and a big label "S03-02  12.4s"
#   (shot 3, frame 2, at 12.4 s on the timeline). More tiles -> out_p2.jpg, out_p3.jpg ...
# Other file names: same tiles, label = file name.
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont

COLS, ROWS, W, H, B = 4, 4, 960, 540, 6          # B = border px
files = sorted(glob.glob(os.path.expandvars(sys.argv[1])))
out = sys.argv[2]
try: font = ImageFont.truetype("arialbd.ttf", 44)
except OSError: font = ImageFont.load_default()

def label(f):
    m = re.match(r"cam_(\d+)_(\d+)_0*([\d.]+)s", os.path.basename(f))
    return ("S%s-%s  %.1fs" % (m.group(1), m.group(2), float(m.group(3))), m.group(1)) if m else (os.path.basename(f)[:-4], None)

cells, col, shot = [], 0, None                     # (row, col, file); a new shot starts a new row
row = 0
for f in files:
    text, s = label(f)
    if cells and (col == COLS or (s is not None and s != shot)): row += 1; col = 0
    cells.append((row, col, f, text)); col += 1; shot = s
pages = {}
for r, c, f, t in cells: pages.setdefault(r // ROWS, []).append((r % ROWS, c, f, t))
for p, cs in sorted(pages.items()):
    sheet = Image.new("RGB", (COLS * W, ROWS * H), (20, 20, 20))
    for r, c, f, t in cs:
        im = Image.open(f).convert("RGB").resize((W - 2 * B, H - 2 * B), Image.LANCZOS)
        tile = Image.new("RGB", (W, H), (255, 220, 0)); tile.paste(im, (B, B))
        d = ImageDraw.Draw(tile); x0, y0, x1, y1 = d.textbbox((0, 0), t, font=font)
        d.rectangle((B, B, B + x1 - x0 + 24, B + y1 - y0 + 20), fill=(0, 0, 0))
        d.text((B + 12 - x0, B + 10 - y0), t, font=font, fill=(255, 220, 0))
        sheet.paste(tile, (c * W, r * H))
    used = max(r for r, *_ in cs) + 1
    sheet = sheet.crop((0, 0, COLS * W, used * H))   # last page: no empty rows
    o = out if p == 0 else out[:-4] + "_p%d.jpg" % (p + 1)
    sheet.save(o, quality=90)
    print(o, len(cs), "images", sheet.size)
