# -*- coding: utf-8 -*-
"""selfupdate.py - the program updates ITSELF from the latest GitHub release, whatever started it
(user 2026-11-23 "ทำไมเครื่องอื่นไม่อัปเดต": GPT/MCP and Ai-iclone.cmd run python directly, so only the exe updated).

Same rules as the exe launcher: at most one check per 10 minutes (force = now), never in a git checkout,
never overwrite work data (stories/, parts/, progress/ keep existing files) or paths.local.json.
Errors are PRINTED (never silent), the old version keeps running.
"""
import io, json, os, re, shutil, sys, time, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "apinanautan/iclone-story-pipeline"
KEEP_DIRS = ("stories", "parts", "progress")
KEEP_FILES = ("paths.local.json",)
STAMP = os.path.join(ROOT, "progress", "update_check.txt")


def ver(v): return [int(x) for x in re.findall(r"\d+", v or "")[:3]] + [0] * (3 - len(re.findall(r"\d+", v or "")[:3]))


def current():
    try: return open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
    except OSError: return "0"


def _get(url, t=20):
    rq = urllib.request.Request(url, headers={"User-Agent": "Ai-iclone"})
    with urllib.request.urlopen(rq, timeout=t) as r: return r.read()


def check(force=False, say=lambda s: print(s, file=sys.stderr, flush=True)):
    """returns the new version string if it installed one, else None."""
    if os.path.isdir(os.path.join(ROOT, ".git")) or os.path.isfile(os.path.join(ROOT, ".git")):
        from pathlib import Path
        root=Path(ROOT)
        if (root/"progress"/"managed_release.json").is_file():
            from checkout_update import check_managed
            return check_managed(root, _get, REPO, force, say)
        if force: say("Ai-iclone: unmanaged Git checkout; not auto-updated")
        return None
    if not force:
        try:
            if time.time() - os.path.getmtime(STAMP) < 600: return None
        except OSError: pass
    try:
        tag = json.loads(_get("https://api.github.com/repos/%s/releases/latest" % REPO))["tag_name"]
        os.makedirs(os.path.dirname(STAMP), exist_ok=True)
        open(STAMP, "w", encoding="utf-8").write(time.strftime("%Y-%m-%dT%H:%M:%S") + " latest " + tag)
        cur = current()
        if ver(tag) <= ver(cur):
            if force: say("Ai-iclone: up to date (%s)" % cur)
            return None
        say("Ai-iclone: update %s -> %s ..." % (cur, tag))
        z = zipfile.ZipFile(io.BytesIO(_get("https://codeload.github.com/%s/zip/refs/tags/%s" % (REPO, tag), 120)))
        top = z.namelist()[0].split("/")[0]
        if top + "/scripts/ai_iclone.py" not in z.namelist(): raise RuntimeError("release has no scripts/ai_iclone.py")
        n, skipped = 0, []
        for name in z.namelist():
            rel = name[len(top) + 1:]
            if not rel or name.endswith("/"): continue
            dst = os.path.join(ROOT, *rel.split("/"))
            keep = rel in KEEP_FILES or rel.split("/")[0] in KEEP_DIRS
            if keep and os.path.exists(dst): continue
            if rel == "VERSION": continue            # written last: a half install is retried next time
            if rel.lower().endswith(".exe") and os.path.exists(dst):
                try: os.replace(dst, dst + ".old")     # a running exe can be renamed, not overwritten
                except OSError: pass
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with z.open(name) as s, open(dst, "wb") as d: shutil.copyfileobj(s, d)
                n += 1
            except OSError as e: skipped.append("%s (%s)" % (rel, e.strerror))
        if skipped:
            say("Ai-iclone: update NOT finished, %d file(s) locked: %s. Close the Ai-iclone window / other copies, then: Ai-iclone update"
                % (len(skipped), ", ".join(skipped[:5])))
            return None
        with z.open(top + "/VERSION") as s, open(os.path.join(ROOT, "VERSION"), "wb") as d: shutil.copyfileobj(s, d)
        say("Ai-iclone: installed %s (%d files) -> %s" % (tag, n, ROOT))
        return tag
    except Exception as e:
        say("Ai-iclone: update check failed (%s) - still using %s" % (e, current()))
        return None


if __name__ == "__main__":
    check(force="--check" not in sys.argv[1:], say=print)
