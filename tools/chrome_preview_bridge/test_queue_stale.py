"""Offline: a stuck delivery must not block later images; Preview status line is honest (2026-11-28)."""
import json,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import queue_preview as Q

JPG=b'\xff\xd8'+b'0'*100

class Stale(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();Q.STATE=Path(self.tmp.name)
        self.img=Path(self.tmp.name)/'a.jpg';self.img.write_bytes(JPG)
        Q.current=lambda:{'story':'s','part':'1'}
        Q.binding=lambda:{'story':'s','url':'https://chatgpt.com/c/abc'}
        Q.handoff_pending=lambda:None
        Q.ensure_relay=lambda:True
        Q.relay_up=lambda timeout=0.5:True
    def tearDown(self):self.tmp.cleanup()
    def job(self,**k):(Q.STATE/'job.json').write_text(json.dumps(k),encoding='utf-8')

    def test_in_flight_is_kept(self):
        self.job(id='old',state='claimed',phase='sending',created=time.time()-30)
        self.assertIn('still in progress',Q.queue(str(self.img),'s','1'))
        self.assertEqual(Q.read_job()['id'],'old')
    def test_stuck_claimed_is_replaced(self):
        self.job(id='old',state='claimed',phase='sending',created=time.time()-Q.STALE-5)
        self.assertIn('replaced stuck delivery',Q.queue(str(self.img),'s','1'))
        j=Q.read_job();self.assertEqual(j['state'],'pending');self.assertEqual(j['replaced']['id'],'old')
    def test_needs_review_stuck_is_replaced(self):
        self.job(id='old',state='needs_review',phase='attach',created=time.time()-Q.STALE-5)
        self.assertIn('replaced',Q.queue(str(self.img),'s','1'))
    def test_pending_is_replaced_by_fresher(self):
        self.job(id='old',state='pending',created=time.time()-10)
        self.assertIn('replaced',Q.queue(str(self.img),'s','1'))
    def test_dead_relay_is_reported(self):
        Q.ensure_relay=lambda:False
        self.assertIn('WARNING relay not running',Q.queue(str(self.img),'s','1'))
    def test_status_lines(self):
        self.job(id='x',state='pending',created=time.time(),diagnostic='waiting: mouse or keyboard active')
        self.assertIn('เมาส์',Q.status_line())
        Q.relay_up=lambda timeout=0.5:False
        self.assertIn('relay ไม่ทำงาน',Q.status_line())
        self.job(id='x',state='sent',created=time.time())
        self.assertIn('ถึงแชตแล้ว',Q.status_line())

if __name__=='__main__':unittest.main()
