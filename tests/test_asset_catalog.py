import struct
import tempfile
import unittest
from pathlib import Path
from src.asset_catalog import read_vpk_index, classify

class CatalogTests(unittest.TestCase):
    def test_real_null_terminated_vpk(self):
        def c(s): return s.encode() + bytes([0])
        tree = c("mdl") + c("props") + c("car") + struct.pack("<IHHIIH", 0, 0, 0x7fff, 0, 0, 0xffff) + c("") + c("") + c("")
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"pak01_dir.vpk"
            p.write_bytes(struct.pack("<III", 0x55AA1234, 1, len(tree)) + tree)
            self.assertEqual(read_vpk_index(p), ["props/car.mdl"])
    def test_categories(self):
        self.assertEqual(classify("models/a.mdl"), "model")
        self.assertIsNone(classify("readme.txt"))
