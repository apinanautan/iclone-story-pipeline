"""Offline tests; no iClone API invocation or scene mutation."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"


class McpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        (self.root / "docs" / "rules.md").write_text("rules", encoding="utf-8")
        self.job = Path(self.temp.name) / "jobs"
        self.run = self.job / "run"
        self.run.mkdir(parents=True)
        spec = importlib.util.spec_from_file_location("icmcp", SCRIPT)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.m.ROOT = self.root
        self.m.DATA = self.job
        self.m.RUN = self.run

    def test_read_scope(self):
        self.assertEqual(self.m.read_project_file("docs/rules.md")["text"], "rules")
        with self.assertRaises(ValueError): self.m.read_project_file("../escape.txt")
        with self.assertRaises(ValueError): self.m.read_project_file("/etc/passwd")

    def test_stage_atomic_and_result(self):
        with patch.object(self.m, "_iclone_running", return_value=True):
            result = self.m.inspect_scene()
        job_id = result["job_id"]
        self.assertTrue((self.run / (job_id + ".py")).exists())
        self.assertEqual(json.loads((self.run / (job_id + ".json")).read_text())["action"], "inspect_scene")
        self.assertEqual(self.m.get_job_result(job_id)["watcher_state"], "queued")
        (self.run / (job_id + ".py")).rename(self.run / (job_id + ".done"))
        (self.run / (job_id + ".result.json")).write_text('{"ok":true,"data":{}}')
        self.assertTrue(self.m.get_job_result(job_id)["success"])

    def test_refuse_preexisting_queue(self):
        (self.run / "old.py").write_text("# unknown existing job")
        with patch.object(self.m, "_iclone_running", return_value=True):
            with self.assertRaises(RuntimeError):
                self.m.inspect_scene()

    def test_guards(self):
        with self.assertRaises(ValueError): self.m.place_existing_avatar("A",0,0,0,0)
        with self.assertRaises(ValueError): self.m.set_project_duration(80)
        with self.assertRaises(ValueError): self.m.render_part(1, 80)
        with self.assertRaises(ValueError): self.m.set_existing_camera("Camera_0",1,1,1,2,2,2,50,True,True)
        with self.assertRaises(ValueError): self.m.get_job_result("bad")
        with self.assertRaises(ValueError): self.m.preview_camera_still("Other_Camera")
        with self.assertRaises(ValueError): self.m.build_part2_camera_sequence()
        with self.assertRaises(ValueError): self.m.retune_part2_shot(7,33,200,25950,33,600,25860)
        with self.assertRaises(ValueError): self.m.retune_part2_group_shot(7,33,120,26000,33,700,25850)
        with self.assertRaises(RuntimeError): self.m.apply_part2_face_lips("p2_monk")
        with self.assertRaises(RuntimeError): self.m.apply_part2_face_lips("unknown", True)
        with self.assertRaises(RuntimeError):
            self.m.apply_part2_face_lips("p2_old", True)

    def test_list_ignores_git(self):
        (self.root / ".git").mkdir()
        (self.root / ".git" / "config").write_text("private")
        ls = self.m.list_project_files()
        self.assertEqual([x["path"] for x in ls["files"]], ["docs/rules.md"])


if __name__ == "__main__":
    unittest.main()
