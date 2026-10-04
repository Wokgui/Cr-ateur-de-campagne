from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from command_parser import apply_command
from vmf_generator import build_vmf


class State:
    def __init__(self, scene_path: Path, vmf_path: Path) -> None:
        self.scene_path = scene_path
        self.vmf_path = vmf_path
        self.scene = self._load()

    def _load(self) -> dict:
        if self.scene_path.exists():
            return json.loads(self.scene_path.read_text(encoding="utf-8"))
        return {"rooms": [], "doors": [], "horde_triggers": []}

    def save(self) -> None:
        self.scene_path.parent.mkdir(parents=True, exist_ok=True)
        self.vmf_path.parent.mkdir(parents=True, exist_ok=True)
        self.scene_path.write_text(
            json.dumps(self.scene, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.vmf_path.write_text(build_vmf(self.scene), encoding="utf-8")


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._json(200, {"ok": True})
            elif self.path == "/scene":
                self._json(200, state.scene)
            else:
                self._json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            if self.path != "/command":
                self._json(404, {"error": "not_found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(length) or b"{}")
                command = str(data["command"])
                pointer = data.get("pointer", [0, 0, 0])
                selected_id = data.get("selected_id")
                state.scene = apply_command(state.scene, command, pointer, selected_id)
                state.save()
                self._json(200, {"ok": True, "scene": state.scene})
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                self._json(400, {"ok": False, "error": str(exc)})

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Local bridge for the L4D2 VR builder")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--scene", type=Path, default=Path("build/live_scene.json"))
    parser.add_argument("--vmf", type=Path, default=Path("build/live_scene.vmf"))
    args = parser.parse_args()

    state = State(args.scene, args.vmf)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    print(f"VR bridge listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
