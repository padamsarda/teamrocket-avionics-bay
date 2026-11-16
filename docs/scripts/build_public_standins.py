"""Redistributable stand-ins for the three GrabCAD-derived boards (GrabCAD files can't be republished).
Same local frames as the GrabCAD-based models, so the viewer/mount layout is identical:
origin = PCB bottom-left corner, Z up (component side), PCB bottom at z = 0.
  GY-BMP280 6-pin : 15 x 11, header row along X at y = 1.495, BMP280 centre (7.35, 7.55)
  GY-63 (MS5611)  : 13 x 19, header column along Y at x = 0.97, MS5611 centre (10.16, 9.75)
  ESP32-DevKitC V4: 28.1 x 48.26, header rows at x = 1.35 / 26.75, official Espressif WROOM-32E model on top"""
import sys, cadquery as cq
from cadquery import Color, Location as L, Vector as V
DL, OUT = sys.argv[1], sys.argv[2]
P = 2.54; MAG = Color(1, 0, 1); GOLD = Color(.85, .68, .2); BLK = Color(.1, .1, .1)

def marker(a, x, y, zt):
    pin = cq.Workplane().circle(0.18).extrude(zt + 3.0).translate((0, 0, -0.5))
    cross = (cq.Workplane().rect(4.0, 0.25).extrude(0.08).union(cq.Workplane().rect(0.25, 4.0).extrude(0.08))).translate((0, 0, zt))
    ring = cq.Workplane().circle(1.0).circle(0.8).extrude(0.08).translate((0, 0, zt))
    a.add(pin.union(cross).union(ring).union(cq.Workplane().sphere(0.45).translate((0, 0, zt + 3))), name="IC_CENTRE_MARKER", loc=L(V(x, y, 0)), color=MAG)

def pcb(w, h, t, holes=(), r=0.6):
    p = cq.Workplane().box(w, h, t, centered=False).edges("|Z").fillet(r)
    for x, y, d in holes: p = p.cut(cq.Workplane().circle(d / 2).extrude(t).translate((x, y, 0)))
    return p

def header(a, pts, t, name, plastic=2.54):
    for i, (x, y) in enumerate(pts):
        a.add(cq.Workplane().rect(0.64, 0.64).extrude(11.5).translate((x, y, -8.9)), name=f"{name}_pin{i+1}", color=GOLD)
        a.add(cq.Workplane().box(2.54, 2.54, plastic, centered=(True, True, False)).translate((x, y, -plastic)), name=f"{name}_body{i+1}", color=BLK)

def smd(a, n, x, y, t, w=1.6, d=0.8, h=0.5, rot=0, col=Color(.15, .15, .15)):
    a.add(cq.Workplane().box(w, d, h, centered=(True, True, False)), name=n, loc=L(V(x, y, t), V(0, 0, 1), rot), color=col)

# ---- GY-BMP280 ----
T = 1.57
a = cq.Assembly(name="GY-BMP280_public")
a.add(pcb(15.0, 11.0, T, [(2.2, 8.8, 3.0), (12.8, 8.8, 3.0)]), name="PCB", color=Color(.42, .12, .45))
header(a, [(1.155 + i * P, 1.495) for i in range(6)], T, "J1")
a.add(cq.importers.importStep(f"{DL}/k3d/Package_LGA.3dshapes/Bosch_LGA-8_2x2.5mm_P0.65mm_ClockwisePinNumbering.step"),
      name="BMP280_LGA8", loc=L(V(7.35, 7.55, T)), color=Color(.8, .8, .82))
for k, x in enumerate((4.0, 6.4, 8.8, 11.2)): smd(a, f"R{k+1}", x, 4.3, T, rot=90)
smd(a, "C1", 4.2, 7.6, T, h=0.8, col=Color(.75, .6, .45))
marker(a, 7.35, 7.55, 2.52); a.save(f"{OUT}/BMP280_GY-BMP280_public.step", "STEP")

# ---- GY-63 MS5611 ----
T = 1.55
a = cq.Assembly(name="GY-63_MS5611_public")
a.add(pcb(13.0, 19.0, T, [(10.5, 2.5, 3.0)]), name="PCB", color=Color(.05, .25, .75))
header(a, [(0.97, 1.9 + i * P) for i in range(7)], T, "J1")
a.add(cq.Workplane().box(3.0, 5.0, 0.45, centered=(True, True, False)), name="MS5611_ceramic", loc=L(V(10.16, 9.75, T)), color=Color(.9, .9, .85))
a.add(cq.Workplane().box(2.7, 4.6, 0.25, centered=(True, True, False)).edges("|Z").fillet(0.3), name="MS5611_cap", loc=L(V(10.16, 9.75, T + 0.45)), color=Color(.78, .78, .8))
a.add(cq.Workplane().box(2.9, 1.6, 1.1, centered=(True, True, False)), name="LDO_662K", loc=L(V(6.5, 16.5, T)), color=BLK)
for k in range(2): a.add(cq.Workplane().box(2.9, 1.6, 1.1, centered=(True, True, False)), name=f"Q{k+1}", loc=L(V(5.0, 12.0 - 3.5 * k, T)), color=BLK)
smd(a, "C1", 10.0, 16.0, T, w=3.2, d=1.6, h=1.6, col=Color(.85, .65, .1))
for k, y in enumerate((4.0, 6.0, 8.0, 14.0)): smd(a, f"R{k+1}", 5.5, y, T)
marker(a, 10.16, 9.75, 2.25); a.save(f"{OUT}/MS5611_GY-63_public.step", "STEP")

# ---- ESP32-DevKitC V4 (PCB + official Espressif module) ----
T = 1.6
a = cq.Assembly(name="ESP32-DevKitC-V4_public")
a.add(pcb(28.1, 48.26, T, r=1.0), name="PCB", color=Color(.06, .06, .07))
header(a, [(1.35, 1.27 + i * P) for i in range(19)] + [(26.75, 1.27 + i * P) for i in range(19)], T, "J")
a.add(cq.importers.importStep(f"{DL}/esp/3dmodels/espressif.3dshapes/ESP32-WROOM-32E.STEP"), name="ESP32-WROOM-32E_Espressif", loc=L(V(5.05, 28.76, T)), color=Color(.72, .72, .75))
a.add(cq.Workplane().box(7.6, 5.6, 2.9, centered=(True, False, False)), name="microUSB", loc=L(V(14.05, -0.6, T)), color=Color(.75, .75, .78))
for x in (6.0, 22.1): a.add(cq.Workplane().box(4.0, 3.0, 1.8, centered=(True, True, False)), name=f"button_{x:.0f}", loc=L(V(x, 4.5, T)), color=Color(.8, .8, .8))
a.add(cq.Workplane().box(6.5, 3.5, 1.6, centered=(True, True, False)), name="AMS1117", loc=L(V(8.5, 12.0, T)), color=BLK)
a.add(cq.Workplane().box(5.0, 5.0, 0.9, centered=(True, True, False)), name="USB_UART", loc=L(V(19.0, 13.0, T)), color=BLK)
marker(a, 12.55, 28.76 + 10.29, T + 3.2); a.save(f"{OUT}/ESP32-DevKitC-V4_public.step", "STEP")
print("ok")
