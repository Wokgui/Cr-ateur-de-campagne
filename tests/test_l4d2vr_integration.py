import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IntegrationFilesTests(unittest.TestCase):
    def test_builder_action_fragment_is_valid_json(self):
        path = ROOT / "integration" / "l4d2vr" / "builder_action_manifest.fragment.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        names = {a["name"] for a in data["actions"]}
        self.assertIn("/actions/builder/in/ToggleBuilder", names)
        self.assertIn("/actions/builder/in/Place", names)
        self.assertEqual(data["action_sets"][0]["name"], "/actions/builder")

    def test_cpp_client_is_loopback_only(self):
        path = ROOT / "integration" / "l4d2vr" / "builder_client.cpp"
        code = path.read_text(encoding="utf-8")
        self.assertIn('L"127.0.0.1"', code)
        self.assertNotIn("http://", code)
        self.assertNotIn("https://", code)


if __name__ == "__main__":
    unittest.main()
