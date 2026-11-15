"""ic8_story.py - everything about a story lives in stories/<story>.json; the AI reads the brief instead of hunting.

  python scripts/ic8_story.py <story> init          NEW story: copy stories/_template.json -> stories/<story>.json, then fill it
  python scripts/ic8_story.py <story> close         story finished: stories/<story>.json + parts/<story>_* -> Recycle Bin
  python scripts/ic8_story.py <story> scan <scene> after ic8_scene_scan.py ran in iClone: store objects + room in the story file
  python scripts/ic8_story.py <story> list          all parts: time range, scenes, status, which files exist
  python scripts/ic8_story.py <story> brief <N>     one part, as points: what/where/who/when/script text/plan/files
  python scripts/ic8_story.py <story> new <N>       write parts/<story>_<N>.json (spec for ic8_part.py) from the story file

No iClone. Read-only except `new` (writes into parts/, refuses to overwrite).

stories/<story>.json:
 name, folder, script_docx, script_split ("(AD.)"), master_audio, audio_dir (ท่อนN.wav [+ ท่อนN.json transcript]),
 save_dir, video_dir, publish_dir, teacher_range [s,e] (seconds of master the teacher wants),
 reference_clips {N: mp4 to continue from},
 characters {name: {role, voice, avatar}},          name = the avatar's name inside iClone
 scenes {name: {file, notes}},
 parts [{n, master [s,e], content, scenes [..], script_block, cast [..], plan, status}]
"""
import json, os, re, sys, zipfile, glob, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def say(s=""): print(s, flush=True)
def fail(s): say("FAIL: " + s); sys.exit(1)
def mmss(t): return "%d:%04.1f" % (t // 60, t % 60)
def ok(p): return "OK " if p and os.path.exists(p) else "MISSING "


def load(story):
    p = os.path.join(ROOT, "stories", story + ".json")
    if not os.path.exists(p): fail("no story file " + p)
    return json.load(open(p, encoding="utf-8"))


def part(S, n):
    for i, P in enumerate(S["parts"]):
        if P["n"] == str(n): return i, P
    fail("part %s not in story file (add it to parts)" % n)


def paths(S, n):
    return {"wav": "%s/ท่อน%s.wav" % (S["audio_dir"], n),
            "transcript": "%s/ท่อน%s.json" % (S["audio_dir"], n),
            "project": "%s/ท่อน%s.iProject" % (S["save_dir"], n),
            "video": "%s/%s.mp4" % (S["video_dir"], n)}


def docx_blocks(S):
    p = S.get("script_docx")
    if not p or not os.path.exists(p): return []
    xml = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
    paras = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)]
    text = "\n".join(x for x in paras if x.strip())
    return [b.strip() for b in text.split(S.get("script_split", "(AD.)"))]


def transcript(path):
    if not os.path.exists(path): return []
    d = json.load(open(path, encoding="utf-8"))
    segs = d.get("segments", d) if isinstance(d, dict) else d
    return [(float(s["start"]), float(s["end"]), s["text"].strip()) for s in segs if "start" in s]


def cmd_list(S):
    say("%s  teacher range %s-%s" % (S["name"], mmss(S["teacher_range"][0]), mmss(S["teacher_range"][1])))
    for P in S["parts"]:
        f = paths(S, P["n"]); a, b = P["master"]
        flags = " ".join(k + ("+" if os.path.exists(f[k]) else "-") for k in ("wav", "project", "video"))
        say("ท่อน%-3s %s-%s (%4.1fs) %-8s %-40s %s | %s" % (P["n"], mmss(a), mmss(b), b - a, P.get("status", ""),
                                                   ",".join(P.get("scenes", [])) or "scene ?", flags, P.get("content", "")))


def cmd_brief(S, n):
    i, P = part(S, n); f = paths(S, n); a, b = P["master"]
    prev = S["parts"][i - 1] if i else None
    say("# %s ท่อน%s  (part %d of %d; teacher range ends %s)" % (S["name"], n, i + 1, len(S["parts"]), mmss(S["teacher_range"][1])))
    say("- master audio %s-%s = %.1f s   status: %s" % (mmss(a), mmss(b), b - a, P.get("status", "todo")))
    say("- content: " + P.get("content", "?"))
    say("- plan: " + (P.get("plan") or "(none yet: write it in stories/%s.json before building)" % S["name"]))
    say("- wav: %s%s" % (ok(f["wav"]), f["wav"]))
    say("- continue from: " + (("ท่อน%s %s%s" % (prev["n"], ok(paths(S, prev["n"])["project"]), paths(S, prev["n"])["project"])) if prev else "first part"))
    if S.get("reference_clips", {}).get(str(n)): say("- reference clip (match it): " + S["reference_clips"][str(n)])
    for sc in P.get("scenes", []) or ["?"]:
        d = S["scenes"].get(sc, {})
        say("- scene %s: %s%s %s" % (sc, ok(d.get("file")), d.get("file", "not in scenes list"), d.get("notes", "")))
        b = d.get("room") or d.get("area")
        if b: say("  - %s %s x %s..%s  y %s..%s" % (d.get("type", "indoor"), "room" if d.get("room") else "area", b[0], b[2], b[1], b[3]))
        elif d: say("  - room NOT measured: open the scene, run ic8_scene_scan.py, then: ic8_story.py %s scan %s" % (S["name"], sc))
        for n in d.get("notes_list", []): say("  - RULE: " + n)
        for k, v in d.get("spots", {}).items():
            say("  - spot %-24s %s yaw %s %s%s" % (k, v.get("pos"), v.get("yaw"), "" if v.get("approved") else "(NOT approved) ", v.get("notes", "")))
        for k, v in d.get("cams", {}).items():
            say("  - cam  %-24s %smm %s%s" % (k, v.get("focal"), "" if v.get("approved") else "(NOT approved) ", v.get("notes", "")))
    cast = P.get("cast") or []
    say("- cast: " + (", ".join(cast) if cast else "(not set: decide from the script text below)"))
    for c in cast:
        d = S["characters"].get(c)
        if not d: say("  - %s: NOT in characters list" % c); continue
        say("  - %s (%s, voice %s): %s%s" % (c, d.get("role", ""), d.get("voice", ""), ok(d.get("avatar")), d.get("avatar")))
    say("- outputs: project %s%s | video %s%s" % (ok(f["project"]), f["project"], ok(f["video"]), f["video"]))
    bl = P.get("script_block"); blocks = docx_blocks(S)
    if bl and 0 < bl <= len(blocks):
        say("\n## script block %d (docx, find this part's lines inside it)\n%s" % (bl, blocks[bl - 1]))
    tr = transcript(f["transcript"])
    if tr:
        say("\n## transcript (part-local seconds; who = match with the script)")
        for s, e, t in tr: say("  %6.2f-%6.2f %s" % (s, e, t))
    say("\n## next: python scripts/ic8_story.py %s new %s  ->  python scripts/ic8_part.py parts/%s_%s.json audio" % (S["name"], n, S["name"], n))
    say("rules: docs/DELIVERY_CHECKLIST.md | max 2 parts per chat")


def cmd_new(S, n):
    i, P = part(S, n); f = paths(S, n)
    out = os.path.join(ROOT, "parts", "%s_%s.json" % (S["name"], n))
    if os.path.exists(out): fail("exists: %s (edit it instead)" % out)
    prev = S["parts"][i - 1] if i else None
    frm = paths(S, prev["n"])["project"] if prev else S["scenes"].get((P.get("scenes") or ["?"])[0], {}).get("file", "")
    lines = [{"who": "?", "t": [round(s, 2), round(e, 2)], "text": t} for s, e, t in transcript(f["transcript"])]
    spec = {"story": S["name"], "part": str(n), "wav": f["wav"], "from": frm, "project": f["project"], "video": f["video"],
            "publish": S.get("publish_dir"), "scene": (P.get("scenes") or [""])[0], "lines": lines,
            "cast": {c: {"lookfront": True} for c in P.get("cast", [])}, "hide": [], "shots": []}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(spec, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    say("OK wrote %s\nfill: lines.who (from the brief), cast pos/yaw/motions/lookat, hide, shots; then run ic8_part.py ... audio / check" % out)


if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    if sys.argv[2] == "init":
        dst = os.path.join(ROOT, "stories", sys.argv[1] + ".json")
        if os.path.exists(dst): fail("exists: " + dst)
        t = open(os.path.join(ROOT, "stories", "_template.json"), encoding="utf-8").read().replace("<เรื่อง>", sys.argv[1])
        t = t.replace("ชื่อเรื่อง (ตรงกับชื่อไฟล์นี้)", sys.argv[1])
        open(dst, "w", encoding="utf-8").write(t); say("OK " + dst + "  (fill characters, scenes, parts)"); sys.exit(0)
    S = load(sys.argv[1]); c = sys.argv[2]
    if c == "close":   # story finished: its data files are trash (user rule). Recycle Bin, not hard delete.
        todo = [P["n"] for P in S["parts"] if P.get("status") != "done"]
        if todo and "--force" not in sys.argv: fail("parts not done: %s (mark them done, or --force)" % ", ".join(todo))
        files = [os.path.join(ROOT, "stories", sys.argv[1] + ".json")] + glob.glob(os.path.join(ROOT, "parts", sys.argv[1] + "_*"))
        for f in files:
            subprocess.run(["powershell", "-NoProfile", "-Command", "Add-Type -AssemblyName Microsoft.VisualBasic;"
                            "[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($env:RECYCLE,'OnlyErrorDialogs','SendToRecycleBin')"],
                           env=dict(os.environ, RECYCLE=f))
            if os.path.exists(f): fail("could not recycle " + f)
            say("recycled " + f)
        say("OK closed %s (videos/projects untouched)" % sys.argv[1]); sys.exit(0)
    if c == "scan" and len(sys.argv) > 3:
        sc = sys.argv[3]
        if sc not in S["scenes"]: fail("scene %s not in the story file" % sc)
        d = json.load(open(os.path.join(os.environ["LOCALAPPDATA"], "Tidmunz Studio", "snapgen_data", "ic8_jobs", "scene_scan.json"), encoding="utf-8"))
        objs = [o for o in d["objects"] if o["kind"] in ("prop", "building")]
        S["scenes"][sc]["objects"] = {o["name"]: {"min": o["min"], "max": o["max"]} for o in objs}
        small = [o for o in objs if o["max"][0] - o["min"][0] < 1500 and o["max"][1] - o["min"][1] < 1500]
        key = "area" if S["scenes"][sc].get("type") == "outdoor" else "room"
        if small and not S["scenes"][sc].get(key):
            S["scenes"][sc][key] = [min(o["min"][0] for o in small), min(o["min"][1] for o in small),
                                       max(o["max"][0] for o in small), max(o["max"][1] for o in small)]
            say("room GUESSED from furniture %s: check it on a top view, fix by hand if wrong" % S["scenes"][sc][key])
        json.dump(S, open(os.path.join(ROOT, "stories", sys.argv[1] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        say("OK %d objects stored in scene %s; next: name spots/cams in the story file, show stills, mark approved" % (len(objs), sc)); sys.exit(0)
    if c == "list": cmd_list(S)
    elif c in ("brief", "new") and len(sys.argv) > 3: (cmd_brief if c == "brief" else cmd_new)(S, sys.argv[3])
    else: print(__doc__)
