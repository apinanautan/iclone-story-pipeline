from pathlib import Path
import sys,ast,os,tempfile,json,unittest
from unittest.mock import patch
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/"scripts"))
from workflow_state import menu_save_verified,expected_live_title,unsaved_live_part
from cinematic_qa import read,write
import cinematic_qa
class SaveRender(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name)
  self.f=self.r/"part.iProject";self.f.write_bytes(b"existing project")
  self.title="iClone 8 - part.iProject";self.proof={"baseline_mtime_ns":self.f.stat().st_mtime_ns}
  self.g=self.r/"progress"/"Fixture_2.json"
  write(self.g,{"steps_done":{"switch":1},"ok":{"step5":True},"ready_menu_save":self.proof})
  self.S={"story":"Fixture","part":"2","project":str(self.f),"lines":[]}
  self.calls=[]
  tree=ast.parse((r/"scripts/ic8_part.py").read_text(encoding="utf-8"))
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="step_ready")
  def fail(msg):raise AssertionError(msg)
  self.ns={"__file__":str(self.r/"scripts/ic8_part.py"),"os":os,"sys":sys,"json":json,"Path":Path,"ROOT":str(self.r),"ORDER":["switch"],"NARR":(),"title":lambda:self.title,"live_project_identity":lambda:"123:456","gui":lambda *a:self.calls.append(a),"say":lambda *a:None,"count":lambda *a:None,"fail":fail}
  exec(compile(ast.Module(body=[fn],type_ignores=[]),"<ready>","exec"),self.ns)
  self.m=patch.object(cinematic_qa,"editorial_valid",return_value=True);self.m.start()
 def tearDown(self):self.m.stop();self.t.cleanup()
 def test_save_does_not_reopen(self):
  os.utime(self.f,ns=(self.proof["baseline_mtime_ns"]+20000000,)*2)
  self.ns["step_ready"](self.S,"")
  self.assertFalse(read(self.g).get("ready_menu_save"))
  self.assertEqual(self.calls,[])
 def test_unsaved_requires_explicit_live_render(self):
  self.title+=" *"
  with patch.dict(os.environ,{"AIICLONE_RENDER_LIVE":"0"}):
   with self.assertRaises(SystemExit) as cm:self.ns["step_ready"](self.S,"")
   self.assertEqual(cm.exception.code,3)
  self.assertFalse(read(self.g)["ready_menu_save"].get("live_render_pending_save"))
 def test_live_render_keeps_pending_save(self):
  self.title+=" *"
  with patch.dict(os.environ,{"AIICLONE_RENDER_LIVE":"1"}):
   self.ns["step_ready"](self.S,"")
  self.assertEqual(read(self.g)["ready_menu_save"]["live_identity"],"123:456")
  self.assertEqual(unsaved_live_part(self.r),"Fixture_2")
  self.assertEqual(self.calls,[])
 def test_wrong_live_project_fails(self):
  self.title="iClone 8 - different.iProject"
  with patch.dict(os.environ,{"AIICLONE_RENDER_LIVE":"1"}):
   with self.assertRaises(AssertionError):self.ns["step_ready"](self.S,"")
 def test_wrong_title_or_empty_file_not_verified(self):
  self.f.write_bytes(b"")
  self.assertFalse(menu_save_verified(self.f,self.proof,self.title))
  self.assertFalse(expected_live_title(self.f,"iClone 8 - another part.iProject"))
if __name__=="__main__":unittest.main()
