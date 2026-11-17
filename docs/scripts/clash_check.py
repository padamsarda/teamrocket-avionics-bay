"""Interference check: printed parts vs every other solid in a mount assembly (volume of overlap)."""
import sys, cadquery as cq
a = cq.Assembly.importStep(sys.argv[1]); items = []
def walk(n, loc, top):
    for ch in n.children:
        l2 = loc * ch.loc
        if ch.obj is not None:
            shp = ch.obj if isinstance(ch.obj, cq.Shape) else cq.Compound.makeCompound(ch.obj.vals())
            items.append((top or ch.name, shp.moved(l2)))
        walk(ch, l2, top or ch.name)
walk(a, cq.Location(), None)
printed = [(n, s) for n, s in items if n.startswith(("S1_", "S2_"))]
others = [(n, s) for n, s in items if not n.startswith(("S1_", "S2_", "M4_", "M3_grommet", "grommet"))]
bad = 0
for pn, ps in printed:
    pb = ps.BoundingBox()
    for on, os_ in others:
        ob = os_.BoundingBox()
        if ob.xmax < pb.xmin or ob.xmin > pb.xmax or ob.ymax < pb.ymin or ob.ymin > pb.ymax or ob.zmax < pb.zmin or ob.zmin > pb.zmax: continue
        try: v = ps.intersect(os_).Volume()
        except Exception as e: v = -1
        if abs(v) > 0.05: print(f"CLASH {pn} x {on}: {v:.2f} mm3"); bad += 1
print("clashes:", bad, "| printed parts:", [n for n, _ in printed])
