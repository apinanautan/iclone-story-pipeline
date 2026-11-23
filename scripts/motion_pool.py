# -*- coding: utf-8 -*-
"""motion_pool.py - pick body motions per line from the WHOLE library, not a hand list of 25 clips.

User 2026-11-23: "กูเจอแต่โมชั่นซ้ำๆ ... ยืนกอดอกก็ยืนกอดอกทั้งเรื่อง" - the acting skill listed ~25 standing
clips, so Stand03 / StandTKI came back in every part. The library ({MOTION}, ~6000 clips) has stand/sit x
talk/listen x calm/sad/angry/happy/fear clips for men and women.

  python scripts/motion_pool.py index [--rebuild]       scan {MOTION} -> progress/motion_index.json (per PC)
  python scripts/motion_pool.py find <words...>         search the index (tags + name)
  python scripts/motion_pool.py pick <story> <part> [--write]
        for every standing/sitting person (work clips like Brick Laying are kept): follow the lines -
        speaks -> talk clip, someone else speaks -> listen clip, narrator -> idle clip; mood from
        line "mood" / cast "mood" (calm sad angry happy fear); one clip per ~14 s on screen (2+ when > 20 s);
        least used in the story first, never a clip another person in this part has, never one already in
        2 other parts, arms folded only for an angry mood and 1 person per part.
        --write puts the list in parts/<story>_<part>.json cast.<name>.motions (pose changes it at camera cuts).
Only packs made for acting are used (no combat, weapons, dance, swim, sleep, sex, riding, ghosts, walking).
"""
import json, math, os, re, sys, time, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from paths import root  # noqa: E402

INDEX = os.path.join(ROOT, "progress", "motion_index.json")
EXT = (".imotion", ".rlmotion")
# acting packs (path part, lower case) -> priority (0 = made for conversation, best first)
PACKS = [("mixmoves communication 200", 0), ("motion_-_talklisten", 0), ("studio mocap/conversation", 0),
         ("03_cc mixmove_male", 1), ("04_cc mixmove_female", 1), ("mographmotion", 1), ("life convos", 1), ("studio mocap-city life/chat", 1), ("mixamo", 2)]
NO = re.compile(r"_to_|stand_?to_?sit|sit_?to_?stand|walk|run|jog|turn|step|moving|stroll|pivot|strafe|jump|"
                r"crouch|kneel|lay|laying|sleep|lying|zombie|attack|punch|kick|fight|box|sword|rifle|pistol|gun|"
                r"aim|reload|dance|danc|swim|death|dying|fall|hit_?reac|taunt|melee|magic|spell|cast|throw|"
                r"climb|crawl|drunk|injur|flip|ninja|torch|stomp|sexy|twerk|samba|salsa|capoeira|hip_?hop|mma", re.I)
# Mixamo has ~2500 clips, mostly action: only these names are acting clips
MIXAMO_OK = re.compile(r"^(talking|standing_idle|idle|happy_idle|sad_idle|female_standing_pose|standing_pose|"
                       r"agreeing|acknowledging|head_nod|thoughtful_head_shake|nervously_look_around|looking|"
                       r"thinking|sitting_talking|sitting_idle|sitting|arguing|explaining|disappointed|yelling|"
                       r"crying|annoyed_head_shake|angry|laughing|rejected|relieved_sigh|whatever_gesture|"
                       r"shrugging|weight_shift|bored|listening)", re.I)
SIT = re.compile(r"sit|chair|seat|sofa|bench|legs[ _]crossed|leaning forward|graceful", re.I)
TALK = re.compile(r"talk|explain|convo|discuss|argu|chat_|yell|nagging|sincere|aggress|introduce|"
                  r"query|inquire|bossy|rage|passion|direction", re.I)
LISTEN = re.compile(r"listen|response|agree|nod|curious|focus|acknowledg|apolog", re.I)
MOODS = [("angry", re.compile(r"angry|anger|rage|irritat|impatient|aggress|agress|argu|bossy|disagree|yell|furious|"
                              r"arms[ _]*crossed|hips|decline|nagging|annoyed|dumbness", re.I)),
         ("sad", re.compile(r"sad|cry|disappoint|depress|lose|apolog|reject|sigh", re.I)),
         ("fear", re.compile(r"fear|scared|nervous|worr|afraid|shock|spooked|panic", re.I)),
         ("happy", re.compile(r"happy|laugh|joy|cheer|passion|excit|pleased|greet|met_", re.I))]
CROSSED = re.compile(r"arms[ _]*crossed|hands? on hips|mographmotion/02_female/(stand03|standtki)\.imotion$", re.I)


def tags(rel):
    low = rel.replace("\\", "/").lower(); name = os.path.splitext(os.path.basename(low))[0]
    pri = next((p for k, p in PACKS if k in low), None)
    if pri is None or NO.search(name): return None
    if pri == 2 and not MIXAMO_OK.match(name): return None
    if "mographmotion" in low or "mixmove_" in low:      # these packs: only Stand* / Sit* idles
        if not re.match(r"(stand|sit)", name): return None
    sex = "F" if re.search(r"female|(^|[_ ])f(\d\d?)?$|_f_|_f\d", name) or "_female" in low else \
          "M" if re.search(r"(^|[_ ])m(\d\d?)?$|_m_|_m\d", name) or "_male" in low else "any"
    folder = low.split("/")[-2] if "/" in low else ""      # role from the clip name, else its own folder (Idle_Talk, *_Response)
    role = next((r for t in (name, folder) for r, rx in (("listen", LISTEN), ("talk", TALK)) if rx.search(t)), "idle")
    mood = next((m for m, rx in MOODS if rx.search(name)), "calm")
    return {"path": "{MOTION}/" + rel.replace("\\", "/"), "sit": bool(SIT.search(low)), "sex": sex, "role": role,
            "mood": mood, "crossed": bool(CROSSED.search(low)), "pri": pri}


def index(rebuild=False):
    if not rebuild:
        try:
            d = json.load(open(INDEX, encoding="utf-8"))
            if time.time() - d["time"] < 7 * 86400: return d["clips"]
        except (OSError, ValueError, KeyError): pass
    base = root("MOTION"); clips = []
    for d, _, fs in os.walk(base):
        for f in fs:
            if f.lower().endswith(EXT):
                t = tags(os.path.relpath(os.path.join(d, f), base))
                if t: clips.append(t)
    os.makedirs(os.path.dirname(INDEX), exist_ok=True)
    json.dump({"time": time.time(), "clips": clips}, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False)
    return clips


def key(p):  # same clip whatever the drive / placeholder: last folder + file name (as ic8_part.clip_key)
    return "/".join(p.replace("\\", "/").split("/")[-2:]).lower()


def motions_of(c):
    return c.get("motions", []) + ([c["motion"]] if c.get("motion") else [])


STANDY = re.compile(r"stand|idle|tki|breath|listen|response|talk|sit", re.I)


def is_acting(c):   # replace only standing/sitting/talking clips; keep work clips (Brick Laying, Sawing ...)
    ms = motions_of(c)
    return not ms or all(STANDY.search(os.path.basename(m)) and not re.search(r"bench_|read|relax_01a", m, re.I) for m in ms)


def windows(c, end):
    vis = sorted(c.get("visible") or [[0, 1]]); out = []
    for i, (t0, on) in enumerate(vis):
        t1 = vis[i + 1][0] if i + 1 < len(vis) else end
        if on and t1 > t0: out.append((t0, t1))
    return out


def sex_of(name, c, story):
    """cast "sex" F/M, else the story character's voice / role (variants like อัมพร_คุย use อัมพร)."""
    if c.get("sex") in ("F", "M"): return c["sex"]
    chars = story.get("characters", {})
    tries = [name] + [name.rsplit("_", k)[0] for k in range(1, name.count("_") + 1)]
    for n in tries:
        ch = chars.get(n) or {}
        for v in (ch.get("voice") or "", ch.get("role") or ""):
            if re.search("หญิง|สาว|แม่|ป้า|ยาย|น้า|ภรรยา", v): return "F"
            if re.search("ชาย|พ่อ|ลุง|ปู่|สามี", v): return "M"
    return "any"


def plan(story_name, part, clips=None):
    clips = clips or index()
    pf = os.path.join(ROOT, "parts", "%s_%s.json" % (story_name, part)); S = json.load(open(pf, encoding="utf-8"))
    try: story = json.load(open(os.path.join(ROOT, "stories", story_name + ".json"), encoding="utf-8"))
    except (OSError, ValueError): story = {}
    lines = S.get("lines", []); end = lines[-1]["t"][1] if lines else 60
    other = {}                                   # clip -> parts of this story that use it
    for f in os.listdir(os.path.join(ROOT, "parts")):
        m = re.match(re.escape(story_name) + r"_(\d+)\.json$", f)
        if not m or m.group(1) == str(part): continue
        try: sp = json.load(open(os.path.join(ROOT, "parts", f), encoding="utf-8"))
        except (OSError, ValueError): continue
        for c in sp.get("cast", {}).values():
            for p in motions_of(c): other.setdefault(key(p), set()).add(m.group(1))
    taken = set(); crossed_used = False; out = {}
    for n, c in S["cast"].items():
        if not is_acting(c):
            for p in motions_of(c): taken.add(key(p))
    for n, c in S["cast"].items():
        if not is_acting(c): continue
        sex = sex_of(n, c, story); sit = c.get("posture") == "sit" or any(SIT.search(os.path.basename(p)) for p in motions_of(c))
        base = n.split("_")[0]
        slots = []
        for t0, t1 in windows(c, end):
            k = max(1, math.ceil((t1 - t0) / 14.0))
            if t1 - t0 > 20: k = max(k, 2)
            for i in range(k):
                a = t0 + (t1 - t0) * i / k; b = t0 + (t1 - t0) * (i + 1) / k
                said = [l for l in lines if l["t"][0] < b and l["t"][1] > a]
                me = sum(min(b, l["t"][1]) - max(a, l["t"][0]) for l in said if l.get("who") in (n, base))
                them = sum(min(b, l["t"][1]) - max(a, l["t"][0]) for l in said if l.get("who") not in (n, base, "บรรยาย", None))
                role = "talk" if me >= them and me > 0 else "listen" if them > 0 else "idle"
                moods = [l.get("mood") for l in said if l.get("mood")]
                slots.append((round(a, 1), role, (moods[0] if moods else c.get("mood", "calm"))))
        picks = []
        for si, (t, role, mood) in enumerate(slots):
            def ok(x, role=role, mood=mood, strict=2):
                if x["sit"] != sit or (sex != "any" and x["sex"] not in (sex, "any")) or key(x["path"]) in taken: return False
                if len(other.get(key(x["path"]), ())) >= 2: return False
                if x["crossed"] and (mood != "angry" or crossed_used): return False
                if strict >= 2 and x["role"] != role: return False
                if strict >= 1 and x["mood"] != mood: return False
                return True
            pool = []
            for strict in (2, 1, 0):
                pool = [x for x in clips if ok(x, strict=strict)]
                if strict < 2: pool = [x for x in pool if x["role"] in (role, "idle", "listen")] or pool
                if pool: break
            if not pool: continue
            rank = lambda x: (len(other.get(key(x["path"]), ())) > 0, x["pri"], len(other.get(key(x["path"]), ())))  # unused first, then the better pack
            best = min(rank(x) for x in pool); pool = [x for x in pool if rank(x) == best]
            x = pool[zlib.crc32(("%s|%s|%d" % (n, part, si)).encode("utf-8")) % len(pool)]
            taken.add(key(x["path"])); crossed_used |= x["crossed"]
            picks.append({"t": t, "role": role, "mood": mood, "path": x["path"]})
        out[n] = picks
    return S, pf, out


def main(a):
    if not a or a[0] == "index":
        cl = index("--rebuild" in a)
        from collections import Counter
        print("%d acting clips in {MOTION} (index: progress/motion_index.json)" % len(cl))
        print(Counter(("sit" if x["sit"] else "stand", x["role"], x["mood"]) for x in cl).most_common())
        return 0
    if a[0] == "find":
        w = [s.lower() for s in a[1:]]
        for x in index():
            s = json.dumps(x, ensure_ascii=False).lower()
            if all(v in s for v in w): print(x["path"], "|", "sit" if x["sit"] else "stand", x["sex"], x["role"], x["mood"])
        return 0
    if a[0] == "pick" and len(a) >= 3:
        S, pf, out = plan(a[1], a[2])
        for n, ps in out.items():
            print(n)
            for p in ps: print("  %5.1fs %-6s %-5s %s" % (p["t"], p["role"], p["mood"], os.path.basename(p["path"])))
            if not ps: print("  (no clip fits - keep the old one)")
        if "--write" in a:
            for n, ps in out.items():
                if ps: S["cast"][n].pop("motion", None); S["cast"][n]["motions"] = [p["path"] for p in ps]
            json.dump(S, open(pf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("written:", os.path.relpath(pf, ROOT))
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
