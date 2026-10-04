from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    @classmethod
    def from_list(cls, values: list[float]) -> "Vec3":
        if len(values) != 3:
            raise ValueError("Expected a 3D vector")
        return cls(float(values[0]), float(values[1]), float(values[2]))

    def source(self) -> str:
        return f"{self.x:g} {self.y:g} {self.z:g}"


def q(value: object) -> str:
    return f'"{value}"'


def block(name: str, items: Iterable[str], indent: int = 0) -> str:
    pad = "\t" * indent
    inner = "\n".join(items)
    return f"{pad}{name}\n{pad}{{\n{inner}\n{pad}}}"


def kv(key: str, value: object, indent: int = 1) -> str:
    return f'{"\t" * indent}{q(key)} {q(value)}'


def plane(a: Vec3, b: Vec3, c: Vec3) -> str:
    return f"({a.source()}) ({b.source()}) ({c.source()})"


def side(side_id: int, p1: Vec3, p2: Vec3, p3: Vec3, material: str) -> str:
    return block(
        "side",
        [
            kv("id", side_id, 2),
            kv("plane", plane(p1, p2, p3), 2),
            kv("material", material, 2),
            kv("uaxis", "[1 0 0 0] 0.25", 2),
            kv("vaxis", "[0 -1 0 0] 0.25", 2),
            kv("rotation", "0", 2),
            kv("lightmapscale", "16", 2),
            kv("smoothing_groups", "0", 2),
        ],
        1,
    )


def box_solid(
    solid_id: int,
    side_id_start: int,
    mins: Vec3,
    maxs: Vec3,
    material: str,
) -> tuple[str, int]:
    x0, y0, z0 = mins.x, mins.y, mins.z
    x1, y1, z1 = maxs.x, maxs.y, maxs.z

    p000 = Vec3(x0, y0, z0)
    p001 = Vec3(x0, y0, z1)
    p010 = Vec3(x0, y1, z0)
    p011 = Vec3(x0, y1, z1)
    p100 = Vec3(x1, y0, z0)
    p101 = Vec3(x1, y0, z1)
    p110 = Vec3(x1, y1, z0)
    p111 = Vec3(x1, y1, z1)

    planes = [
        (p000, p010, p011),
        (p100, p101, p111),
        (p000, p100, p101),
        (p010, p011, p111),
        (p000, p010, p110),
        (p001, p101, p111),
    ]

    sides: list[str] = []
    side_id = side_id_start
    for a, b, c in planes:
        sides.append(side(side_id, a, b, c, material))
        side_id += 1

    solid = block(
        "solid",
        [
            kv("id", solid_id, 1),
            *sides,
        ],
        0,
    )
    return solid, side_id


def room_solids(room: dict, next_solid: int, next_side: int) -> tuple[list[str], int, int]:
    origin = Vec3.from_list(room.get("origin", [0, 0, 0]))
    size = Vec3.from_list(room.get("size", [512, 512, 160]))
    wall = float(room.get("wall_thickness", 16))
    material = room.get("material", "DEV/DEV_MEASUREGENERIC01")

    x0 = origin.x - size.x / 2
    x1 = origin.x + size.x / 2
    y0 = origin.y - size.y / 2
    y1 = origin.y + size.y / 2
    z0 = origin.z
    z1 = origin.z + size.z

    boxes = [
        (Vec3(x0, y0, z0 - wall), Vec3(x1, y1, z0)),
        (Vec3(x0, y0, z1), Vec3(x1, y1, z1 + wall)),
        (Vec3(x0 - wall, y0, z0), Vec3(x0, y1, z1)),
        (Vec3(x1, y0, z0), Vec3(x1 + wall, y1, z1)),
        (Vec3(x0, y0 - wall, z0), Vec3(x1, y0, z1)),
        (Vec3(x0, y1, z0), Vec3(x1, y1 + wall, z1)),
    ]

    solids: list[str] = []
    for mins, maxs in boxes:
        solid, next_side = box_solid(next_solid, next_side, mins, maxs, material)
        solids.append(solid)
        next_solid += 1
    return solids, next_solid, next_side


def entity(entity_id: int, classname: str, props: dict[str, object]) -> str:
    lines = [
        kv("id", entity_id, 1),
        kv("classname", classname, 1),
    ]
    for key, value in props.items():
        lines.append(kv(key, value, 1))
    return block("entity", lines, 0)


def build_vmf(scene: dict) -> str:
    solids: list[str] = []
    entities: list[str] = []

    next_solid = 10
    next_side = 100
    next_entity = 1000

    for room in scene.get("rooms", []):
        created, next_solid, next_side = room_solids(
            room, next_solid=next_solid, next_side=next_side
        )
        solids.extend(created)

    for door in scene.get("doors", []):
        pos = Vec3.from_list(door["origin"])
        entities.append(
            entity(
                next_entity,
                "prop_door_rotating",
                {
                    "origin": pos.source(),
                    "angles": door.get("angles", "0 0 0"),
                    "model": door.get(
                        "model",
                        "models/props_doors/doormainmetal01.mdl",
                    ),
                    "spawnflags": door.get("spawnflags", "8192"),
                    "targetname": door.get("targetname", f"door_{next_entity}"),
                },
            )
        )
        next_entity += 1

    for prop in scene.get("props", []):
        pos = Vec3.from_list(prop["origin"])
        entities.append(
            entity(
                next_entity,
                "prop_physics",
                {
                    "origin": pos.source(),
                    "angles": prop.get("angles", "0 0 0"),
                    "model": prop["model"],
                },
            )
        )
        next_entity += 1

    for weapon in scene.get("weapons", []):
        pos = Vec3.from_list(weapon["origin"])
        entities.append(
            entity(
                next_entity,
                weapon.get("classname", "weapon_spawn"),
                {
                    "origin": pos.source(),
                    "angles": weapon.get("angles", "0 0 0"),
                    "weapon_selection": weapon.get("weapon_selection", "any_primary"),
                },
            )
        )
        next_entity += 1

    for light in scene.get("lights", []):
        pos = Vec3.from_list(light["origin"])
        entities.append(
            entity(
                next_entity,
                "light",
                {
                    "origin": pos.source(),
                    "_light": light.get("brightness", "255 244 214 200"),
                },
            )
        )
        next_entity += 1

    for trigger in scene.get("horde_triggers", []):
        pos = Vec3.from_list(trigger["origin"])
        radius = float(trigger.get("radius", 96))
        targetname = trigger.get("targetname", f"horde_trigger_{next_entity}")

        trigger_mins = Vec3(pos.x - radius, pos.y - radius, pos.z)
        trigger_maxs = Vec3(pos.x + radius, pos.y + radius, pos.z + 128)
        brush, next_side = box_solid(
            next_solid,
            next_side,
            trigger_mins,
            trigger_maxs,
            "TOOLS/TOOLSTRIGGER",
        )

        lines = [
            kv("id", next_entity, 1),
            kv("classname", "trigger_once", 1),
            kv("targetname", targetname, 1),
            kv("spawnflags", "1", 1),
            brush.replace("\n", "\n\t"),
            "\tconnections\n\t{\n"
            + kv("OnTrigger", "horde_director,ForcePanicEvent,,0,-1", 2)
            + "\n\t}",
        ]
        entities.append(block("entity", lines, 0))
        next_entity += 1
        next_solid += 1

    entities.append(
        entity(
            next_entity,
            "info_director",
            {
                "targetname": "horde_director",
                "origin": scene.get("director_origin", "0 0 64"),
            },
        )
    )

    world = block(
        "world",
        [
            kv("id", 1, 1),
            kv("mapversion", 1, 1),
            kv("classname", "worldspawn", 1),
            kv("skyname", scene.get("skyname", "sky_day01_01"), 1),
            *solids,
        ],
        0,
    )

    header = [
        block(
            "versioninfo",
            [
                kv("editorversion", 400, 1),
                kv("editorbuild", 0, 1),
                kv("mapversion", 1, 1),
                kv("formatversion", 100, 1),
                kv("prefab", 0, 1),
            ],
            0,
        ),
        block("visgroups", [], 0),
        block(
            "viewsettings",
            [
                kv("bSnapToGrid", 1, 1),
                kv("bShowGrid", 1, 1),
                kv("bShowLogicalGrid", 0, 1),
                kv("nGridSpacing", 16, 1),
            ],
            0,
        ),
    ]

    return "\n".join([*header, world, *entities]) + "\n"
