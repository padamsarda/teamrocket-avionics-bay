"""SmartElex 6DoF LSM6DSO breakout (Robu R101054) = SparkFun Qwiic 6DoF LSM6DSO layout (SEN-18020),
rotated 90 deg CW so the 2.54 headers run down the left/right edges and the Qwiic ports sit top/bottom
(matches the Robu product photos). All part positions come from SparkFun's Eagle .brd (CC BY-SA 4.0).
Frame: origin = PCB bottom-left corner, Z up, PCB top z = 1.6."""
import sys, xml.etree.ElementTree as ET, cadquery as cq
from cadquery import Color, Location as L, Vector as V
brd, k3d_ic, out, png = sys.argv[1:5]
S, T = 25.4, 1.6
rot = lambda x, y: (y, S - x)                      # SparkFun coords -> SmartElex orientation (90 deg CW)
r = ET.parse(brd).getroot()
E = {e.get("name"): e for e in r.find(".//board/elements")}
def pos(n):
    e = E[n]; return rot(float(e.get("x")), float(e.get("y")))
def ang(n):
    a = e = E[n].get("rot") or "R0"; return float(a.lstrip("MR")) - 90

a = cq.Assembly(name="LSM6DSO_SmartElex_6DoF")
pcb = cq.Workplane().box(S, S, T, centered=False).edges("|Z").fillet(1.0)
for n in ("STANDOFF1", "STANDOFF2", "STANDOFF3", "STANDOFF4"):
    x, y = pos(n); pcb = pcb.cut(cq.Workplane().circle(3.048 / 2).extrude(T).translate((x, y, 0)))
for n in ("JP1", "JP3"):                            # 1x06 header holes, drill 1.016
    e = E[n]; x0, y0 = float(e.get("x")), float(e.get("y")); s = -1 if e.get("rot") == "R180" else 1
    for i in range(6):
        x, y = rot(x0 + s * i * 2.54, y0); pcb = pcb.cut(cq.Workplane().circle(0.508).extrude(T).translate((x, y, 0)))
a.add(pcb, name="PCB", color=Color(0.05, 0.05, 0.05))

icx, icy = pos("U1")
a.add(cq.importers.importStep(k3d_ic), name="LSM6DSO_LGA14", loc=L(V(icx, icy, T), V(0, 0, 1), 90), color=Color(0.15, 0.15, 0.15))

for n in ("J1", "J2"):                              # JST SM04B-SRSS-TB, opening faces board edge
    x, y = pos(n); body = cq.Workplane().box(6.0, 4.25, 2.95, centered=(True, False, False)).translate((0, -4.6, 0))
    a.add(body, name=f"Qwiic_{n}", loc=L(V(x, y, T), V(0, 0, 1), ang(n)), color=Color(0.95, 0.92, 0.82))

for n, (w, d, h, c) in {"C3": (1.6, .8, .8, (.75, .6, .45)), "C4": (1.6, .8, .8, (.75, .6, .45)), "L1": (1.6, .8, .8, (.2, .2, .2)),
                         "R1": (1.6, .8, .45, (.15, .15, .15)), "R2": (1.6, .8, .45, (.15, .15, .15)), "R3": (1.6, .8, .45, (.15, .15, .15)),
                         "R4": (1.6, .8, .45, (.15, .15, .15)), "R5": (1.6, .8, .45, (.15, .15, .15)), "D1": (1.6, .8, .6, (.3, .9, .3))}.items():
    x, y = pos(n); a.add(cq.Workplane().box(w, d, h, centered=(True, True, False)), name=n, loc=L(V(x, y, T), V(0, 0, 1), ang(n)), color=Color(*c))

# loose 6-pin headers shown soldered on the bottom (breadboard / perfboard style)
for n in ("JP1", "JP3"):
    e = E[n]; x0, y0 = float(e.get("x")), float(e.get("y")); s = -1 if e.get("rot") == "R180" else 1
    pts = [rot(x0 + s * i * 2.54, y0) for i in range(6)]
    for i, (x, y) in enumerate(pts):
        a.add(cq.Workplane().rect(0.64, 0.64).extrude(11.0).translate((x, y, -8.5)), name=f"{n}_pin{i+1}", color=Color(.85, .68, .2))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    a.add(cq.Workplane().box(2.54, 6 * 2.54, 2.5, centered=(True, True, False)).translate((xs[0], sum(ys) / 6, -2.5)), name=f"{n}_body", color=Color(.1, .1, .1))

# IC centre marker + sensor axes (from SparkFun package: sensor +X/+Y; after rotation X -> board +Y, Y -> board -X)
zt = T + 0.86
pin = cq.Workplane().circle(0.18).extrude(zt + 3.0).translate((0, 0, -0.5))
cross = (cq.Workplane().rect(4.0, 0.25).extrude(0.08).union(cq.Workplane().rect(0.25, 4.0).extrude(0.08))).translate((0, 0, zt))
ring = cq.Workplane().circle(1.0).circle(0.8).extrude(0.08).translate((0, 0, zt))
ball = cq.Workplane().sphere(0.45).translate((0, 0, zt + 3.0))
a.add(pin.union(cross).union(ring).union(ball), name="IC_CENTRE_MARKER", loc=L(V(icx, icy, 0)), color=Color(1, 0, 1))
arrow = lambda: cq.Workplane().rect(0.3, 5.0).extrude(0.1).translate((0, 2.5, 0)).union(cq.Workplane().polyline([(-0.6, 5), (0.6, 5), (0, 6)]).close().extrude(0.1))
a.add(arrow(), name="SENSOR_AXIS_X", loc=L(V(icx, icy, zt + 3.0)), color=Color(1, 0, 0))
a.add(arrow(), name="SENSOR_AXIS_Y", loc=L(V(icx, icy, zt + 3.0), V(0, 0, 1), 90), color=Color(0, 0.8, 0))
a.save(out, "STEP")
print("IC centre", round(icx, 3), round(icy, 3), zt)

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from matplotlib.collections import PolyCollection
parts = []
for nm, ch in a.traverse():
    if ch.obj is None: continue
    shp = cq.Compound.makeCompound(ch.obj.vals()) if hasattr(ch.obj, "vals") else ch.obj
    shp = shp.moved(ch.loc); vs, tr = shp.tessellate(0.05)
    if not tr: continue
    v = np.array([[q.x, q.y, q.z] for q in vs]); k = v[:, 2].max() + (100 if ("MARKER" in nm or "AXIS" in nm) else 0)
    parts.append((k, v, np.array(tr), ch.color.toTuple()[:3]))
parts.sort(key=lambda p: p[0]); fig, ax = plt.subplots(figsize=(6, 6))
for _, v, tr, c in parts: ax.add_collection(PolyCollection(v[tr][:, :, :2], facecolor=c, edgecolor=c, linewidth=0.2))
ax.set_xlim(-1, 26.4); ax.set_ylim(-1, 26.4); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_title("LSM6DSO SmartElex top view (red = sensor +X, green = +Y)"); fig.savefig(png, dpi=120, bbox_inches="tight")
