#!/usr/bin/env python3
"""18 mm köşe sabitleme aparatı — iki varyant.

1) Kulaklı: gövde + iki yanak + kulak (Ø2.5 vida 1→kulak→2)
2) Kulaksız: aynı gövde, yanak/kulak yok

Ortak: 70×22 mm, et 5 mm, U kanal 18 mm.
Kulaklıda kılavuz: kenardan 9 mm, üstten 36 mm, Ø3.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import box as tbox
from trimesh.transformations import rotation_matrix

ROOT = Path(__file__).resolve().parent

CLAMP = 18.0  # U kanal iç genişlik
ENTRY = 18.4  # ağızda hafif giriş
WALL = 5.0  # et kalınlığı (kanal duvarları)
ARM = 70.0
MOUTH = 8.0
H = 22.0
TOP = 5.0
DROP = H - TOP
HOLE_X = 9.0
HOLE_FROM_TOP = 36.0
GUIDE_R = 1.5
SCREW_R = 1.25
EAR_W = 12.0
EAR_T = 4.0
CHEEK_W = 4.5
CHEEK_T = 4.0
CLEAR = 0.35


def box_at(sx, sy, sz, origin) -> trimesh.Trimesh:
    m = tbox(extents=[float(sx), float(sy), float(sz)])
    m.apply_translation([sx / 2, sy / 2, sz / 2])
    m.apply_translation(list(origin))
    return m


def U(a, b):
    return a.union(b, engine="manifold")


def D(a, b):
    return a.difference(b, engine="manifold")


def cyl_x(r, length, n=32) -> trimesh.Trimesh:
    c = trimesh.creation.cylinder(radius=r, height=length, sections=n)
    c.apply_transform(rotation_matrix(np.pi / 2, [0, 1, 0]))
    return c


def cyl_y(r, length, n=32) -> trimesh.Trimesh:
    c = trimesh.creation.cylinder(radius=r, height=length, sections=n)
    c.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
    return c


def build_plain_body() -> trimesh.Trimesh:
    """Kulaksız gövde — yanak yok, vida deliği yok."""
    ch = WALL + CLAMP + WALL
    body = box_at(ARM, ch, H, (0, 0, 0))
    body = U(body, box_at(ch, ARM, H, (0, 0, 0)))
    body = D(body, box_at(ARM - WALL + 1, CLAMP, DROP + 0.2, (WALL, WALL, -0.1)))
    body = D(body, box_at(CLAMP, ARM - WALL + 1, DROP + 0.2, (WALL, WALL, -0.1)))
    flare = (ENTRY - CLAMP) / 2
    body = D(body, box_at(MOUTH + 1, ENTRY, DROP + 0.2, (ARM - MOUTH, WALL - flare, -0.1)))
    body = D(body, box_at(ENTRY, MOUTH + 1, DROP + 0.2, (WALL - flare, ARM - MOUTH, -0.1)))
    win = 9.0
    body = D(body, box_at(28, win, TOP + 2, (14, WALL + (CLAMP - win) / 2, DROP - 1)))
    body = D(body, box_at(win, 28, TOP + 2, (WALL + (CLAMP - win) / 2, 14, DROP - 1)))
    return body


def build_with_ear():
    hole_x = HOLE_X
    hole_z = H - HOLE_FROM_TOP
    body = build_plain_body()

    screw_z = 2.5
    cheek_h = 10.0
    cheek_z0 = screw_z - 4.0
    cheek_y0 = -CHEEK_T
    cheek_dy = CHEEK_T + 1.0
    left_x = hole_x - EAR_W / 2 - CLEAR - CHEEK_W
    right_x = hole_x + EAR_W / 2 + CLEAR
    body = U(body, box_at(CHEEK_W, cheek_dy, cheek_h, (left_x, cheek_y0, cheek_z0)))
    body = U(body, box_at(CHEEK_W, cheek_dy, cheek_h, (right_x, cheek_y0, cheek_z0)))

    ear_y = cheek_y0
    screw_y = cheek_y0 + CHEEK_T / 2
    span = (right_x + CHEEK_W) - left_x + 2
    screw = cyl_x(SCREW_R, span)
    screw.apply_translation([(left_x + right_x + CHEEK_W) / 2, screw_y, screw_z])
    body = D(body, screw)

    ear_bot = hole_z - 5.0
    ear_top = screw_z + 4.0
    flap = box_at(EAR_W, EAR_T, ear_top - ear_bot, (hole_x - EAR_W / 2, ear_y, ear_bot))
    guide = cyl_y(GUIDE_R, EAR_T + 4)
    guide.apply_translation([hole_x, screw_y, hole_z])
    hinge = cyl_x(SCREW_R, EAR_W + 2)
    hinge.apply_translation([hole_x, screw_y, screw_z])
    flap = D(D(flap, guide), hinge)

    assembly = trimesh.util.concatenate([body, flap])
    return assembly, body, flap


def check(body: trimesh.Trimesh) -> None:
    samples = np.array(
        [
            [40.0, WALL + CLAMP / 2, 8.0],
            [WALL + CLAMP / 2, 40.0, 8.0],
            [WALL + 2.0, WALL + CLAMP / 2, 8.0],
            [40.0, WALL / 2, H - 2.0],
            [WALL / 2, WALL / 2, 10.0],
        ]
    )
    inside = body.contains(samples)
    print("inside", inside.tolist(), "(False×3, True×2)")
    if inside[:3].any() or not inside[3:].all():
        raise SystemExit("geometri kontrolü başarısız")


def main() -> None:
    assembly, body_eared, flap = build_with_ear()
    plain = build_plain_body()
    check(plain)
    check(body_eared)

    assembly.export(ROOT / "corner-assembly-square.stl")
    body_eared.export(ROOT / "corner-body.stl")
    flap.export(ROOT / "corner-ear.stl")
    plain.export(ROOT / "corner-plain.stl")
    plain.export(ROOT / "edge-slot-corner-jig.stl")  # viewer 2. ürün

    print(
        f"kulaklı faces={len(assembly.faces)}  "
        f"kulaksız extents={np.round(plain.extents, 1)}  "
        f"H={H} wall={WALL} arm={ARM}"
    )


if __name__ == "__main__":
    main()
