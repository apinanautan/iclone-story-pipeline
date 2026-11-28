import json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from repair_queue import record,lines
import cam_check
from PIL import Image

class RepairQueue(unittest.TestCase):
    def test_countdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            for passed in (0,1,2,2,9):
                row=record(tmp,"story","5","cam_check",{str(i):{"state":"pass" if i<passed else "fail","detail":""} for i in range(9)})
                self.assertEqual(row["remaining"],9-passed)
            self.assertEqual([r["remaining"] for r in row["history"]],[9,8,7,0])
            self.assertIn("0/9",lines(tmp,"story","5")[0])
    def test_only_changed_evidence_reopens(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Path(tmp)/"jobs";j.mkdir();p=Path(tmp)/"progress"
            S={"story":"story","part":"5","shots":[{"t":[0,2]},{"t":[2,4]}]}
            for i in (1,2):
                for k in (1,2,3):Image.new("RGB",(32,18),(i*40,k*40,0)).save(j/f"cam_{i:02}_{k:02}_sample.png")
            self.assertEqual(cam_check.check(S,str(j),str(p))[0],3)
            f=p/"story_5_camcheck.json";d=json.loads(f.read_text(encoding="utf-8"))
            for e in d["shots"]:
                e.update(see="Visible verified subject in actual frame",**{k:True for k in cam_check.ASK})
            f.write_text(json.dumps(d),encoding="utf-8")
            self.assertEqual(cam_check.check(S,str(j),str(p))[0],0)
            Image.new("RGB",(32,18),(0,0,200)).save(j/"cam_02_01_sample.png")
            self.assertEqual(cam_check.check(S,str(j),str(p))[0],3)
            d=json.loads(f.read_text(encoding="utf-8"));self.assertTrue(d["shots"][0]["framing"]);self.assertIsNone(d["shots"][1]["framing"])
            q=json.loads((p/"story_5_repair_queue.json").read_text(encoding="utf-8"))["stages"]["cam_check"]
            self.assertEqual((q["passed"],q["remaining"],q["pending"]),(1,1,1))
if __name__=="__main__":unittest.main()
