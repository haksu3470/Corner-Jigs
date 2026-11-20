// Gövde 70×22, et 3, kanal 18.
// Kulak = dış etin devamı (y=0..wall), z=0'da basamaksız birleşir.
// Yanaklar aynı ette, sadece X'te kalın (kulağı tutmak için).

clamp = 18;
entry = 18.4;
wall = 3;
arm = 70;
h = 22;
top = 5;
drop = h - top;
mouth = 8;
ear_w = 12;
cheek_w = 7;
clear = 0.25;
hole_x = cheek_w + clear + ear_w / 2 + 3;
hole_from_top = 36;
hole_z = h - hole_from_top;
screw_r = 1.25;
guide_r = 1.5;
ear_t = wall;
ch = wall + clamp + wall;
screw_z = -3;
screw_y = wall / 2;
left_x = hole_x - ear_w / 2 - clear - cheek_w;
right_x = hole_x + ear_w / 2 + clear;
cheek_z0 = hole_z - 5;
cheek_top = 0;
cheek_h = cheek_top - cheek_z0;
ear_bot = hole_z - 5;
ear_top = 0;
slot_x0 = hole_x - ear_w / 2 - clear;
slot_w = ear_w + 2 * clear;

module body() {
  difference() {
    union() {
      cube([arm, ch, h]);
      cube([ch, arm, h]);
      translate([left_x, 0, cheek_z0]) cube([cheek_w, wall, cheek_h]);
      translate([right_x, 0, cheek_z0]) cube([cheek_w, wall, cheek_h]);
    }
    translate([wall, wall, -0.1]) cube([arm - wall + 1, clamp, drop + 0.2]);
    translate([wall, wall, -0.1]) cube([clamp, arm - wall + 1, drop + 0.2]);
    flare = (entry - clamp) / 2;
    translate([arm - mouth, wall - flare, -0.1]) cube([mouth + 1, entry, drop + 0.2]);
    translate([wall - flare, arm - mouth, -0.1]) cube([entry, mouth + 1, drop + 0.2]);
    win = 9;
    translate([14, wall + (clamp - win) / 2, drop - 1]) cube([28, win, top + 2]);
    translate([wall + (clamp - win) / 2, 14, drop - 1]) cube([win, 28, top + 2]);
    translate([slot_x0, -0.02, -0.05]) cube([slot_w, wall + 0.05, 3]);
    translate([(left_x + right_x + cheek_w) / 2, screw_y, screw_z])
      rotate([0, 90, 0]) cylinder(h = (right_x + cheek_w) - left_x + 2, r = screw_r, center = true, $fn = 28);
  }
}

module ear() {
  difference() {
    translate([hole_x - ear_w / 2, 0, ear_bot])
      cube([ear_w, ear_t, ear_top - ear_bot]);
    translate([hole_x, screw_y, hole_z])
      rotate([90, 0, 0]) cylinder(h = ear_t + 4, r = guide_r, center = true, $fn = 28);
    translate([hole_x, screw_y, screw_z])
      rotate([0, 90, 0]) cylinder(h = ear_w + 2, r = screw_r, center = true, $fn = 28);
  }
}

body();
ear();
