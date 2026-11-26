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
        self.assertEqual(ORDER[ORDER.index("cast"):ORDER.index("cams")+1], ["cast", "sound", "pose", "lip", "cams"])
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
if __name__ == "__main__":
    unittest.main()
