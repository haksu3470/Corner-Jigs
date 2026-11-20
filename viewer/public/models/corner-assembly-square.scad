// Gövde 70×22, et 3, kanal 18. Kulak iki yanak arasında. Vida Ø2.5.
// Kılavuz: kenardan 9, üstten 36, Ø3.

clamp = 18;
entry = 18.4;
wall = 3;
arm = 70;
h = 22;
top = 5;
drop = h - top;
mouth = 8;
hole_x = 9;
hole_from_top = 36;
hole_z = h - hole_from_top;
screw_r = 1.25;
guide_r = 1.5;
ear_w = 12;
ear_t = 4;
cheek_w = 4.5;
cheek_t = 4;
clear = 0.35;
ch = wall + clamp + wall;
screw_z = 2.5;
cheek_y0 = -cheek_t;
cheek_dy = cheek_t + 1;
ear_y = cheek_y0;
screw_y = cheek_y0 + cheek_t / 2;
left_x = hole_x - ear_w / 2 - clear - cheek_w;
right_x = hole_x + ear_w / 2 + clear;
ear_bot = hole_z - 5;
ear_top = screw_z + 4;

module body() {
  difference() {
    union() {
      cube([arm, ch, h]);
      cube([ch, arm, h]);
      translate([left_x, cheek_y0, screw_z - 4]) cube([cheek_w, cheek_dy, 10]);
      translate([right_x, cheek_y0, screw_z - 4]) cube([cheek_w, cheek_dy, 10]);
    }
    translate([wall, wall, -0.1]) cube([arm - wall + 1, clamp, drop + 0.2]);
    translate([wall, wall, -0.1]) cube([clamp, arm - wall + 1, drop + 0.2]);
    flare = (entry - clamp) / 2;
    translate([arm - mouth, wall - flare, -0.1]) cube([mouth + 1, entry, drop + 0.2]);
    translate([wall - flare, arm - mouth, -0.1]) cube([entry, mouth + 1, drop + 0.2]);
    win = 9;
    translate([14, wall + (clamp - win) / 2, drop - 1]) cube([28, win, top + 2]);
    translate([wall + (clamp - win) / 2, 14, drop - 1]) cube([win, 28, top + 2]);
    translate([(left_x + right_x + cheek_w) / 2, screw_y, screw_z])
      rotate([0, 90, 0]) cylinder(h = (right_x + cheek_w) - left_x + 2, r = screw_r, center = true, $fn = 28);
  }
}

module ear() {
  difference() {
    translate([hole_x - ear_w / 2, ear_y, ear_bot])
      cube([ear_w, ear_t, ear_top - ear_bot]);
    translate([hole_x, screw_y, hole_z])
      rotate([90, 0, 0]) cylinder(h = ear_t + 4, r = guide_r, center = true, $fn = 28);
    translate([hole_x, screw_y, screw_z])
      rotate([0, 90, 0]) cylinder(h = ear_w + 2, r = screw_r, center = true, $fn = 28);
  }
}

body();
ear();
