"""Build avionics-bay module CAD with magenta IC-centre markers.
Frame per board: origin = PCB bottom-left corner, X = board length, Y = board width,
Z up, PCB top at z = T. All mm."""
import cadquery as cq, csv, os, sys
from cadquery import Color, Location as L, Vector as V

DL = sys.argv[1]; OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
K3D = f"{DL}/k3d"
T = 1.6
MAG = Color(1, 0, 1)            # marker colour
GOLD = Color(0.85, 0.68, 0.2)
rows = []

def imp(p): return cq.importers.importStep(p)

def marker(a, x, y, ztop, name="IC_CENTRE_MARKER"):
    """Magenta pin through the IC centre + crosshair + ring on top of the IC."""
    pin = cq.Workplane().circle(0.18).extrude(ztop + 3.0).translate((0, 0, -0.5))
    cross = (cq.Workplane().rect(4.0, 0.25).extrude(0.08)
             .union(cq.Workplane().rect(0.25, 4.0).extrude(0.08))).translate((0, 0, ztop))
    ring = cq.Workplane().circle(1.0).circle(0.8).extrude(0.08).translate((0, 0, ztop))
    ball = cq.Workplane().sphere(0.45).translate((0, 0, ztop + 3.0))
    m = pin.union(cross).union(ring).union(ball)
    a.add(m, name=name, loc=L(V(x, y, 0)), color=MAG)

def pcb(lx, ly, holes=(), r=0.5):
    w = cq.Workplane().box(lx, ly, T, centered=False).edges("|Z").fillet(r)
    for (hx, hy, d) in holes:
        w = w.cut(cq.Workplane().circle(d / 2).extrude(T).translate((hx, hy, 0)))
    return w

def header(a, x0, y, n, pitch=2.54, axis="y", name="header"):
    """Straight male header soldered on the BOTTOM (breadboard style)."""
    for i in range(n):
        x, yy = (x0, y + i * pitch) if axis == "y" else (x0 + i * pitch, y)
        a.add(cq.Workplane().rect(0.64, 0.64).extrude(11.0).translate((x, yy, -8.5)),
              name=f"{name}_pin{i+1}", color=GOLD)
    if axis == "y":
        body = cq.Workplane().box(2.54, n * pitch, 2.5, centered=(True, False, False)).translate((x0, y - pitch / 2, -2.5))
    else:
        body = cq.Workplane().box(n * pitch, 2.54, 2.5, centered=(False, True, False)).translate((x0 - pitch / 2, y, -2.5))
    a.add(body, name=f"{name}_body", color=Color(0.1, 0.1, 0.1))

def record(name, board, lx, ly, icx, icy, icz, src, conf):
    rows.append(dict(module=name, board=board, pcb_L_mm=lx, pcb_W_mm=ly,
                     ic_centre_x_mm=round(icx, 2), ic_centre_y_mm=round(icy, 2), ic_top_z_mm=round(icz, 2),
                     ic_offset_from_pcb_centre_x=round(icx - lx / 2, 2) if lx else "",
                     ic_offset_from_pcb_centre_y=round(icy - ly / 2, 2) if ly else "",
                     ic_model_source=src, position_confidence=conf))

ASM=[]
def save(a, fn):
    a.save(f"{OUT}/{fn}.step", "STEP"); ASM.append((fn,a))

# ---------------- 1. BMI270 : 7Semi/EVE BMI270 Breakout ES-12135 (30x25, Qwiic x2, SPI pins) ----------------
# Positions measured by pixel analysis of the vendor's own dimensioned top-view CAD render
# (evelta.com eve-bmi270-dimetions.png, 21.7 px/mm). IC body measured 2.49 x 3.03 mm -> matches datasheet.
lx, ly = 30.0, 25.0
icx, icy = 16.27, ly - 10.75
hi = 2.45; HD = 3.0                      # hole inset from edges, hole dia (measure: M2.5 or M3)
a = cq.Assembly(name="BMI270_7Semi_EVE_Breakout_ES-12135")
a.add(pcb(lx, ly, [(hi, hi, HD), (lx - hi, hi, HD), (hi, ly - hi, HD), (lx - hi, ly - hi, HD)], r=2.5),
      name="PCB", color=Color(0.1, 0.45, 0.1))
ic = imp(f"{K3D}/Package_LGA.3dshapes/Bosch_LGA-14_3x2.5mm_P0.5mm.step")
a.add(ic, name="BMI270_LGA14", loc=L(V(icx, icy, T), V(0, 0, 1), 90), color=Color(0.15, 0.15, 0.15))
qy = ly - 11.45
for side, x0 in (("L", -0.4), ("R", lx - 4.85)):
    a.add(cq.Workplane().box(5.25, 6.0, 2.95, centered=(False, True, False)), name=f"Qwiic_{side}_JST-SH_4p",
          loc=L(V(x0, qy, T)), color=Color(0.1, 0.1, 0.7))
# NOT FITTED: top row is half a pitch off the bottom row, so it cannot also go into a 2.54 perfboard
# header(a, 15.0 - 2.5 * 2.54, ly - 3.0, 6, axis="x", name="J_top_OSDO-OSDB-INT1-INT2-ASCX-ASDX")
header(a, 15.0 - 3 * 2.54, 2.5, 7, axis="x", name="J_bot_VIN-3V3-GND-SCK-ADD-SDA-CS")
marker(a, icx, icy, T + 0.78)
save(a, "BMI270_7Semi-EVE-Breakout_marked")
record("BMI270", "7Semi/EVE BMI270 Breakout ES-12135 30x25 (Evelta link)", lx, ly, icx, icy, T + 0.78,
       "KiCad Bosch_LGA-14_3x2.5mm (datasheet-accurate package)",
       "board/IC/holes/pins measured from vendor dimensioned CAD render, est. +/-0.15 mm; hole dia unverified")

# ---------------- 2. LSM6DSO : IC only, board not chosen ----------------
a = cq.Assembly(name="LSM6DSO_IC_only")
ic = imp(f"{K3D}/Package_LGA.3dshapes/LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step")
a.add(ic, name="LSM6DSO_LGA14", color=Color(0.15, 0.15, 0.15))
marker(a, 0, 0, 0.86)
save(a, "LSM6DSO_IC-only_marked")
record("LSM6DSO", "BOARD NOT IDENTIFIED - IC only, origin = IC centre", "", "", 0, 0, 0.86,
       "KiCad LGA-14_3x2.5mm (ST LGA-14L 2.5x3x0.86)", "IC exact; board TBD")

# ---------------- 3. BMP280 : generic GY-BMP280-3.3 (6-pin, purple) ----------------
lx, ly = 15.0, 11.5
holes = [(2.5, 9.0, 3.0), (12.5, 9.0, 3.0)]
icx, icy = 6.6, 6.8
a = cq.Assembly(name="BMP280_GY-BMP280")
a.add(pcb(lx, ly, holes), name="PCB", color=Color(0.45, 0.1, 0.45))
ic = imp(f"{K3D}/Package_LGA.3dshapes/Bosch_LGA-8_2x2.5mm_P0.65mm_ClockwisePinNumbering.step")
a.add(ic, name="BMP280_LGA8", loc=L(V(icx, icy, T)), color=Color(0.75, 0.75, 0.75))
header(a, 1.15 + 0.0, 1.27, 6, axis="x", name="J1_VCC-GND-SCL-SDA-CSB-SDO")
marker(a, icx, icy, T + 0.78)
save(a, "BMP280_GY-BMP280_marked")
record("BMP280", "Generic GY-BMP280-3.3 6-pin (Robocraze listing)", lx, ly, icx, icy, T + 0.78,
       "KiCad Bosch_LGA-8_2x2.5mm (datasheet-accurate package)",
       "PCB/holes = typical listing dims; IC position from angled photos, est. +/-1 mm - VERIFY")

# ---------------- 4. MS5611 : GY-63 ----------------
lx, ly = 14.0, 18.0                 # X across (header side at x=0), Y along header
icx, icy = 10.8, ly - 7.9
a = cq.Assembly(name="MS5611_GY-63")
a.add(pcb(lx, ly, [(11.1, ly - 15.4, 2.6)]), name="PCB", color=Color(0.05, 0.25, 0.75))
base = cq.Workplane().box(3.0, 5.0, 0.45)              # MS5611-01BA03 5.0x3.0x1.0
lid = cq.Workplane().box(2.7, 4.6, 0.55).edges("|Z").fillet(0.3).translate((0, 0, 0.5))
a.add(base, name="MS5611_ceramic", loc=L(V(icx, icy, T + 0.225)), color=Color(0.9, 0.9, 0.85))
a.add(lid, name="MS5611_metal_cap", loc=L(V(icx, icy, T + 0.225)), color=Color(0.78, 0.78, 0.8))
header(a, 1.36, ly - 1.0 - 6 * 2.54, 7, axis="y", name="J1_VCC-GND-SCL-SDA-CSB-SDO-PS")
marker(a, icx, icy, T + 1.0)
save(a, "MS5611_GY-63_marked")
record("MS5611", "Generic GY-63 (7-pin)", lx, ly, icx, icy, T + 1.0,
       "Own model from MS5611-01BA03 datasheet outline 5.0x3.0x1.0",
       "PCB = listing spec 18x14; IC/hole/pins from ProtoSupplies top photo, est. +/-0.5 mm")

# ---------------- 5. ESP32-WROOM-32E (Espressif official STEP) ----------------
a = cq.Assembly(name="ESP32-WROOM-32E")
a.add(imp(f"{DL}/esp/3dmodels/espressif.3dshapes/ESP32-WROOM-32E.STEP"), name="ESP32-WROOM-32E_Espressif",
      color=Color(0.7, 0.7, 0.72))
icx, icy = (4.98 + 10.02) / 2, (7.77 + 12.81) / 2       # ESP32-D0WD die package inside the can
marker(a, icx, icy, 3.2)
save(a, "ESP32-WROOM-32E_marked")
record("ESP32-WROOM-32E", "Bare module 18x25.5 (Espressif official STEP)", 18.0, 25.5, icx, icy, 3.2,
       "Espressif kicad-libraries ESP32-WROOM-32E.STEP (internal ESP32 QFN located)", "exact (from vendor model)")

# ---------------- 6. 2S 600 mAh LiPo : PLACEHOLDER ----------------
blx, bly, blz = 58.0, 30.0, 15.0
a = cq.Assembly(name="LiPo_2S_600mAh_PLACEHOLDER")
a.add(cq.Workplane().box(blx, bly, blz, centered=False).edges().fillet(1.5), name="cell_pack", color=Color(0.1, 0.4, 0.9))
a.add(cq.Workplane().box(10.2, 8.0, 5.0, centered=False), name="XT30_plug",
      loc=L(V(blx + 40, bly / 2 - 4, blz / 2 - 2.5)), color=Color(0.95, 0.85, 0.1))
save(a, "LiPo_2S_600mAh_PLACEHOLDER")

with open(f"{OUT}/IC_centres.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("ok", len(rows))

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np
os.makedirs(f"{OUT}/previews", exist_ok=True)
for fn,a in ASM:
    tol = 0.3 if fn.startswith("ESP32") else 0.05
    parts=[]
    for name,child in a.traverse():
        if child.obj is None: continue
        shp = cq.Compound.makeCompound(child.obj.vals()) if hasattr(child.obj,"vals") else child.obj
        loc=child.loc; par=child.parent
        while par is not None: loc=par.loc*loc; par=par.parent
        shp=shp.moved(loc)
        vs,tris=shp.tessellate(tol)
        if not tris: continue
        v=np.array([[q.x,q.y,q.z] for q in vs]); t=np.array(tris)
        c=child.color.toTuple()[:3] if child.color else (0.6,0.6,0.6)
        ismark = "MARKER" in name
        parts.append((v[:,2].max()+ (100 if ismark else 0), v, t, c, name))
    parts.sort(key=lambda p:p[0])
    fig,ax=plt.subplots(figsize=(6,6))
    for _,v,t,c,name in parts:
        ax.add_collection(PolyCollection(v[t][:,:,:2], facecolor=c, edgecolor=c, linewidth=0.2))
    V=np.vstack([p[1] for p in parts]); ax.set_xlim(V[:,0].min()-1,V[:,0].max()+1); ax.set_ylim(V[:,1].min()-1,V[:,1].max()+1)
    ax.set_aspect("equal"); ax.grid(alpha=.3); ax.set_title(fn+"  (top view, origin = PCB corner)"); ax.set_xlabel("X mm"); ax.set_ylabel("Y mm")
    fig.savefig(f"{OUT}/previews/{fn}.png",dpi=120,bbox_inches="tight"); plt.close(fig)
print("rendered")
