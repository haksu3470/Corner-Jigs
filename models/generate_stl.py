#!/usr/bin/env python3
"""18 mm köşe sabitleme aparatı — iki varyant.

Kulaklı: dış et (y=0..WALL) aşağı doğru iki yanak + arada kulak.
- Kulak et kalınlığının devamı; suntaya (y=WALL) yaslanır; gövdeden taşmaz.
- Gövde ile kulak arasında basamak/yükseklik farkı yok (z=0'da birleşir).
- Yanaklar sadece X'te kalın (kulağı tutmak için); kanala veya dışarı şişmez.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import box as tbox
from trimesh.transformations import rotation_matrix

ROOT = Path(__file__).resolve().parent

CLAMP = 18.0
ENTRY = 18.4
WALL = 3.0
ARM = 70.0
MOUTH = 8.0
H = 22.0
TOP = 5.0
DROP = H - TOP

# Kulak konumu: dış et üzerinde, yanaklar x>0 içinde kalsın
EAR_W = 12.0
CHEEK_W = 7.0  # tutan yanakların X kalınlığı
CLEAR = 0.25
HOLE_X = CHEEK_W + CLEAR + EAR_W / 2 + 3.0  # ≈ 16.25
HOLE_FROM_TOP = 36.0
GUIDE_R = 1.5
SCREW_R = 1.25
EAR_T = WALL  # et devamı


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
    hole_z = H - HOLE_FROM_TOP  # 22-36 = -14
    body = build_plain_body()

    # Dış et zarfı: y=[0, WALL] — taşma yok, sunta yüzeyi y=WALL
    ear_y = 0.0
    cheek_y0 = 0.0
    cheek_dy = WALL

    left_x = hole_x - EAR_W / 2 - CLEAR - CHEEK_W
    right_x = hole_x + EAR_W / 2 + CLEAR

    # Yanaklar: gövde alt yüzünden (z=0) aşağı — etin düz devamı, basamak yok
    cheek_z0 = hole_z - 5.0
    cheek_top = 0.0  # z=0'da gövdeye flush birleşir
    cheek_h = cheek_top - cheek_z0

    # Gövde dış etinde kulak yuvası (yanaklar arası), z=0'dan biraz içeri
    slot_x0 = hole_x - EAR_W / 2 - CLEAR
    slot_w = EAR_W + 2 * CLEAR
    body = D(
        body,
        box_at(slot_w, WALL + 0.05, 3.0, (slot_x0, -0.02, -0.05)),
    )

    # İki yanak — et devamı (Y=WALL), X'te kalın
    body = U(body, box_at(CHEEK_W, cheek_dy, cheek_h, (left_x, cheek_y0, cheek_z0)))
    body = U(body, box_at(CHEEK_W, cheek_dy, cheek_h, (right_x, cheek_y0, cheek_z0)))

    # Menteşe: yanakların üstünde, gövdeye yakın
    screw_z = -3.0
    screw_y = WALL / 2
    span = (right_x + CHEEK_W) - left_x + 2
    screw = cyl_x(SCREW_R, span)
    screw.apply_translation([(left_x + right_x + CHEEK_W) / 2, screw_y, screw_z])
    body = D(body, screw)

    # Kulak: et kalınlığı, z=0'a kadar (basamaksız birleşim)
    ear_bot = hole_z - 5.0
    ear_top = 0.0
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

    b = assembly.bounds
    print(f"bounds X {b[0,0]:.2f}→{b[1,0]:.2f}  Y {b[0,1]:.2f}→{b[1,1]:.2f}  Z {b[0,2]:.2f}→{b[1,2]:.2f}")
    if b[0, 1] < -0.05:
        raise SystemExit(f"Y taşması: {b[0,1]}")
    if b[0, 0] < -0.05:
        raise SystemExit(f"X taşması: {b[0,0]}")

    assembly.export(ROOT / "corner-assembly-square.stl")
    body_eared.export(ROOT / "corner-body.stl")
    flap.export(ROOT / "corner-ear.stl")
    plain.export(ROOT / "corner-plain.stl")
    plain.export(ROOT / "edge-slot-corner-jig.stl")

    print(
        f"ok wall={WALL} ear_t={EAR_T} cheek_w={CHEEK_W} "
        f"hole_x={HOLE_X:.1f} faces={len(assembly.faces)}"
    )


if __name__ == "__main__":
    main()
