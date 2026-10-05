import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from vr_bridge import State, make_handler

class BridgeTests(unittest.TestCase):
    def test_http_catalog_persistence_and_vmf(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            catalog=root/"assets.json"
            catalog.write_text(json.dumps({"assets":[{"path":"models/props_vehicles/ambulance.mdl","category":"model"}]}))
            state=State(root/"scene.json", root/"scene.vmf", catalog)
            server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(state))
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            base=f"http://127.0.0.1:{server.server_port}"
            try:
                self.assertEqual(json.load(urlopen(base+"/health"))["service"],"l4d2vr-builder")
                for command in ("cree une piece de 6 par 4 metres", "mets une ambulance ici"):
                    payload=json.dumps({"command":command,"pointer":[0,0,0]}).encode()
                    self.assertTrue(json.load(urlopen(Request(base+"/command",payload,{"Content-Type":"application/json"})))["ok"])
                self.assertEqual(State(root/"scene.json",root/"scene.vmf").scene,state.scene)
                vmf=(root/"scene.vmf").read_text()
                self.assertIn("info_player_start",vmf)
                self.assertEqual(vmf.count('"classname" "info_survivor_position"'),4)
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(base+"/command",b'{"command":"inconnue"}',{"Content-Type":"application/json"}))
                self.assertEqual(error.exception.code,400)
            finally:
                server.shutdown(); server.server_close(); thread.join()
