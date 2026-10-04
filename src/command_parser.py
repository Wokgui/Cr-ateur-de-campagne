from __future__ import annotations

import re
import unicodedata
from copy import deepcopy


def _plain(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _numbers(text: str) -> list[float]:
    return [float(v.replace(",", ".")) for v in re.findall(r"\d+(?:[.,]\d+)?", text)]


def _meters_to_source(value: float) -> float:
    # Source units: 1 unit ~= 1 inch.
    return round(value * 39.3701)


def apply_command(scene: dict, command: str, pointer: list[float] | None = None) -> dict:
    """Apply a small French/English VR building command to a scene.

    pointer is the 3D point currently targeted by the VR controller, in Source units.
    The parser is deliberately deterministic: an LLM can later translate richer speech
    into the same scene operations without making the VMF generator dependent on AI.
    """
    result = deepcopy(scene)
    p = pointer or [0, 0, 0]
    text = _plain(command)
    nums = _numbers(text)

    if any(word in text for word in ("piece", "room")):
        width_m = nums[0] if len(nums) >= 1 else 6
        depth_m = nums[1] if len(nums) >= 2 else 4
        height_m = nums[2] if len(nums) >= 3 else 2.7
        result.setdefault("rooms", []).append({
            "origin": p,
            "size": [
                _meters_to_source(width_m),
                _meters_to_source(depth_m),
                _meters_to_source(height_m),
            ],
            "wall_thickness": 8,
            "material": "DEV/DEV_MEASUREGENERIC01",
        })
        return result

    if any(word in text for word in ("porte", "door")):
        result.setdefault("doors", []).append({
            "origin": p,
            "angles": "0 0 0",
            "targetname": f"vr_door_{len(result.get('doors', [])) + 1}",
        })
        return result

    if any(word in text for word in ("horde", "panic")):
        result.setdefault("horde_triggers", []).append({
            "origin": p,
            "radius": 64,
            "targetname": f"vr_horde_{len(result.get('horde_triggers', [])) + 1}",
        })
        return result

    if "supprime" in text or "delete" in text or "remove" in text:
        # Selection IDs will replace this coarse fallback once the VR selection bridge
        # supplies an exact object id.
        for key in ("horde_triggers", "doors", "rooms"):
            if result.get(key):
                result[key].pop()
                return result
        return result

    raise ValueError(f"Commande non reconnue: {command}")
