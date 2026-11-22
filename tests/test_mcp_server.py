"""Offline tests for the Ai-iclone MCP server (no iClone, no real step runs)."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"
spec = importlib.util.spec_from_file_location("icmcp", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class McpTests(unittest.TestCase):
    def call(self, fn, *a, **k):
        with patch.object(m, "_run", side_effect=lambda *x: list(x)) as r:
            return fn(*a, **k)

    def test_tools_map_to_ai_iclone(self):
        self.assertEqual(self.call(m.status), ["status"])
        self.assertEqual(self.call(m.do_next_step), ["do"])
        self.assertEqual(self.call(m.do_next_step, dry=True), ["do", "--dry"])
        self.assertEqual(self.call(m.do_next_step, retry=True), ["do", "--force"])
        self.assertEqual(self.call(m.use_part, "เรื่อง", "3"), ["use", "เรื่อง", "3"])
        self.assertEqual(self.call(m.use_part, "เรื่อง"), ["use", "เรื่อง"])
        self.assertEqual(self.call(m.set_range, "1:05-2:10"), ["range", "1:05-2:10"])
        self.assertEqual(self.call(m.approve, "ผ่าน"), ["approve", "--said", "ผ่าน"])

    def test_approve_needs_user_words(self):
        for bad in ("", "   "):
            with self.assertRaises(ValueError):
                self.call(m.approve, bad)

    def test_no_part_specific_or_code_tools(self):
        names = [t.__name__ for t in m.TOOLS]
        self.assertFalse([n for n in names if "part2" in n or "python" in n or "script" in n])
        self.assertLessEqual(len(names), 12)

    def test_real_status_runs(self):   # read-only: really runs scripts/ai_iclone.py status
        out = m.status()
        self.assertIn("[Ai-iclone exit", out)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main()
