# -*- coding: utf-8 -*-
"""Offline: standing poses must vary (user 2026-11-22: folded arms for the whole story). No iClone."""
import ast
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
import ic8_part as P  # noqa: E402


def pose_funcs():   # clip_end + its constants from ic8_pose_place.py without running the iClone part
    src = open(os.path.join(HERE, "scripts", "ic8_pose_place.py"), encoding="utf-8").read()
    keep = [n for n in ast.parse(src).body
            if (isinstance(n, ast.FunctionDef) and n.name == "clip_end")
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("GAP",) for t in n.targets))
            or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple))]
    g = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "pose", "exec"), g)
    return g


F3 = "{MOTION}/MographMotion/02_Female/Stand03.iMotion"
TKI = "{MOTION}/MographMotion/01_Male/StandTKI.iMotion"
S00 = "{MOTION}/04_CC MixMove_Female/Stand00.iMotion"


class Variety(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp(); os.makedirs(os.path.join(self.t, "parts")); self.old = P.ROOT; P.ROOT = self.t
        for n in ("1", "2"):
            json.dump({"cast": {"a": {"motions": [F3]}}}, open(os.path.join(self.t, "parts", "S_%s.json" % n), "w"))

    def tearDown(self):
        P.ROOT = self.old

    def run_check(self, cast, part="3", end=60):
        e, w = [], []
        P.motion_variety({"story": "S", "part": part, "cast": cast, "lines": [{"t": [0, end]}]}, e, w)
        return e, w

    def test_reused_in_two_parts(self):
        e, _ = self.run_check({"แม่": {"motions": [F3, S00]}})
        self.assertTrue(any("already in parts 1, 2" in x for x in e))

    def test_shared_in_part(self):
        e, _ = self.run_check({"แม่": {"motions": [TKI, S00]}, "พ่อ": {"motions": ["G:/x/MographMotion/01_Male/StandTKI.iMotion"]}})
        self.assertTrue(any("share the standing clip" in x for x in e))

    def test_two_folded_arms(self):
        e, _ = self.run_check({"แม่": {"motions": [F3]}, "ป้า": {"motions": ["x/Arms Crossed_Response/Agree01.iMotion"]}}, part="1")
        self.assertTrue(any("arms folded" in x for x in e))

    def test_one_clip_long_on_screen_fails(self):
        e, _ = self.run_check({"แม่": {"motions": [TKI]}})
        self.assertTrue(any("one motion" in x for x in e))
        e, _ = self.run_check({"แม่": {"motions": [TKI], "visible": [[0, 1], [15, 0]]}})   # 15 s on screen: fine
        self.assertFalse(any("one motion" in x for x in e))

    def test_varied_is_clean(self):
        e, w = self.run_check({"แม่": {"motions": [TKI, S00]}, "ลูก": {"motions": ["z/Brick Laying.rlMotion"]}})
        self.assertEqual((e, w), ([], []))


class ClipEnd(unittest.TestCase):
    def test_cut_aligned_and_capped(self):
        g = pose_funcs(); ce, GAP = g["clip_end"], g["GAP"]
        self.assertAlmostEqual(ce(0, 60, [5, 12, 30]), 12 - GAP)   # first cut >= 8 s: next clip starts ON the cut
        self.assertAlmostEqual(ce(0, 60, [25, 40]), 20)            # no cut in 8-20 s: cap at 20
        self.assertAlmostEqual(ce(0, 6, [3]), 6)                   # short clip ends by itself
        self.assertAlmostEqual(ce(10, 60, [15, 19, 30]), 19 - GAP)  # cut 5 s in: too soon; 9 s in: use it
        self.assertAlmostEqual(ce(0, 60, []), 20)


if __name__ == "__main__":
    unittest.main()
