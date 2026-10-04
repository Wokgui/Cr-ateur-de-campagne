from src.asset_resolver import resolve_asset

ASSETS=[
 {"path":"models/props_vehicles/cara_82hatchback.mdl","category":"model","source":"pak01_dir.vpk"},
 {"path":"models/props_vehicles/ambulance.mdl","category":"model","source":"pak01_dir.vpk"},
 {"path":"models/props_interiors/shelf.mdl","category":"model","source":"pak01_dir.vpk"},
]
def test_french_car_alias(): assert "cara_" in resolve_asset("voiture",ASSETS)["path"]
def test_exact_ambulance_wins(): assert resolve_asset("ambulance",ASSETS)["path"].endswith("ambulance.mdl")
def test_unknown_returns_none(): assert resolve_asset("dragon spatial",ASSETS) is None
