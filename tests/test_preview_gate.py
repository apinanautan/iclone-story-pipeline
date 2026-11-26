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
if __name__=="__main__": unittest.main()
