"""Offline regression checks for camera still review; never imports RLPy or starts iClone."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from still_check import check


class StillCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        rng = np.random.default_rng(20261120)
        arr = rng.integers(0, 256, size=(90, 160), dtype=np.uint8)
        self.original = Image.fromarray(arr).convert("RGB").resize(
            (1600, 900), resample=Image.Resampling.NEAREST
        )

    def frames(self, offsets, skip=()):
        paths = []
        for n, offset in enumerate(offsets, 1):
            if n in skip:
                continue
            im = Image.new("RGB", self.original.size)
            im.paste(self.original, (offset, 0))
            path = Path(self.tmp.name) / f"cam_01_{n:02d}_{n:05.1f}s.png"
            im.save(path)
            paths.append(str(path))
        return paths

    def test_valid_steady_sequence(self):
        self.assertEqual(check(self.frames([0, 0, 0, 0, 0]), [5]), [])

    def test_jump_is_detected(self):
        result = check(self.frames([0, 0, 120, 120, 120]), [5])
        self.assertTrue(any("JUMP" in r for r in result), result)

    def test_flip_is_detected(self):
        result = check(self.frames([0, 0, 120, 0, 0]), [5])
        self.assertTrue(any("FLIP" in r for r in result), result)

    def test_no_images_must_fail(self):
        self.assertTrue(any("no still images" in r for r in check([], [1])))

    def test_missing_still_index_must_fail(self):
        result = check(self.frames([0, 0, 0, 0, 0], skip=(3,)), [5])
        self.assertTrue(any("indices" in r for r in result), result)
        self.assertTrue(any("4/5" in r for r in result), result)

    def test_unreadable_png_must_fail(self):
        files = self.frames([0, 0, 0])
        Path(files[1]).write_bytes(b"not a real PNG")
        result = check(files, [3])
        self.assertTrue(any("unreadable image" in r for r in result), result)


if __name__ == "__main__":
    unittest.main()