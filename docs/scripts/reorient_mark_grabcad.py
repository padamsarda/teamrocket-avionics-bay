"""Re-orient downloaded GrabCAD STEP assemblies into the bay frame (origin = PCB bottom-left corner,
Z up = component side, PCB bottom at z=0) and add the magenta IC_CENTRE_MARKER. Keeps original names/colours.
usage: reorient_mark.py <job> <src.step> <out.step> <preview.png>"""
import sys, cadquery as cq
from cadquery import Color, Location as L, Vector as V
from OCP.gp import gp_Trsf, gp_Ax3, gp_Pnt, gp_Dir

JOBS = {
    # origin (old coords), new Z dir, new X dir, IC centre in NEW frame (x, y, top z), board L x W for preview
    "gy63": dict(o=(-5.13, 4.44, 18.69), n=(0, 1, 0), vx=(1, 0, 0), ic=(10.16, 9.75, 2.25), lim=(-1, 14, -1, 20)),
    "devkitc": dict(o=(-14.05, 0.0, 24.13), n=(0, 1, 0), vx=(1, 0, 0), ic=(12.55, 38.75, 4.80), lim=(-1, 29.5, -1, 55.5)),
}
job, src, out, png = sys.argv[1:5]
J = JOBS[job]
t = gp_Trsf(); t.SetTransformation(gp_Ax3(gp_Pnt(*J["o"]), gp_Dir(*J["n"]), gp_Dir(*J["vx"])))
src_asm = cq.Assembly.importStep(src)
top = cq.Assembly(name=f"{job}_bayframe")
top.add(src_asm, name="vendor_model", loc=cq.Location(t))
x, y, z = J["ic"]
pin = cq.Workplane().circle(0.18).extrude(z + 3.0).translate((0, 0, -0.5))
cross = (cq.Workplane().rect(4.0, 0.25).extrude(0.08).union(cq.Workplane().rect(0.25, 4.0).extrude(0.08))).translate((0, 0, z))
ring = cq.Workplane().circle(1.0).circle(0.8).extrude(0.08).translate((0, 0, z))
ball = cq.Workplane().sphere(0.45).translate((0, 0, z + 3.0))
top.add(pin.union(cross).union(ring).union(ball), name="IC_CENTRE_MARKER", loc=L(V(x, y, 0)), color=Color(1, 0, 1))
top.save(out, "STEP")

# z-sorted top-view preview
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
from matplotlib.collections import PolyCollection
parts = []
def walk(a, loc):
    for ch in a.children:
        l2 = loc * ch.loc
        if ch.obj is not None:
            shp = ch.obj if isinstance(ch.obj, cq.Shape) else cq.Compound.makeCompound(ch.obj.vals())
            shp = shp.moved(l2); vs, tr = shp.tessellate(0.1, 0.5)
            if tr:
                v = np.array([[q.x, q.y, q.z] for q in vs])
                c = ch.color.toTuple()[:3] if ch.color else (0.5, 0.5, 0.5)
                parts.append((v[:, 2].max() + (100 if "MARKER" in ch.name else 0), v, np.array(tr), c))
        walk(ch, l2)
walk(top, cq.Location())
parts.sort(key=lambda p: p[0]); fig, ax = plt.subplots(figsize=(6, 6))
for _, v, tr, c in parts: ax.add_collection(PolyCollection(v[tr][:, :, :2], facecolor=c, edgecolor=c, linewidth=0.1))
a0, a1, b0, b1 = J["lim"]; ax.set_xlim(a0, a1); ax.set_ylim(b0, b1); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_title(f"{job} top view, origin = PCB corner; IC centre ({x}, {y})"); fig.savefig(png, dpi=120, bbox_inches="tight")
V_all = np.vstack([p[1] for p in parts if p[0] < 100]); print("extent", V_all.min(0).round(2), V_all.max(0).round(2))
