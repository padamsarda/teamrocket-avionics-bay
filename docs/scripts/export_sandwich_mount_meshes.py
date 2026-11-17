"""Add the sandwich bay-mount parts (printed parts, rods/nuts, grommets + screws) to the viewer meshes (viewer world frame)."""
import sys, json, base64, numpy as np, cadquery as cq
js = sys.argv[1]; s = open(js).read(); data = json.loads(s[len("window.BOARD_MESH="):-1])
KEEP = ("S1_", "S2_", "M4_", "grommet", "M3_grommet")
for key, f in (("MOUNT_S1", "mounts_s/Sandwich_V1_slide_rails/Sandwich_V1_slide_rails_ASSEMBLY.step"),
               ("MOUNT_S2", "mounts_s/Sandwich_V2_backplate_frame/Sandwich_V2_backplate_frame_ASSEMBLY.step")):
    a = cq.Assembly.importStep(f); groups = {}
    for ch in a.children:
        if not ch.name.startswith(KEEP) or ch.obj is None: continue
        shp = ch.obj if isinstance(ch.obj, cq.Shape) else cq.Compound.makeCompound(ch.obj.vals())
        vs, tr = shp.moved(ch.loc).tessellate(0.08, 0.3)
        c = tuple(round(x, 3) for x in (ch.color.toTuple()[:3] if ch.color else (0.3, 0.45, 0.62)))
        g = groups.setdefault(c, [[], [], 0]); g[0].append(np.array([[q.x, q.y, q.z] for q in vs], np.float32)); g[1].append(np.array(tr, np.uint32) + g[2]); g[2] += len(vs)
    parts = [dict(c=c, p=base64.b64encode(np.round(np.vstack(P) * 50).astype(np.int16).tobytes()).decode(),
                  i=base64.b64encode(np.vstack(I).astype(np.uint32).tobytes()).decode()) for c, (P, I, _) in groups.items()]
    data[key] = dict(parts=parts, bmin=[0, 0, 0], bmax=[0, 0, 0], q=50); print(key, len(parts), sum(len(np.vstack(P)) for P, _, _ in groups.values()))
open(js, "w").write("window.BOARD_MESH=" + json.dumps(data, separators=(",", ":")) + ";"); print("bytes", len(open(js).read()))
