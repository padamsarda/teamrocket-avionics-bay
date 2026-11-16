"""Add the real KiCad TO-220-3 Vertical model to the viewer meshes, split into body / tab / leads by geometry."""
import sys, json, base64, numpy as np, cadquery as cq
js, step = sys.argv[1], sys.argv[2]
s = open(js).read(); data = json.loads(s[len("window.BOARD_MESH="):-1])
shp = cq.importers.importStep(step).val()
vs, tr = shp.tessellate(0.02, 0.3)
V = np.array([[q.x, q.y, q.z] for q in vs], np.float32); T = np.array(tr, np.int64)
c = V[T].mean(1)
groups = {(0.72, 0.72, 0.74): (c[:, 2] < 0.2) | (c[:, 1] > 1.85),   # leads + metal tab
          (0.08, 0.08, 0.09): ~((c[:, 2] < 0.2) | (c[:, 1] > 1.85))}  # epoxy body
parts = []
for col, m in groups.items():
    tri = T[m]; idx, inv = np.unique(tri.ravel(), return_inverse=True)
    P = V[idx]; I = inv.reshape(-1, 3).astype(np.uint32)
    parts.append(dict(c=col, p=base64.b64encode(np.round(P * 200).astype(np.int16).tobytes()).decode(),
                      i=base64.b64encode(I.tobytes()).decode()))
data["TO220"] = dict(parts=parts, bmin=V.min(0).round(3).tolist(), bmax=V.max(0).round(3).tolist())
open(js, "w").write("window.BOARD_MESH=" + json.dumps(data, separators=(",", ":")) + ";")
print("TO220", data["TO220"]["bmin"], data["TO220"]["bmax"])
