// İkinci ürün = kulaksız gövde (corner-plain ile aynı).
// 70×22, et 5 mm, U kanal 18 mm.

clamp = 18;
entry = 18.4;
wall = 5;
arm = 70;
h = 22;
top = 5;
drop = h - top;
mouth = 8;
ch = wall + clamp + wall;

difference() {
  union() {
    cube([arm, ch, h]);
    cube([ch, arm, h]);
  }
  translate([wall, wall, -0.1]) cube([arm - wall + 1, clamp, drop + 0.2]);
  translate([wall, wall, -0.1]) cube([clamp, arm - wall + 1, drop + 0.2]);
  flare = (entry - clamp) / 2;
  translate([arm - mouth, wall - flare, -0.1]) cube([mouth + 1, entry, drop + 0.2]);
  translate([wall - flare, arm - mouth, -0.1]) cube([entry, mouth + 1, drop + 0.2]);
  win = 9;
  translate([14, wall + (clamp - win) / 2, drop - 1]) cube([28, win, top + 2]);
  translate([wall + (clamp - win) / 2, 14, drop - 1]) cube([win, 28, top + 2]);
}
