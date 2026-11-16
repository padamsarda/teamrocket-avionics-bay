"""Tessellate each board STEP (local frame) into compact colour-grouped meshes for the web viewer."""
import sys, json, base64, numpy as np, cadquery as cq
OUTJS = sys.argv[1]
BOARDS = {
    "BMI270":  ("out/BMI270_7Semi-EVE-Breakout_marked.step", 0.03),
    "LSM6DSO": ("out/LSM6DSO_SmartElex-6DoF_marked.step", 0.03),
    "BMP280":  ("out/BMP280_GY-BMP280-GrabCAD_marked.step", 0.03),
    "MS5611":  ("out/MS5611_GY-63-GrabCAD_marked.step", 0.04),
    "ESP32":   ("out/ESP32-DevKitC-V4-GrabCAD_marked.step", 0.12),
    "SDCARD":  ("out/SD_Waveshare_MicroSD_Board.step", 0.03),
}
DEFAULT = {"NAUO2": (0.12, 0.12, 0.12), "NAUO3": (0.85, 0.85, 0.88), "NAUO15": (0.1, 0.1, 0.1), "NAUO16": (0.1, 0.1, 0.1)}
out = {}
for key, (f, tol) in BOARDS.items():
    asm = cq.Assembly.importStep(f)
    groups = {}
    def walk(a, loc, pc):
        for ch in a.children:
            if "MARKER" in ch.name: continue
            l2 = loc * ch.loc
            cc = ch.color.toTuple()[:3] if ch.color else DEFAULT.get(ch.name, pc)
            if ch.obj is not None:
                shp = ch.obj if isinstance(ch.obj, cq.Shape) else cq.Compound.makeCompound(ch.obj.vals())
                vs, tr = shp.moved(l2).tessellate(tol, 0.4)
                if tr:
                    c = tuple(round(x, 3) for x in (cc or (0.55, 0.55, 0.58)))
                    g = groups.setdefault(c, [[], []])
                    base = sum(len(p) for p in g[0])
                    g[0].append(np.array([[q.x, q.y, q.z] for q in vs], np.float32))
                    g[1].append(np.array(tr, np.uint32) + base)
            walk(ch, l2, cc)
    walk(asm, cq.Location(), None)
    parts, allv = [], []
    for c, (P, I) in groups.items():
        P = np.vstack(P); I = np.vstack(I).ravel(); allv.append(P)
        q = np.round(P * 200).astype(np.int16)          # 5 um quantisation
        parts.append(dict(c=c, p=base64.b64encode(q.tobytes()).decode(), i=base64.b64encode(I.astype(np.uint32).tobytes()).decode()))
    V = np.vstack(allv)
    out[key] = dict(parts=parts, bmin=V.min(0).round(3).tolist(), bmax=V.max(0).round(3).tolist())
    print(key, len(parts), "verts", len(V), "tris", sum(len(base64.b64decode(p["i"])) // 12 for p in parts), "bbox", out[key]["bmin"], out[key]["bmax"])
s = "window.BOARD_MESH=" + json.dumps(out, separators=(",", ":")) + ";"
open(OUTJS, "w").write(s); print("bytes", len(s))
