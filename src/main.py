from __future__ import annotations

import argparse
import json
from pathlib import Path

from vmf_generator import build_vmf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Left 4 Dead 2 VMF prototype from a scene JSON file."
    )
    parser.add_argument("scene", type=Path, help="Path to the scene JSON file")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("build/generated.vmf"),
        help="Output VMF path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene = json.loads(args.scene.read_text(encoding="utf-8"))
    vmf = build_vmf(scene)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(vmf, encoding="utf-8")
    print(f"Generated {args.out}")


if __name__ == "__main__":
    main()
