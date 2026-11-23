"""The repo is public and runs on many PCs: no file in git may carry this PC's folders
(user 2026-11-23: drive letters differ per PC, and my paths must not go to GitHub).
Write {MOTION} {DRIVE} {SAVE} {VIDEO} {DESKTOP} (scripts/paths.py) or %USERPROFILE% / os.path.expanduser("~")."""
import os, re, subprocess, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAD = re.compile(r"(?<![A-Za-z])(?:[D-Z]:(?:\\\\|\\|/)(?!\s|or\b)|C:(?:\\\\|\\|/)Users(?:\\\\|\\|/)(?!Public\b|<|\.\.\.)[^\\/%\s\"'`]+)")
BINARY = (".exe", ".jpg", ".png", ".mp4", ".wav", ".mp3", ".ico", ".pyc", ".blend", ".fbx")


class NoMachinePaths(unittest.TestCase):
    def test_tracked_files(self):
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True)
        if out.returncode: self.skipTest("not a git checkout")
        hits = []
        for f in out.stdout.decode("utf-8").split("\0"):
            if not f or f.lower().endswith(BINARY): continue
            try: text = open(os.path.join(ROOT, f), encoding="utf-8").read()
            except (OSError, UnicodeDecodeError): continue
            for i, line in enumerate(text.splitlines(), 1):
                if "never hardcode" in line: continue
                m = BAD.search(line)
                if m: hits.append("%s:%d %s" % (f, i, m.group(0)))
        self.assertEqual(hits, [], "machine paths in git (use {MOTION}/{SAVE}/... or ~):\n" + "\n".join(hits[:30]))


if __name__ == "__main__":
    unittest.main()
