import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import goal_signal as g
class Signal(unittest.TestCase):
    def test_exact_stop_receipt(self):
        with tempfile.TemporaryDirectory() as t,patch.object(g,"STATE",Path(t)):
            a="ABCD1234-ABC";b="ABCD1234-DEF"
            d=g.request(a);self.assertEqual(d["state"],"requested")
            self.assertEqual(g.read(b),{})
            with self.assertRaises(ValueError):g.acknowledge(a,"wrong","session")
            self.assertEqual(g.acknowledge(a,d["id"],"session")["state"],"stopped")
            self.assertEqual(g.request(a)["state"],"stopped")
            with self.assertRaises(ValueError):g.acknowledge(a,d["id"],"other")
            with self.assertRaises(ValueError):g.request("../bad")
if __name__=="__main__":unittest.main()
