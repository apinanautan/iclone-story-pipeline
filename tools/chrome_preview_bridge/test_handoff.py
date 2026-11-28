import sys,tempfile,unittest,json
from pathlib import Path
from unittest.mock import patch
import bridge_binding as b
import queue_preview as q
import prompt_handoff as h
class Handoff(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
        self.root=self.base/"tools/chrome_preview_bridge";self.root.mkdir(parents=True)
        self.state=self.root.parent/"preview_bridge_local";self.state.mkdir()
        self.patches=[patch.multiple(b,ROOT=self.root,STATE=self.state),patch.object(q,"STATE",self.state),patch.object(q,"ensure_relay",lambda:True)]
        for p in self.patches:p.start()
        self.put("stories/Fixture.json",{"name":"Fixture","parts":[{"n":"2"},{"n":"3"},{"n":"8.2"}]})
        self.put("progress/now.json",{"story":"Fixture","part":"2","step":"render","state":"failed"})
        self.put("progress/ai_iclone.json",{"story":"Fixture","part":"3"})
        self.put("progress/Fixture_2.json",{"steps_done":{"render":1}})
    def put(self,p,d):
        f=self.base/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(d),encoding="utf-8")
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def test_chat_code_reused_then_binds_gpt_chat(self):
        c=b.chat_code();self.assertRegex(c,r"^\[iClone Handoff [a-f0-9]{32}\]$")
        self.assertEqual(c,b.chat_code())
        x=b.handoff_bind(c[16:-1],"https://chatgpt.com/c/gpt")
        self.assertEqual(x["url"],"https://chatgpt.com/c/gpt")
        self.assertNotEqual(c,b.chat_code())
    def test_new_story_prompt_has_marker(self):
        v=b.handoff_create(kind="new")["prompt"]
        self.assertRegex(v,r"^\[iClone Handoff [a-f0-9]{32}\]\n")
    def test_generic_prompt_identical_across_targets(self):
        x=h.build("continue",self.base)
        self.put("progress/ai_iclone.json",{"story":"Other","part":"21.3"})
        self.assertEqual(x,h.build("continue",self.base))
        self.assertNotIn("Fixture",x)
        self.assertNotIn("21.3",x)
        self.assertNotIn("current_part_spec",x)
        self.assertIn("ขั้นตอนที่ลงมือเสร็จและตรวจผ่านแล้วถือว่าจบ",x)
        self.assertIn("แก้เฉพาะจุดนั้น",x)
        v=b.handoff_create()
        self.assertEqual(set(v),{"prompt"})
        self.assertNotIn("part",b.handoff_pending())
    def test_bind_live_story_and_one_time(self):
        b.handoff_create();id=b.handoff_pending()["id"]
        self.put("progress/ai_iclone.json",{"story":"Other","part":"8.2"})
        with self.assertRaises(ValueError):b.handoff_bind("wrong","https://chatgpt.com/c/test")
        x=b.handoff_bind(id,"https://chatgpt.com/c/test")
        self.assertEqual(x["story"],"Other")
        self.assertNotIn("part",x)
        with self.assertRaises(ValueError):b.handoff_bind(id,"https://chatgpt.com/c/other")
    def test_no_old_chat_image(self):
        b.bind("https://chatgpt.com/c/old")
        b.handoff_create();img=self.base/"sample.jpg";img.write_bytes(bytes([255,216,255])+b"sample")
        self.assertIn("waiting",q.queue(img,"Fixture","3"))
        b.handoff_bind(b.handoff_pending()["id"],"https://chatgpt.com/c/new")
        self.assertEqual(q.queue(img,"Fixture","3"),"queued one preview")
        self.assertEqual(b.read(self.state/"job.json")["url"],"https://chatgpt.com/c/new")
    def test_chat_code_does_not_block_story_images(self):
        b.bind("https://chatgpt.com/c/work");img=self.base/"sample.jpg";img.write_bytes(bytes([255,216,255])+b"sample")
        b.chat_code()   # Ai-iclone prints it on every run; GPT may not echo it again
        self.assertEqual(q.queue(img,"Fixture","3"),"queued one preview")
    def test_snap_has_no_story_rules(self):
        img=self.base/"sample.jpg";img.write_bytes(bytes([255,216,255])+b"sample")
        self.assertIn("no chat bound",q.queue_snap(img))
        b.bind("https://chatgpt.com/c/work")
        self.put("progress/ai_iclone.json",{"story":"Other","part":"9"})   # live story differs from the bound one
        self.assertEqual(q.queue_snap(img),"queued one preview")
        j=b.read(self.state/"job.json");self.assertEqual((j["kind"],j["url"],j["sleep"]),("snap","https://chatgpt.com/c/work",False))
    def test_new_handoff_archives_stranded_old_draft(self):
        b.bind("https://chatgpt.com/c/old")
        self.put("tools/preview_bridge_local/job.json",{"id":"a"*32,"url":"https://chatgpt.com/c/old","created":1,"state":"claimed","phase":"drafted","diagnostic":"waiting: bound chat not unique"})
        (self.state/"preview.jpg").write_bytes(b"original")
        b.handoff_create()
        x=b.handoff_bind(b.handoff_pending()["id"],"https://chatgpt.com/c/new")
        self.assertEqual(x["url"],"https://chatgpt.com/c/new")
        self.assertEqual(b.read(self.state/"job.json")["state"],"superseded")
        self.assertEqual((self.state/"superseded"/("a"*32)/"preview.jpg").read_bytes(),b"original")
    def test_new_handoff_never_discards_sending(self):
        b.bind("https://chatgpt.com/c/old")
        self.put("tools/preview_bridge_local/job.json",{"id":"a"*32,"url":"https://chatgpt.com/c/old","created":1,"state":"claimed","phase":"sending","diagnostic":"waiting: bound chat not unique"})
        b.handoff_create()
        with self.assertRaises(ValueError):b.handoff_bind(b.handoff_pending()["id"],"https://chatgpt.com/c/new")
        self.assertEqual(b.read(self.state/"job.json")["phase"],"sending")
    def test_busy_blocks_bind(self):
        b.handoff_create()
        self.put("progress/now.json",{"story":"Fixture","part":"3","state":"running"})
        with self.assertRaises(ValueError):b.handoff_bind(b.handoff_pending()["id"],"https://chatgpt.com/c/test")
    def test_next_verified_complete(self):
        with patch("sleep_session.complete",return_value=True):
            self.assertEqual(b.handoff_options()["default"],"8.2")
    def test_any_story_plan_and_count(self):
        for ids in (["7"],["2.4","5","12","21.3"],[str(i) for i in range(1,26)]):
            self.put("stories/Other.json",{"name":"Other","parts":[{"n":n} for n in ids]})
            self.put("progress/ai_iclone.json",{"story":"Other","part":ids[0]})
            o=b.handoff_options();self.assertEqual(o["parts"],ids)
            with patch("sleep_session.complete",return_value=True):
                self.assertEqual(b.handoff_options()["default"],ids[1] if len(ids)>1 else ids[0])
            v=b.handoff_create();self.assertNotIn("Other",v["prompt"])
            self.assertNotIn("Ai-iclone use",v["prompt"])
    def test_generic_instruction_not_legacy_part_numbers(self):
        p=self.base/"docs/CHROME_PREVIEW_GUIDE.md";p.parent.mkdir(exist_ok=True)
        p.write_text("legacy part9 only\nlegacy ท่อน 12 only\nuse generic watcher",encoding="utf-8")
        x=h.build("new",self.base)
        self.assertNotIn("legacy part9 only",x)
        self.assertNotIn("legacy ท่อน 12 only",x)
        self.assertIn("use generic watcher",x)
        self.assertNotIn("1.1, 1.2",x)
if __name__=="__main__":unittest.main()
