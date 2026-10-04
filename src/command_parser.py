from __future__ import annotations

import math
import re
import unicodedata
import uuid
from copy import deepcopy


COLLECTIONS = ("rooms", "doors", "horde_triggers", "props", "weapons", "lights")


def _plain(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _numbers(text: str) -> list[float]:
    return [float(v.replace(",", ".")) for v in re.findall(r"\d+(?:[.,]\d+)?", text)]


def _meters_to_source(value: float) -> float:
    return round(value * 39.3701)


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _nearest(scene: dict, pointer: list[float]) -> tuple[str, int] | None:
    best = None
    best_distance = float("inf")
    for collection in COLLECTIONS:
        for index, item in enumerate(scene.get(collection, [])):
            origin = item.get("origin")
            if not isinstance(origin, list) or len(origin) != 3:
                continue
            distance = math.dist([float(v) for v in origin], [float(v) for v in pointer])
            if distance < best_distance:
                best_distance = distance
                best = (collection, index)
    return best


def apply_command(
    scene: dict,
    command: str,
    pointer: list[float] | None = None,
    selected_id: str | None = None,
) -> dict:
    """Apply a deterministic VR building command.

    Richer speech/AI layers should translate into these same scene operations.
    """
    result = deepcopy(scene)
    p = pointer or [0, 0, 0]
    text = _plain(command)
    nums = _numbers(text)

    if any(word in text for word in ("piece", "room")) and not any(
        word in text for word in ("deplace", "supprime", "tourne")
    ):
        width_m = nums[0] if len(nums) >= 1 else 6
        depth_m = nums[1] if len(nums) >= 2 else 4
        height_m = nums[2] if len(nums) >= 3 else 2.7
        result.setdefault("rooms", []).append({
            "id": _id("room"),
            "origin": p,
            "size": [_meters_to_source(width_m), _meters_to_source(depth_m), _meters_to_source(height_m)],
            "wall_thickness": 8,
            "material": "DEV/DEV_MEASUREGENERIC01",
        })
        return result

    if any(word in text for word in ("porte", "door")) and not any(
        word in text for word in ("deplace", "supprime", "tourne")
    ):
        result.setdefault("doors", []).append({
            "id": _id("door"),
            "origin": p,
            "angles": "0 0 0",
            "targetname": f"vr_door_{len(result.get('doors', [])) + 1}",
        })
        return result

    if any(word in text for word in ("horde", "panic")):
        result.setdefault("horde_triggers", []).append({
            "id": _id("horde"),
            "origin": p,
            "radius": 64,
            "targetname": f"vr_horde_{len(result.get('horde_triggers', [])) + 1}",
        })
        return result

    if any(word in text for word in ("arme", "weapon", "fusil")):
        result.setdefault("weapons", []).append({
            "id": _id("weapon"),
            "origin": p,
            "classname": "weapon_spawn",
            "weapon_selection": "any_primary",
        })
        return result

    if any(word in text for word in ("lumiere", "light")):
        brightness = int(nums[0]) if nums else 200
        result.setdefault("lights", []).append({
            "id": _id("light"),
            "origin": p,
            "brightness": f"255 244 214 {brightness}",
        })
        return result

    prop_words = ("voiture", "car", "ambulance", "camion", "etagere", "chaise", "table", "lit", "poubelle", "barriere")
    if any(word in text for word in prop_words):
        match = resolve_asset(text, assets or [], "model") if assets else None
        fallback = "models/props_vehicles/cara_82hatchback.mdl" if any(word in text for word in ("voiture", "car")) else None
        if not match and not fallback:
            raise ValueError("Aucun asset L4D2 correspondant dans le catalogue")
        result.setdefault("props", []).append({
            "id": _id("prop"),
            "origin": p,
            "angles": "0 0 0",
            "model": match["path"] if match else fallback,
            "asset_source": match.get("source") if match else "builtin-fallback",
        })
        return result

    target = None
    if selected_id:
        for collection in COLLECTIONS:
            for index, item in enumerate(result.get(collection, [])):
                if item.get("id") == selected_id:
                    target = (collection, index)
                    break
            if target:
                break
    if target is None:
        target = _nearest(result, p)

    if "supprime" in text or "delete" in text or "remove" in text:
        if target:
            collection, index = target
            result[collection].pop(index)
        return result

    if "deplace" in text or "move" in text:
        if not target:
            raise ValueError("Aucun objet à déplacer")
        collection, index = target
        result[collection][index]["origin"] = p
        return result

    if "tourne" in text or "rotate" in text:
        if not target:
            raise ValueError("Aucun objet à tourner")
        angle = nums[0] if nums else 90
        collection, index = target
        result[collection][index]["angles"] = f"0 {angle:g} 0"
        return result

    raise ValueError(f"Commande non reconnue: {command}")
