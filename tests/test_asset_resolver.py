from src.asset_resolver import resolve_asset

ASSETS=[
 {"path":"models/props_vehicles/cara_82hatchback.mdl","category":"model","source":"pak01_dir.vpk"},
 {"path":"models/props_vehicles/ambulance.mdl","category":"model","source":"pak01_dir.vpk"},
 {"path":"models/props_interiors/shelf.mdl","category":"model","source":"pak01_dir.vpk"},
]
import unittest
class ResolverTests(unittest.TestCase):
    def test_french_alias(self): self.assertIn("cara_", resolve_asset("voiture", ASSETS)["path"])
    def test_exact_match(self): self.assertTrue(resolve_asset("ambulance", ASSETS)["path"].endswith("ambulance.mdl"))
    def test_unknown(self): self.assertIsNone(resolve_asset("dragon spatial", ASSETS))
