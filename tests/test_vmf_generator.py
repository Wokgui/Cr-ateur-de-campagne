import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vmf_generator import build_vmf


class VmfGeneratorTests(unittest.TestCase):
    def test_room_door_and_horde_are_emitted(self) -> None:
        scene = json.loads((ROOT / "examples" / "room_horde.json").read_text(encoding="utf-8"))
        vmf = build_vmf(scene)

        self.assertIn('"classname" "worldspawn"', vmf)
        self.assertIn('"classname" "prop_door_rotating"', vmf)
        self.assertIn('"classname" "trigger_once"', vmf)
        self.assertIn('"classname" "info_director"', vmf)
        self.assertIn('"OnTrigger" "horde_director,ForcePanicEvent,,0,-1"', vmf)
        self.assertGreaterEqual(vmf.count("\nsolid\n"), 6)


if __name__ == "__main__":
    unittest.main()
