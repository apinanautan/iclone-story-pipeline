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
    def test_actionable_step_not_stopped_by_message_count(self):
        self.p.step_states=lambda s,n:({"switch":"done","user_ok":"done","ready":"todo"},{})
        for i in range(25):
            self.assertEqual(relay.goal_attempt(self.url,"session",str(i)),{"stop":False,"mode":"work","step":"ready"})
        self.assertFalse(relay.goal_control().get("stopped"))
    def test_failed_step_and_old_count_latch(self):
        self.p.step_states=lambda s,n:({"switch":"done","user_ok":"done","ready":"fail"},{})
        relay.sleep.write(self.root/"progress/now.json",{"story":"Fixture","part":"2","step":"ready","state":"failed"})
        relay.sleep.write(relay.STATE/"goal_stop.json",{"stopped":True,"url":self.url,"checkpoint":relay.goal_checkpoint(),"reason":"Preview unchanged after two follow-ups; inspect the blocked step before retrying"})
        for i in range(25):
            self.assertEqual(relay.goal_attempt(self.url,"session",str(i)),{"stop":False,"mode":"repair","step":"ready"})
        self.p.step_states=lambda s,n:({"switch":"done","user_ok":"todo","ready":"todo"},{})
        self.assertTrue(relay.goal_gate(self.url)["stop"])
    def test_running_waits_without_retry(self):
        relay.sleep.write(self.root/"progress/now.json",{"story":"Fixture","part":"2","step":"ready","state":"running"})
        self.assertTrue(relay.goal_attempt(self.url,"session","one")["wait"])
        self.assertFalse(relay.goal_control().get("attempt"))
    def test_sleep_not_paused_by_message_count(self):
        self.sleep.stop()
        relay.sleep.save(self.root,{"enabled":True,"url":self.url,"phase":"work"})
        try:
            for i in range(25):self.assertFalse(relay.goal_attempt(self.url,"session",str(i))["stop"])
            self.assertTrue(relay.sleep.state(self.root)["enabled"])
        finally:self.sleep.start()
    def test_manual_resume_rearms_but_does_not_bypass_approval(self):
        self.p.step_states=lambda s,n:({"switch":"done","user_ok":"done","ready":"todo"},{})
        relay.sleep.write(relay.STATE/"goal_stop.json",{"stopped":True,"checkpoint":relay.goal_checkpoint()})
        self.assertTrue(relay.goal_gate(self.url)["stop"])
        self.assertFalse(relay.goal_resume(self.url)["stop"])
        for i in range(25):self.assertFalse(relay.goal_attempt(self.url,"fresh",str(i))["stop"])
        self.p.step_states=lambda s,n:({"switch":"done","user_ok":"todo","ready":"todo"},{})
        self.assertTrue(relay.goal_resume(self.url)["stop"])
    def test_generic_needs_no_preview_binding(self):
        relay.binding.return_value={}
        relay.sleep.write(relay.STATE/"goal_stop.json",{"stopped":True,"checkpoint":"unbound"})
        self.assertFalse(relay.goal_gate(self.url)["stop"])
        self.assertFalse(relay.goal_resume(self.url)["stop"])
        for i in range(25):
            self.assertEqual(relay.goal_attempt(self.url,"fresh",str(i)),{"stop":False,"mode":"generic"})
        self.assertFalse(relay.goal_control().get("stopped"))
        self.assertFalse(relay.goal_control().get("attempt"))
    def test_generic_ignores_other_story_running(self):
        relay.binding.return_value={}
        relay.sleep.write(self.root/"progress/now.json",{"story":"Other","part":"9","state":"running"})
        self.assertEqual(relay.goal_attempt(self.url,"fresh","one"),{"stop":False,"mode":"generic"})
    def test_bound_block_does_not_stop_unrelated_chat(self):
        relay.sleep.write(relay.STATE/"goal_stop.json",{"stopped":True,"url":self.url,"reason":"explicit local pause"})
        self.assertTrue(relay.goal_gate(self.url)["stop"])
        self.assertEqual(relay.goal_attempt("https://chatgpt.com/c/other","other","one"),{"stop":False,"mode":"generic"})
    def test_selected_target_not_previous_execution(self):
        relay.sleep.write(self.root/"progress/ai_iclone.json",{"story":"Fixture","part":"8.2"})
        from workflow_state import active_context
        self.assertEqual(active_context(self.root)["part"],"8.2")
        self.assertEqual(active_context(self.root)["state"],"selected")
        self.assertEqual(relay.sleep.read(self.root/"progress/now.json")["part"],"2")
if __name__=="__main__":unittest.main()
