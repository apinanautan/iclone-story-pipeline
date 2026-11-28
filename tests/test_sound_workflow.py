import ast
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from workflow_state import invalidated_steps, sound_source, source_changed
def assigned(file, name):
    tree = ast.parse((ROOT / file).read_text(encoding="utf-8"))
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
ORDER = assigned("scripts/ic8_part.py", "ORDER")
FULL = ORDER + ["ready", "render", "video_check"]
class SoundWorkflow(unittest.TestCase):
    def test_order(self):
        self.assertEqual(ORDER[ORDER.index("cast"):ORDER.index("cams")+1], ["cast", "sound", "pose", "motion_check", "lip", "scene_review", "prop_review", "camera_replan", "cams"])
        self.assertEqual([k for k, v in assigned("scripts/progress_app.py", "STEPS") if k in ORDER], ORDER)
    def test_repair_keeps_sound(self):
        for step in ("cast", "motion_plan", "pose", "lip", "cams", "cam_check", "motion_check", "light_check", "face_check"):
            with self.subTest(step=step):
                self.assertNotIn("sound", invalidated_steps(step, FULL))
    def test_actual_sound_step_one_native_import(self):
        tree = ast.parse((ROOT / "scripts/ic8_part.py").read_text(encoding="utf-8"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "step_sound")
        calls = []
        import os
        ns = {"os": os, "gui": lambda *args: calls.append(args), "live": lambda *args: None, "say": lambda *args: None}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), "<step_sound>", "exec"), ns)
        ns["step_sound"]({"wav": "test.wav"}, "")
        self.assertEqual(calls, [("sound", "test.wav", "-Replace")])
    def test_new_project_invalidates_sound(self):
        self.assertIn("sound", invalidated_steps("open", FULL))
    def test_changed_wav_receipt(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "part.wav"
            f.write_bytes(b"first")
            receipt = sound_source(str(f))
            self.assertFalse(source_changed(receipt, str(f)))
            f.write_bytes(b"different length")
            self.assertTrue(source_changed(receipt, str(f)))
            self.assertFalse(source_changed(None, str(f)))
    def test_sound_replacement_keeps_pose(self):
        self.assertNotIn("pose", invalidated_steps("sound", FULL))
        self.assertIn("lip", invalidated_steps("sound", FULL))
        self.assertIn("render", invalidated_steps("sound", FULL))
    def test_camera_repair_keeps_motion(self):
        for step in ("camera_replan","cams","cam_check"):
            self.assertNotIn("motion_check", invalidated_steps(step,FULL))
    def test_live_project_guard(self):
        from workflow_state import live_project_problem
        p="part.iProject"
        good={"title":"iClone 8 - part.iProject *","identity":"12:34","responding":True}
        self.assertFalse(live_project_problem(p,{"identity":"12:34"},good))
        self.assertTrue(live_project_problem(p,{"identity":"old"},good))
        self.assertTrue(live_project_problem(p,None,dict(good,title="iClone 8 - DefProject.iProject")))
        self.assertTrue(live_project_problem(p,None,{}))
    def test_duplicate_hidden_sound_fails_closed(self):
        from ic8_sound_tracks import classify,single_correct
        rows=[{"name":"Project","y":46,"visible":True},{"name":"Switcher","y":70,"visible":True},{"name":"Sound","y":94,"visible":True}]
        one={"id":1,"tip":"part (100.00%) Embedded Timecode : 00:00:00:00 (24fps) ","y":94,"x":0,"visible":True,"selectable":True}
        two=dict(one,id=2,y=0,x=91.919403,visible=False)
        report=classify(rows,[one,two])
        self.assertEqual(len(report["uncertain"]),1)
        self.assertFalse(single_correct(report,"part"))
        self.assertTrue(single_correct(classify(rows,[one]),"part"))
        self.assertFalse(single_correct(classify(rows,[dict(one,x=91.9)]),"part"))
        self.assertFalse(single_correct(classify(rows,[one,dict(one,id=2)]),"part"))
        self.assertFalse(single_correct(classify([],[]),"part"))
    def test_sound_repair_does_not_rebuild_cameras(self):
        for key in ("pose","motion_check","scene_review","camera_replan","cams","cam_check"):
            self.assertNotIn(key,invalidated_steps("sound",FULL))
    def test_native_import_guard_is_before_import(self):
        s=(ROOT/"scripts/ic8_gui.ps1").read_text(encoding="utf-8-sig")
        s=s[s.index(" 'sound'  {"):s.index(" 'lip'    {")]
        self.assertNotIn("ClickRel",s)
        self.assertEqual(s.count("Keys @($CTRL) 0x49"),1)
        self.assertLess(s.index("old audio remains; no import sent"),s.index("Keys @($CTRL) 0x49"))
        self.assertIn("sound not verified; no second import",s)
    def test_readonly_rechecks_keep_production(self):
        for step in ("motion_check","cam_check","light_check"):
            for keep in ("pose","lip","scene_review","prop_review","camera_replan","cams"):
                self.assertNotIn(keep,invalidated_steps(step,FULL))
    def test_lip_repair_keeps_cameras(self):
        for keep in ("scene_review","prop_review","camera_replan","cams","cam_check"):
            self.assertNotIn(keep,invalidated_steps("lip",FULL))
        self.assertIn("face_check",invalidated_steps("lip",FULL))
if __name__ == "__main__":
    unittest.main()
