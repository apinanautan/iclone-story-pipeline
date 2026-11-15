"""Package inspected rental survey evidence; no iClone interaction."""
import hashlib
import json
import os
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont

SRC = Path(os.environ['LOCALAPPDATA']) / 'Tidmunz Studio/snapgen_data/ic8_jobs/spots'
DEST = Path.home() / 'Desktop/ดวงเมียน้อย_ดาต้าเสียง/จุดในฉาก'
APPROVED = 'ABEF'
assert SRC.is_dir() and DEST.is_dir()


def copy_checked(source, destination):
    if destination.exists():
        assert source.read_bytes() == destination.read_bytes(), f'Different destination exists: {destination}'
    else:
        shutil.copy2(source, destination)
    assert source.read_bytes() == destination.read_bytes()


files = []
for n in range(1, 7):
    files.append(f'หน้าห้องเช่าเมียน้อย_wide_{n}_marked.png')
for label in APPROVED:
    files.append(f'หน้าห้องเช่าเมียน้อย_{label}_MCU.png')
for name in files:
    copy_checked(SRC / name, DEST / name)
copy_checked(SRC / 'rental_wide_sheet.jpg', DEST / 'หน้าห้องเช่าเมียน้อย_wide_sheet.jpg')

font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 25)
sheet = Image.new('RGB', (960, 600), '#151515')
for i, label in enumerate(APPROVED):
    x, y = (i % 2) * 480, (i // 2) * 300
    with Image.open(DEST / f'หน้าห้องเช่าเมียน้อย_{label}_MCU.png') as im:
        sheet.paste(im.convert('RGB').resize((480, 270)), (x, y + 30))
    ImageDraw.Draw(sheet).text((x + 10, y), f'{label} | ADULT MCU | REVIEWED', font=font, fill='white')
sheet.save(DEST / 'หน้าห้องเช่าเมียน้อย_MCU_จุดหลัก.jpg', quality=93)

points = json.loads((SRC / 'rental_points.json').read_text(encoding='utf-8'))
for p in points:
    p['adult_mcu_review'] = 'usable' if p['id'] in APPROVED else 'reserve_face_too_dark'
    p['render_pass'] = 'rental_mcu_pass2_F_only' if p['id'] == 'F' else 'rental_mcu_pass1'
    p['horizontal_fov_degrees'] = 25.360763549804688
    p['ground_z_source'] = 'bounds_inferred_not_contact_verified'
    p['image_copied'] = p['id'] in APPROVED
    p['child_framing_verified'] = False
manifest = {
    'description': 'Consolidated reviewed coordinates; not a new six-point render pass.',
    'coordinate_source': str(SRC / 'rental_points.json'),
    'approved_adult_mcu_points': list(APPROVED),
    'points': points,
    'limitations': [
        'Overhead hides whole merged building shell, not just roof.',
        'Wide4 remains partly tree-obstructed.',
        'Ground contact and child/group framing not verified.',
        'Camera remains at F; avatar restoration logged; original pre-survey foliage visibility uncertain.',
        'Existing rental_mcu_meta.json only contains F; use these consolidated coordinates.',
    ],
    'image_sha256': {},
}
for path in DEST.iterdir():
    if path.suffix.lower() in ('.jpg', '.png'):
        with Image.open(path) as im:
            im.verify()
        manifest['image_sha256'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
output = DEST / 'หน้าห้องเช่าเมียน้อย_พิกัด.json'
output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
assert len(manifest['image_sha256']) == 12
print(f'Packaged {len(files)} stills, 2 contact sheets, 6 coordinate records: {DEST}')
print('Approved adult MCU points: A B E F. No iClone calls, project save, or G: writes.')
