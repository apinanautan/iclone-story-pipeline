"""Isolated regression tests. No iClone, Chrome, live progress or production paths."""
import sys,tempfile,unittest,copy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import sleep_session as S, cinematic_qa as Q
from PIL import Image
class PipelineQA(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name)
        self.story="Test Story";self.url="https://chatgpt.com/g/g-test-project/c/old"
        self.plan={"story_plan_ok":"approved","teacher_range_confirmed":True,"teacher_range":[0,18],"parts":[{"n":"1.1","master":[0,6]},{"n":"1.2","master":[6,12]},{"n":"2","master":[12,18]}]}
        Q.write(self.r/"stories"/(self.story+".json"),self.plan)
    def tearDown(self):self.tmp.cleanup()
    def test_scope_confirm_and_handoff(self):
        with self.assertRaises(S.SleepError):S.start(self.r,self.story,self.url,False)
        with patch.object(S,"complete",side_effect=lambda r,s,n:n=="1.1"):
            d=S.start(self.r,self.story,self.url,True)
            self.assertEqual((d["part"],d["phase"]),("1.2","handoff"))
            self.assertFalse(S.active(self.r,self.story,"1.2"))
            with self.assertRaises(S.SleepError):S.bind_next(self.r,"https://chatgpt.com/g/other/c/new")
            with self.assertRaises(S.SleepError):S.bind_next(self.r,self.url)
            S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/new")
            self.assertTrue(S.active(self.r,self.story,"1.2"))
            self.assertFalse(S.active(self.r,self.story,"2"))
            with self.assertRaises(S.SleepError):S.advance(self.r)
            S.pause(self.r);self.assertFalse(S.active(self.r,self.story,"1.2"))
    def test_advance_last_and_no_extra_parts(self):
        with patch.object(S,"complete",return_value=False):
            S.start(self.r,self.story,self.url,True)
        S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/first")
        with patch.object(S,"complete",side_effect=lambda r,s,n:n in ("1.1","1.2")):
            d=S.advance(self.r);self.assertEqual(d["part"],"2")
        S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/final")
        with patch.object(S,"complete",return_value=True):
            d=S.advance(self.r);self.assertFalse(d["enabled"]);self.assertEqual(d["phase"],"complete")
    def test_explicit_current_scope_preserves_earlier_work(self):
        with patch.object(S,"complete",return_value=False):
            with self.assertRaises(S.SleepError):S.start(self.r,self.story,self.url,True,protect_part="1.2")
            self.assertFalse(S.state(self.r).get("enabled"))
            d=S.start(self.r,self.story,self.url,True,from_part="1.2",protect_part="1.2")
            self.assertEqual(d["part"],"1.2")
            self.assertEqual(d["earlier_unverified"],["1.1"])
        S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/current")
        with patch.object(S,"complete",side_effect=lambda r,s,n:n=="1.2"):
            self.assertEqual(S.advance(self.r)["part"],"2")
    def test_plan_change_blocks(self):
        with patch.object(S,"complete",return_value=False):S.start(self.r,self.story,self.url,True)
        self.plan["parts"][0]["note"]="changed";Q.write(self.r/"stories"/(self.story+".json"),self.plan)
        with self.assertRaises(S.SleepError):S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/new")
    def test_incomplete_approval_rejected(self):
        with patch.object(S,"complete",return_value=False):S.start(self.r,self.story,self.url,True)
        S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/new")
        with self.assertRaises(S.SleepError):S.approve(self.r,self.story,"1.1")
    def test_approval_is_separate_and_revoked(self):
        with patch.object(S,"complete",return_value=False):S.start(self.r,self.story,self.url,True)
        S.bind_next(self.r,"https://chatgpt.com/g/g-test-project/c/new")
        spec=self.r/"parts"/(self.story+"_1.1.json");Q.write(spec,{"lines":[{"who":"narrator"}]})
        p=self.r/"progress"/(self.story+"_1.1.json")
        steps="check motion_plan open cast sound pose scene_review prop_review camera_replan cams cam_check motion_check light_check face_check editorial_review switch".split()
        Q.write(p,{"steps_done":{k:1 for k in steps},"ok":{}})
        q=Q.folder(self.r,self.story,"1.1");m={"images":{"cam_01.png":"x"}};notes={"pass":True}
        Q.write(q/"camera_manifest.json",m);Q.write(q/"editorial_notes.json",notes)
        Q.write(q/"editorial_receipt.json",{"manifest":Q.hashobj(m),"notes":Q.hashobj(notes),"spec_sha256":Q.digest(spec)})
        S.approve(self.r,self.story,"1.1");d=Q.read(p)
        self.assertFalse(d["ok"].get("step5"));self.assertTrue(S.approval_valid(self.r,self.story,"1.1",d))
        Q.write(spec,{"lines":[{"who":"narrator"}],"changed":True})
        self.assertFalse(S.approval_valid(self.r,self.story,"1.1",d))
        S.pause(self.r);self.assertFalse(S.approval_valid(self.r,self.story,"1.1",d))
    def test_pacing_and_face_only(self):
        rows=[{"size":"CU","purpose":"narrative purpose example","scene_evidence":"scene_01_000.png observed","cut_reason":"motivated cut example","short_reason":"brief event example","t":[i*3,(i+1)*3]} for i in range(4)]
        e=Q.plan_errors(rows);self.assertTrue(any("face-only" in x for x in e));self.assertTrue(any("short cuts" in x for x in e))
        for i,s in enumerate(rows):s.update(size=["MS","MCU","OTS","CU"][i],t=[i*8,(i+1)*8])
        self.assertFalse(Q.plan_errors(rows))
    def test_replan_hash_stale(self):
        q=Q.folder(self.r,self.story,"1.1");q.mkdir(parents=True)
        Image.new("RGB",(8,8),"red").save(q/"scene_01_000.png")
        m={"images":Q.images(q,"scene_*.png")};Q.write(q/"scene_manifest.json",m)
        spec={"story":self.story,"part":"1.1","shots":[{"t":[0,8]}]}
        Q.write(q/"replan_receipt.json",{"shots":Q.shots(spec),"scene":Q.hashobj(m)})
        self.assertTrue(Q.require_replan(spec,self.r))
        spec["shots"][0]["t"]=[0,9]
        self.assertFalse(Q.require_replan(spec,self.r))
    def test_final_receipt_requires_observations(self):
        p=self.r/"clip.mp4";p.write_bytes(b"fixture");pr=self.r/"clip.iProject";pr.write_bytes(b"fixture")
        spec={"story":self.story,"part":"1.1","video":str(p),"project":str(pr)}
        with self.assertRaises(SystemExit) as ex:Q.check_final(spec,self.r,self.fail,lambda x:None)
        self.assertEqual(ex.exception.code,3)
        q=Q.folder(self.r,self.story,"1.1")
        Q.write(q/"final_notes.json",{"video_sha256":Q.digest(p),"pass":True,**{k:"test-only mocked observation" for k in ("moving_review","audio_review","cuts_review","continuity")}})
        Q.check_final(spec,self.r,self.fail,lambda x:None)
        self.assertEqual(Q.read(q/"final_receipt.json")["video_sha256"],Q.digest(p))
if __name__=="__main__":unittest.main()
