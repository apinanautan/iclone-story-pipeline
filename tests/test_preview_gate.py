import os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import preview_gate as g
class GateTest(unittest.TestCase):
    def test_no_lease_and_wrong_step(self):
        with tempfile.TemporaryDirectory() as t, patch.object(g,"LEASE",Path(t)/"lease.json"):
            with self.assertRaises(g.Blocked): g.require("x.json","pose",[])
            with g.permit("test","1","pose","x.json") as env, patch.dict(os.environ,env), patch.object(os,"getppid",return_value=os.getpid()):
                self.assertEqual(g.require("x.json","pose",[])["step"],"pose")
                for spec,step,args in [("y.json","pose",[]),("x.json","render",[]),("x.json","pose",["--from"])]:
                    with self.assertRaises(g.Blocked): g.require(spec,step,args)
            self.assertFalse(g.LEASE.exists())
    def test_no_overlap(self):
        with tempfile.TemporaryDirectory() as t, patch.object(g,"LOCK",Path(t)/"lock"):
            with g.dispatch():
                with self.assertRaises(g.Blocked):
                    with g.dispatch(): pass
            with g.dispatch(): pass
    def test_orphaned_running_recovery(self):
        import json
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/"progress";p.mkdir()
            n={"story":"Fixture","part":"9.2","step":"open","state":"running","time":1}
            f=p/"now.json";f.write_text(json.dumps(n))
            l=p/"preview_lease.json";l.write_text(json.dumps(dict(n,pid=123,token="fixture")))
            receipts=p/"Fixture_9.2.json";receipts.write_text('{"steps_done":{"plan":1}}')
            with patch.object(g,"process_alive",return_value=True),patch.object(g,"worker_absent",return_value=True):
                self.assertEqual(g.reconcile_orphaned_run(root)["state"],"running")
            with patch.object(g,"process_alive",return_value=False),patch.object(g,"worker_absent",return_value=False):
                self.assertEqual(g.reconcile_orphaned_run(root)["state"],"running")
            with patch.object(g,"process_alive",return_value=False),patch.object(g,"worker_absent",return_value=True):
                with g.dispatch(p/"preview_dispatch.lock"):
                    self.assertEqual(g.reconcile_orphaned_run(root)["state"],"running")
                self.assertEqual(g.reconcile_orphaned_run(root)["state"],"failed")
                self.assertFalse(l.exists())
                self.assertEqual(receipts.read_text(),'{"steps_done":{"plan":1}}')
                self.assertEqual(g.reconcile_orphaned_run(root)["state"],"failed")
if __name__=="__main__": unittest.main()
