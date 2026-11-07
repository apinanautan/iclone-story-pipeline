# Contact sheet: put PNG stills side by side (3 per row, file name on each) so the whole shot list is checked at once.
# Usage:  python scripts/contact_sheet.py "<glob of PNGs>" <out.jpg>
# e.g.    python scripts/contact_sheet.py "%LOCALAPPDATA%\Tidmunz Studio\snapgen_data\ic8_jobs\c3_*.png" sheet.jpg
import glob, os, sys
from PIL import Image, ImageDraw

files = sorted(glob.glob(os.path.expandvars(sys.argv[1])))
out = sys.argv[2]
W, H, COLS = 480, 270, 3
rows = (len(files) + COLS - 1) // COLS
sheet = Image.new("RGB", (W * COLS, H * rows))
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB").resize((W, H))
    ImageDraw.Draw(im).text((6, 6), os.path.basename(f), fill="yellow")
    sheet.paste(im, ((i % COLS) * W, (i // COLS) * H))
sheet.save(out, quality=85)
print(out, len(files), "images")
