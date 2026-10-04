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

    def test_selected_object_can_be_moved(self):
        scene = apply_command({}, "mets une porte ici", [0, 0, 0])
        selected = scene["doors"][0]["id"]
        moved = apply_command(scene, "déplace ça ici", [400, 50, 0], selected)
        self.assertEqual(moved["doors"][0]["origin"], [400, 50, 0])

    def test_nearest_object_can_be_deleted(self):
        scene = apply_command({}, "mets une porte ici", [0, 0, 0])
        scene = apply_command(scene, "mets une porte ici", [500, 0, 0])
        scene = apply_command(scene, "supprime ça", [490, 0, 0])
        self.assertEqual(len(scene["doors"]), 1)
        self.assertEqual(scene["doors"][0]["origin"], [0, 0, 0])

    def test_weapon_light_and_car_are_supported(self):
        scene = apply_command({}, "mets une arme ici", [1, 2, 3])
        scene = apply_command(scene, "mets une lumière 300 ici", [4, 5, 6])
        scene = apply_command(scene, "mets une voiture ici", [7, 8, 9])
        self.assertEqual(len(scene["weapons"]), 1)
        self.assertEqual(len(scene["lights"]), 1)
        self.assertEqual(len(scene["props"]), 1)

    def test_catalog_resolves_spoken_ambulance(self):
        assets = [
            {"path": "models/props_vehicles/ambulance.mdl", "category": "model", "source": "pak01_dir.vpk"},
            {"path": "models/props_vehicles/cara_82hatchback.mdl", "category": "model", "source": "pak01_dir.vpk"},
        ]
        scene = apply_command({}, "mets une ambulance ici", [10, 20, 30], assets=assets)
        self.assertEqual(scene["props"][0]["model"], "models/props_vehicles/ambulance.mdl")
        self.assertEqual(scene["props"][0]["origin"], [10, 20, 30])

    def test_unknown_catalog_prop_is_not_faked(self):
        with self.assertRaises(ValueError):
            apply_command({}, "mets une ambulance ici", [0, 0, 0], assets=[])

    def test_unknown_command_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_command({}, "fais quelque chose")


if __name__ == "__main__":
    unittest.main()
