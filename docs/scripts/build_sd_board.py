"""Waveshare Micro SD Storage Board, modelled from the vendor's dimensioned drawing (wiki):
PCB 29.80 x 23.25 mm, 9-pin header on the left edge (top->bottom: 3.3V GND D0 CMD CLK D3 D2 D1 CD),
push-push microSD socket on the right, card slot opening at the right edge.
Shown with a STRAIGHT header soldered underneath (perfboard mounting) instead of the supplied right-angle one.
Frame: origin = PCB bottom-left corner, Z up, PCB top z = 1.6."""
import sys, cadquery as cq
from cadquery import Color, Location as L, Vector as V
out = sys.argv[1]
W, H, T, P = 29.80, 23.25, 1.6, 2.54
a = cq.Assembly(name="Waveshare_MicroSD_Storage_Board")
pcb = cq.Workplane().box(W, H, T, centered=False).edges("|Z").fillet(0.6)
for i in range(9):
    pcb = pcb.cut(cq.Workplane().circle(0.5).extrude(T).translate((1.27, 1.47 + i * P, 0)))
a.add(pcb, name="PCB", color=Color(0.05, 0.25, 0.75))
names = ["CD", "D1", "D2", "D3", "CLK", "CMD", "D0", "GND", "3V3"]          # bottom -> top
OUTWARD = len(sys.argv) > 2 and sys.argv[2] == "outward"   # header on the component side, pins pointing away (for back-face mounting + wires)
for i, n in enumerate(names):
    z0 = -1.0 if OUTWARD else -8.5
    a.add(cq.Workplane().rect(0.64, 0.64).extrude(11.0).translate((1.27, 1.47 + i * P, z0)), name=f"pin_{n}", color=Color(.85, .68, .2))
zb = T if OUTWARD else -2.5
a.add(cq.Workplane().box(2.54, 9 * P, 2.5, centered=(True, False, False)).translate((1.27, 1.47 - P / 2, zb)), name="header_body", color=Color(.1, .1, .1))
# push-push microSD socket (metal shell) + card, socket overhangs right edge by ~0.7 mm
sock = cq.Workplane().box(15.5, 16.3, 1.85, centered=False)
a.add(sock, name="microSD_socket", loc=L(V(15.0, H - 21.3, T)), color=Color(.78, .78, .8))
a.add(cq.Workplane().box(11.0, 15.0, 0.7, centered=False), name="microSD_card", loc=L(V(18.5, H - 20.6, T + 0.6)), color=Color(.12, .12, .14))
# 7x 10k pull-ups + LED resistor + cap (0603) and power LED (0805)
for k in range(8):
    a.add(cq.Workplane().box(1.6, 0.8, 0.45, centered=(True, True, False)), name=f"R{k+1}", loc=L(V(10.3, H - 8.6 - k * 1.95, T)), color=Color(.15, .15, .15))
a.add(cq.Workplane().box(2.0, 1.25, 0.8, centered=(True, True, False)), name="POW_LED", loc=L(V(10.3, H - 2.4, T)), color=Color(.9, .9, .85))
a.add(cq.Workplane().box(1.6, 0.8, 0.8, centered=(True, True, False)), name="C1", loc=L(V(10.3, H - 6.6, T)), color=Color(.75, .6, .45))
a.save(out, "STEP")
print("ok")
