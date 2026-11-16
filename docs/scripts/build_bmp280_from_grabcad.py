"""Re-orient GrabCAD 'bmp280-module-1' STEP into the bay frame and mark the BMP280 centre.
Source frame: board in XZ plane, IC side = +Y, header edge at x=+1.67.
Target frame: origin = PCB bottom-left corner, X = 15 mm side, Y = 11 mm side (header edge at y~0), Z up, PCB top z=1.57."""
import sys, csv, cadquery as cq
from cadquery import Color, Location as L, Vector as V
from OCP.gp import gp_Trsf, gp_Ax3, gp_Pnt, gp_Dir
src, out_step, csv_path = sys.argv[1:4]
shape = cq.importers.importStep(src)

# new axes expressed in old coords: X' = -z, Y' = -x, Z' = +y ; origin at old (1.67, -24.43, 10.9)
t = gp_Trsf()
t.SetTransformation(gp_Ax3(gp_Pnt(1.67, -24.43, 10.9), gp_Dir(0, 1, 0), gp_Dir(0, 0, -1)))
loc = cq.Location(t)

MAG = Color(1, 0, 1)
a = cq.Assembly(name="BMP280_GY-BMP280_GrabCAD")
ic_c = None
for i, s in enumerate(shape.solids().vals()):
    s2 = s.moved(loc); b = s2.BoundingBox()
    dims = sorted([round(b.xlen, 2), round(b.ylen, 2), round(b.zlen, 2)])
    if dims == [1.57, 11.0, 15.0]:
        name, col = "PCB", Color(0.05, 0.15, 0.6)
    elif dims == [0.97, 2.0, 2.5]:
        name, col = "BMP280_LGA8", Color(0.82, 0.82, 0.85)
        ic_c = ((b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2, b.zmax)
    elif max(dims) > 12:
        name, col = f"header_pin_{i}", Color(0.85, 0.68, 0.2)
    elif dims == [0.9, 0.9, 1.7] or dims == [0.9, 0.9, 1.7]:
        name, col = f"cap_{i}", Color(0.75, 0.6, 0.45)
    else:
        name, col = f"smd_{i}", Color(0.9, 0.9, 0.9)
    a.add(s2, name=name, color=col)
    print(name, [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])

x, y, z = ic_c
pin = cq.Workplane().circle(0.18).extrude(z + 3.0).translate((0, 0, -0.5))
cross = (cq.Workplane().rect(4.0, 0.25).extrude(0.08).union(cq.Workplane().rect(0.25, 4.0).extrude(0.08))).translate((0, 0, z))
ring = cq.Workplane().circle(1.0).circle(0.8).extrude(0.08).translate((0, 0, z))
ball = cq.Workplane().sphere(0.45).translate((0, 0, z + 3.0))
a.add(pin.union(cross).union(ring).union(ball), name="IC_CENTRE_MARKER", loc=L(V(x, y, 0)), color=MAG)
a.save(out_step, "STEP")
print("IC centre", round(x, 2), round(y, 2), round(z, 2))

rows = list(csv.DictReader(open(csv_path)))
for r in rows:
    if r["module"] == "BMP280":
        r.update(board="Generic GY-BMP280 6-pin (GrabCAD bmp280-module-1, downloaded by Padam)", pcb_L_mm=15.0, pcb_W_mm=11.0,
                 ic_centre_x_mm=round(x, 2), ic_centre_y_mm=round(y, 2), ic_top_z_mm=round(z, 2),
                 ic_offset_from_pcb_centre_x=round(x - 7.5, 2), ic_offset_from_pcb_centre_y=round(y - 5.5, 2),
                 ic_model_source="GrabCAD community model (Inventor), BMP280 body 2.0x2.5x0.97",
                 position_confidence="from full board model; matches real-board photo in the download - caliper-check once")
w = csv.DictWriter(open(csv_path, "w", newline=""), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# preview
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from matplotlib.collections import PolyCollection
parts=[]
for name, ch in a.traverse():
    if ch.obj is None: continue
    shp = cq.Compound.makeCompound(ch.obj.vals()) if hasattr(ch.obj, "vals") else ch.obj
    shp = shp.moved(ch.loc); vs, tr = shp.tessellate(0.05)
    if not tr: continue
    v = np.array([[q.x, q.y, q.z] for q in vs]); parts.append((v[:, 2].max() + (100 if "MARKER" in name else 0), v, np.array(tr), ch.color.toTuple()[:3]))
parts.sort(key=lambda p: p[0]); fig, ax = plt.subplots(figsize=(6, 5))
for _, v, t, c in parts: ax.add_collection(PolyCollection(v[t][:, :, :2], facecolor=c, edgecolor=c, linewidth=0.2))
ax.set_xlim(-1, 16); ax.set_ylim(-1, 12); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_title("BMP280 GY-BMP280 (GrabCAD) top view, origin = PCB corner"); fig.savefig(sys.argv[4], dpi=120, bbox_inches="tight")
