import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from command_parser import apply_command


class CommandParserTests(unittest.TestCase):
    def test_room_uses_pointer_and_metric_dimensions(self):
        scene = apply_command({}, "crée une pièce de 6 par 4 mètres", [100, 200, 0])
        room = scene["rooms"][0]
        self.assertEqual(room["origin"], [100, 200, 0])
        self.assertEqual(room["size"][0], 236)
        self.assertEqual(room["size"][1], 157)

    def test_door_is_created_at_pointer(self):
        scene = apply_command({}, "mets une porte ici", [32, 64, 0])
        self.assertEqual(scene["doors"][0]["origin"], [32, 64, 0])

    def test_horde_trigger_is_created_at_pointer(self):
        scene = apply_command({}, "déclenche une horde ici", [1, 2, 3])
        self.assertEqual(scene["horde_triggers"][0]["origin"], [1, 2, 3])

    def test_unknown_command_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_command({}, "fais quelque chose")


if __name__ == "__main__":
    unittest.main()
