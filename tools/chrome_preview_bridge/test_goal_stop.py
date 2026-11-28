"""Goal Tracker must stop when the program itself stops (user 2026-11-28: it kept nudging after Switch)."""
import unittest,sys
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import relay,ai_iclone,progress_app as P
B="https://chatgpt.com/g/g-p-abc-proj/c/bound-1"
class Gate(unittest.TestCase):
    def run_gate(self,url,nxt="switch",why=None):
        steps={k:("done" if k!=nxt else "todo") for k,_ in P.STEPS}
        with patch.object(relay,"local_goal_block",return_value=None),\
             patch.object(relay,"binding",return_value={"story":"S","url":B}),\
             patch.object(relay,"active_context",return_value={"story":"S","part":"6","state":"todo"}),\
             patch.object(relay.sleep,"state",return_value={}),\
             patch.object(P,"story_states",return_value={k:("done",) for k,_ in P.STORY_STEPS}),\
             patch.object(P,"step_states",return_value=(steps,None)),\
             patch.object(ai_iclone,"program_stop",return_value=why):
            return relay.goal_gate(url)
    def test_program_stop_stops_tracker(self):
        g=self.run_gate(B,why="ข้อ switch ลองทางซ่อมครบแล้ว รอผู้ใช้");self.assertTrue(g["stop"]);self.assertIn("switch",g["reason"])
    def test_working_step_keeps_tracking(self):
        self.assertFalse(self.run_gate(B)["stop"])
    def test_user_ok_stops(self):
        self.assertTrue(self.run_gate(B,nxt="user_ok")["stop"])
    def test_unbound_chat_same_project_uses_same_gate(self):
        self.assertTrue(self.run_gate("https://chatgpt.com/g/g-p-abc-proj/c/other-2",nxt="user_ok")["stop"])
    def test_chat_outside_project_untouched(self):
        self.assertFalse(self.run_gate("https://chatgpt.com/c/random-3",nxt="user_ok")["stop"])
class ProgramStop(unittest.TestCase):
    def test_repairs_used_up(self):
        with patch.object(ai_iclone,"fails",return_value=99):
            self.assertIn("ทางซ่อมครบ",ai_iclone.program_stop("S","6","switch"))
    def test_no_fail_no_stop(self):
        with patch.object(ai_iclone,"fails",return_value=0),patch("repair_queue.stuck",return_value=None):
            self.assertIsNone(ai_iclone.program_stop("S","6","switch"))
if __name__=="__main__":unittest.main()
