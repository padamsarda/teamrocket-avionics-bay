import sys, numpy as np, cadquery as cq, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
src, png, title = sys.argv[1:4]
a = cq.Assembly.importStep(src); parts = []; SEC = []
SLAB = cq.Solid.makeBox(200, 2.0, 200, pnt=cq.Vector(-100, 99.0, -100))
def walk(n, loc, pc):
    for ch in n.children:
        l2 = loc * ch.loc; cc = ch.color.toTuple()[:3] if ch.color else pc
        if ch.obj is not None:
            shp = ch.obj if isinstance(ch.obj, cq.Shape) else cq.Compound.makeCompound(ch.obj.vals())
            vs, tr = shp.moved(l2).tessellate(0.3, 0.6)
            if tr: parts.append((np.array([[q.x, q.y, q.z] for q in vs]), np.array(tr), cc or (0.5, 0.5, 0.5)))
            try:
                sh = shp.moved(l2)
                if sh.BoundingBox().ymin < 101 and sh.BoundingBox().ymax > 99:
                    cut = sh.intersect(SLAB); vs2, tr2 = cut.tessellate(0.2, 0.5)
                    if tr2: SEC.append((np.array([[q.x, q.y, q.z] for q in vs2]), np.array(tr2), cc or (0.5, 0.5, 0.5)))
            except Exception: pass
        walk(ch, l2, cc)
walk(a, cq.Location(), None)
fig, axs = plt.subplots(1, 3, figsize=(16, 10), gridspec_kw=dict(width_ratios=[1, 1, 1.25]))
TRI = np.vstack([p[0][p[1]] for p in parts]); COL = np.vstack([np.tile(p[2], (len(p[1]), 1)) for p in parts])
STRI = np.vstack([p[0][p[1]] for p in SEC]); SCOL = np.vstack([np.tile(p[2], (len(p[1]), 1)) for p in SEC])
for ax, (i, j, k), t, tri, col in ((axs[0], (0, 1, 2), "Front (sensor face)", TRI, COL), (axs[1], (2, 1, 0), "Side (from +X)", TRI, COL),
                               (axs[2], (0, 2, 1), "Cross-section at Y = 100 mm (seen from nose)", STRI, SCOL)):
    o = np.argsort(tri[:, :, k].mean(1))                        # painter's sort per triangle
    ax.add_collection(PolyCollection(tri[o][:, :, [i, j]], facecolor=col[o], edgecolor=col[o], linewidth=0.05))
    V = TRI.reshape(-1, 3); ax.set_xlim(V[:, i].min() - 3, V[:, i].max() + 3); ax.set_ylim(V[:, j].min() - 3, V[:, j].max() + 3)
    ax.set_aspect("equal"); ax.set_title(t); ax.grid(alpha=.25)
th = np.linspace(0, 2 * np.pi, 200); axs[2].plot(32 * np.cos(th), 32 * np.sin(th), "k--", lw=1, label="tube ID 64"); axs[2].legend(loc="lower right")
axs[2].set_xlim(-36, 36); axs[2].set_ylim(-36, 36)
fig.suptitle(title); fig.savefig(png, dpi=110, bbox_inches="tight")
