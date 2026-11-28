import json,tempfile,unittest,os
from pathlib import Path
os.environ.setdefault("LOCALAPPDATA",tempfile.gettempdir())
import relay
class T(unittest.TestCase):
    def test_sync_copies_new_files_keeps_key_and_drops_bak(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);(d/"manifest.json").write_text('{"version":"0.0.1"}');(d/"config.local.js").write_text("KEY")
            (d/"old.js.bak").write_text("x")
            done=relay.sync_installed([d])
            self.assertEqual(json.loads((d/"manifest.json").read_text())["version"],relay.ext_version())
            self.assertTrue((d/"popup.js").is_file());self.assertEqual((d/"config.local.js").read_text(),"KEY")
            self.assertFalse((d/"old.js.bak").exists());self.assertTrue(done)
            self.assertEqual(relay.sync_installed([d]),[])   # second run: nothing to copy
    def test_clean_plugin_dir_loads_in_chrome(self):
        # other PC 2026-11-28: Chrome refused the tools folder because of __pycache__
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d, patch.object(relay,"PLUGIN_DIR",Path(d)/"Ai-iclone-Chrome"):
            p=relay.prepare_plugin_dir()
            names={x.name for x in p.iterdir()}
            self.assertFalse([n for n in names if n.startswith("_") or n.endswith(".py") or n=="relay.key"],names)
            self.assertIn("manifest.json",names)
            self.assertIn(relay.KEY,(p/"config.local.js").read_text())
            ref=set(__import__("re").findall(r'src="([^"]+)"',(p/"popup.html").read_text(encoding="utf-8")))
            self.assertTrue(ref<=names,ref-names)   # every file the popup loads is there
    def test_popup_has_no_global_named_top(self):
        # window.top is read-only: `function top` broke the whole popup (found 2026-11-28)
        import re
        for f in ("popup.js","sleep_popup.js"):
            self.assertIsNone(re.search(r"^(async )?function (top|self|name|status|parent)\(",(relay.ROOT/f).read_text(encoding="utf-8"),re.M),f)
if __name__=="__main__":unittest.main()
