"""Regression for local stop latch and Preview gates without a live scene."""
import unittest,tempfile,sys,types
from pathlib import Path
from unittest.mock import patch
import relay
class GoalGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.url="https://chatgpt.com/c/fixture"
        self.env=patch.multiple(relay,BASE=self.root,STATE=self.root/"bridge")
        self.env.start()
        self.binding=patch.object(relay,"binding",return_value={"story":"Fixture","url":self.url});self.binding.start()
        self.sleep=patch.object(relay.sleep,"state",return_value={});self.sleep.start()
        relay.sleep.write(self.root/"progress/now.json",{"story":"Fixture","part":"2","state":"done","step":"switch"})
        self.p=types.SimpleNamespace(STORY_STEPS=[("range","range"),("story_ok","story")],STEPS=[("switch","switch"),("user_ok","approve"),("ready","ready")],story_states=lambda s:{"range":("done",""),"story_ok":("done","")},step_states=lambda s,n:({"switch":"done","user_ok":"todo","ready":"todo"},{}))
        self.mock=patch.dict(sys.modules,{"progress_app":self.p});self.mock.start()
    def tearDown(self):
        self.mock.stop();self.sleep.stop();self.binding.stop();self.env.stop();self.tmp.cleanup()
    def test_latch_even_unbound(self):
        relay.sleep.write(relay.STATE/"goal_stop.json",{"stopped":True})
        self.assertTrue(relay.goal_gate("https://chatgpt.com/c/other")["stop"])
    def test_preview_approval(self):
        self.assertTrue(relay.goal_gate(self.url)["stop"])
        self.assertFalse(relay.goal_gate("https://chatgpt.com/c/other")["stop"])
    def test_active_sleep_not_paused_by_manual_gate(self):
        relay.sleep.state.return_value={"enabled":True}
        self.assertFalse(relay.goal_gate(self.url)["stop"])
    def test_not_stop_while_running(self):
        relay.sleep.write(self.root/"progress/now.json",{"story":"Fixture","part":"2","state":"running"})
        self.assertFalse(relay.goal_gate(self.url)["stop"])
    def test_completed(self):
        self.p.step_states=lambda s,n:({"switch":"done","user_ok":"done","ready":"done"},{})
        self.assertTrue(relay.goal_gate(self.url)["stop"])
if __name__=="__main__":unittest.main()
