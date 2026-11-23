"""cam_check.py - the AI MUST really check every camera angle of a part (user 2026-11-23: "it still does not
really check the cameras"). Step `cam_check` of ic8_part.py, right after `cams`. No iClone: reads the stills only.

  python scripts/cam_check.py parts/<story>_<N>.json        (ic8_part.py <spec> cam_check runs the same)

1. ALL shots in ONE image: ic8_jobs/part_cams_all.jpg (1 still per shot, the middle one; label = shot, time,
   lens, who speaks). One image = the AI sees the whole part at once (same angle twice, jumps, who is missing).
2. Check file progress/<story>_<N>_camcheck.json: one entry per shot. The AI looks at the image and fills
   "see" (what is REALLY in the frame, Thai or English, >= 10 letters) and true/false for every question.
   A shot whose still did not change keeps its old answers (cams --shot N re-shoots only N).
3. Exit 0 = every shot passes. Exit 3 = AI work: the file still has blanks (fill it, run again).
   Exit 1 = some shots fail: fix those shots in the spec, `ic8_part.py <spec> cams --shot a,b`, then again.
"""
import glob, hashlib, json, math, os, re, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tidmunz Studio", "snapgen_data", "ic8_jobs")
SHEET = "part_cams_all.jpg"
# question -> what must be true (shown in the file and the card)
ASK = {
    "subject_face": "the speaker (or the subject of the narration) is in frame and we see the FACE: front or 3/4, not the back/profile only, not dark",
    "framing": "no head cut at the top, nobody sliced by the frame edge, no big empty wall/sky/ground, not full-body-and-legs (except the wide shot)",
    "clean": "no body through a chair/table/bed, nobody floating, no missing/glitchy models, nothing blocking the face",
    "differs": "clearly different from the shot before it (not the same angle only nearer/farther); shot 1 = true",
}


def font(size):
    for f in ("LeelaUIb.ttf", "leelawdb.ttf", "tahomabd.ttf", "arialbd.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()


def md5(f):
    return hashlib.md5(open(f, "rb").read()).hexdigest()[:12]


def who_at(S, t):
    for L in S.get("lines", []):
        if L["t"][0] <= t <= L["t"][1]:
            w = L.get("who", "?")
            return w + (" (%s)" % ", ".join(L.get("about", [])[:1]) if w in ("บรรยาย", "narrator") and L.get("about") else "")
    return "-"


def stills(n_shots, jobs=J):
    """{shot: middle still} from cams (cam_SS_KK_TTT.Ts.png)."""
    by = {}
    for f in sorted(glob.glob(os.path.join(jobs, "cam_*.png"))):
        m = re.match(r"cam_(\d+)_(\d+)_", os.path.basename(f))
        if m: by.setdefault(int(m.group(1)), []).append(f)
    return {s: fs[len(fs) // 2] for s, fs in by.items() if 1 <= s <= n_shots}


def make_sheet(S, pick, out):
    n = len(S["shots"]); cols = 3 if n <= 9 else 4 if n <= 16 else 5
    W = 1920 // cols; H = W * 9 // 16; rows = math.ceil(n / cols)
    sheet = Image.new("RGB", (cols * W, rows * H), (20, 20, 20)); f = font(max(18, W // 22))
    for i, sh in enumerate(S["shots"], 1):
        r, c = divmod(i - 1, cols)
        tile = Image.new("RGB", (W, H), (255, 220, 0))
        if i in pick: tile.paste(Image.open(pick[i]).convert("RGB").resize((W - 8, H - 8), Image.LANCZOS), (4, 4))
        else: ImageDraw.Draw(tile).rectangle((4, 4, W - 4, H - 4), fill=(90, 0, 0))
        t0, t1 = sh["t"]
        lab = "S%02d %.1f-%.1fs %s  พูด: %s" % (i, t0, t1, "WIDE" if sh.get("wide") else "%smm" % sh.get("focal", "?"),
                                               who_at(S, (t0 + t1) / 2))
        d = ImageDraw.Draw(tile); x0, y0, x1, y1 = d.textbbox((0, 0), lab, font=f)
        d.rectangle((4, 4, 4 + x1 - x0 + 16, 4 + y1 - y0 + 12), fill=(0, 0, 0))
        d.text((12 - x0, 10 - y0), lab, font=f, fill=(255, 220, 0))
        sheet.paste(tile, (c * W, r * H))
    sheet.save(out, quality=90)


def check(S, jobs=J, prog=os.path.join(ROOT, "progress")):
    """returns (code, message). code 0 pass, 3 AI must fill the file, 1 shots fail."""
    n = len(S.get("shots", []))
    if not n: return 1, "FAIL cam_check: the spec has no shots"
    pick = stills(n, jobs)
    miss = [i for i in range(1, n + 1) if i not in pick]
    if miss: return 1, "FAIL cam_check: no still for shot %s -> run cams first (ic8_part.py <spec> cams)" % ",".join(map(str, miss))
    out = os.path.join(jobs, SHEET); make_sheet(S, pick, out)
    vf = os.path.join(prog, "%s_%s_camcheck.json" % (S.get("story"), S.get("part")))
    old = {}
    try: old = {e.get("img"): e for e in json.load(open(vf, encoding="utf-8")).get("shots", [])}
    except Exception: pass
    shots = []
    for i, sh in enumerate(S["shots"], 1):
        h = md5(pick[i]); e = old.get(h) or {}
        shots.append({"shot": i, "t": sh["t"], "who": who_at(S, sum(sh["t"]) / 2), "img": h,
                      "see": e.get("see", ""), **{k: e.get(k) for k in ASK}, "fix": e.get("fix", "")})
    doc = {"image": out, "how": "Open the image. For EVERY shot write 'see' = what is really in the frame, and true/false "
           "for each question. false -> write 'fix' (what to change in the spec). Do not guess from the plan: the image wins.",
           "questions": ASK, "shots": shots}
    os.makedirs(prog, exist_ok=True)
    json.dump(doc, open(vf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    blank = [e["shot"] for e in shots if len(e["see"].strip()) < 10 or any(e[k] is None for k in ASK)]
    if blank:
        return 3, ("AI WORK cam_check: open %s (ALL %d shots in one image) and fill %s for shots %s.\n"
                   "Each shot: see = what is really in the frame; true/false: %s. Then run again."
                   % (out, n, vf, ",".join(map(str, blank)), ", ".join(ASK)))
    bad = [e for e in shots if not all(e[k] is True for k in ASK)]
    if bad:
        return 1, ("FAIL cam_check: shots %s do not pass:\n%s\nFix those shots in the spec, then "
                   "ic8_part.py <spec> cams --shot %s, then cam_check again."
                   % (",".join(str(e["shot"]) for e in bad),
                      "\n".join("  S%02d %s -> %s" % (e["shot"], ",".join(k for k in ASK if e[k] is not True), e["fix"] or "(write fix)")
                                for e in bad),
                      ",".join(str(e["shot"]) for e in bad)))
    return 0, "OK cam_check: all %d shots pass (%s)" % (n, out)


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paths import expand
    code, msg = check(expand(json.load(open(sys.argv[1], encoding="utf-8"))))
    print(msg); sys.exit(code)
