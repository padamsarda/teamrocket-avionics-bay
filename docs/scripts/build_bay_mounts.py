"""Removable avionics-bay mounts for the sensor perfboard — two versions.
Frame (same as the 3D viewer): X = across the perfboard (U), Y = rocket axis (nose up), Z = plate normal (sensors face +Z).
Perfboard sensor face at Z = -4.49, thickness 2.4 (back face Z = -6.89). Tube ID 64, platforms Ø63.4.
V1  'slide-in' : bottom platform + 2 full-length grooved side rails (one print) + top cap with board pocket; perfboard slides down the rails.
V2  'backplate': bottom platform + backplate spine (one print) + top cap; perfboard bolts to the spine through 4 corner holes with rubber grommets.
Both: 2× M4 threaded rods + nuts clamp the stack; wire pass-throughs; 3 switch holes in the top platform."""
import sys, json, math, cadquery as cq
from cadquery import Color, Location as L, Vector as V
from OCP.gp import gp_Trsf
S, OUT = sys.argv[1], sys.argv[2]
D = json.load(open(f"{S}/layout_dump.json"))
P, FACE, PT = 2.54, -4.49, 2.4
BACK = FACE - PT                                     # -6.89
R_PLAT, T_PLAT, POCKET = 63.4 / 2, 5.0, 3.0
STEP = {"BMI270": "out/BMI270_7Semi-EVE-Breakout_marked.step", "LSM6DSO": "out/LSM6DSO_SmartElex-6DoF_marked.step",
        "BMP280": "out/BMP280_GY-BMP280-GrabCAD_marked.step", "MS5611": "out/MS5611_GY-63-GrabCAD_marked.step",
        "ESP32": "out/ESP32-DevKitC-V4-GrabCAD_marked.step", "SDCARD": "out/SD_Waveshare_MicroSD_Board.step",
        "TO220": "dl/k3d/Package_TO_SOT_THT.3dshapes/TO-220-3_Vertical.step"}
C_PRINT, C_FR4, C_RUB, C_STEEL = Color(0.30, 0.45, 0.62), Color(0.72, 0.55, 0.30), Color(0.05, 0.05, 0.05), Color(0.75, 0.75, 0.78)
def step_asm(t):                                     # fresh import per instance (an assembly object can't be reused twice)
    try: return cq.Assembly.importStep(f"{S}/{STEP[t]}")
    except ValueError:                               # plain single-part STEP (KiCad TO-220)
        return cq.Assembly(name=t).add(cq.importers.importStep(f"{S}/{STEP[t]}"), name=t + "_body", color=Color(0.1, 0.1, 0.1))

def mat_loc(m, dy=0.0):
    t = gp_Trsf(); t.SetValues(m[0], m[4], m[8], m[12], m[1], m[5], m[9], m[13] + dy, m[2], m[6], m[10], m[14]); return cq.Location(t)

def prim(b):
    bx = b["box"]
    if b["cyl"]:  return cq.Workplane("XZ").circle(bx[0] / 2).extrude(-bx[1]).translate((bx[0] / 2, 0, bx[2] / 2))
    if b["cylZ"]: return cq.Workplane("XY").circle(bx[0] / 2).extrude(bx[2]).translate((bx[0] / 2, bx[1] / 2, 0))
    return cq.Workplane().box(*bx, centered=False)

def electronics(asm, version, dy_batt, dy_charge):
    for b in D["boards"]:
        if version == 2 and b["id"] == "BUZZER": continue            # moved to the front in V2 (added separately)
        dy = dy_batt if b["type"] == "BATT" else dy_charge if b["type"] == "PYRO" else 0.0
        if b["type"] in STEP: asm.add(step_asm(b["type"]), name=b["id"], loc=mat_loc(b["m"], dy))
        else:
            col = {"BATT": Color(0.17, 0.48, 0.85), "PYRO": Color(0.70, 0.15, 0.12), "BUZZ": Color(0.07, 0.07, 0.07)}[b["type"]]
            asm.add(prim(b), name=b["id"], loc=mat_loc(b["m"], dy), color=col)

def perfboard(u_half, v0, v1, corner_holes=None):
    pb = cq.Workplane("XY").box(2 * u_half, v1 - v0, PT, centered=(True, False, False)).translate((0, v0, BACK))
    pts = [(-P / 2 + k * P, j * P) for k in range(-20, 21) for j in range(-5, 120)
           if abs(-P / 2 + k * P) < u_half - 1.0 and v0 + 1.0 < j * P < v1 - 1.0]
    if corner_holes: pts = [p for p in pts if all(math.hypot(p[0] - cx, p[1] - cy) > 4.2 for cx, cy in corner_holes)]
    pb = pb.faces(">Z").workplane(centerOption="ProjectedOrigin", origin=(0, 0, 0)).pushPoints(pts).hole(1.0)
    if corner_holes: pb = pb.faces(">Z").workplane(centerOption="ProjectedOrigin", origin=(0, 0, 0)).pushPoints(corner_holes).hole(6.5)
    return pb

def platform(y0, rods, wires, switches=()):
    p = cq.Workplane("XZ").circle(R_PLAT).extrude(-T_PLAT).translate((0, y0, 0))
    for (x, z, d) in [(x, z, 4.4) for x, z in rods] + [(x, z, 6.0) for x, z in wires] + [(x, z, 6.5) for x, z in switches]:
        p = p.cut(cq.Workplane("XZ").circle(d / 2).extrude(-T_PLAT).translate((x, y0, z)))
    return p

def rods_and_nuts(asm, rods, y0, y1):
    for i, (x, z) in enumerate(rods):
        asm.add(cq.Workplane("XZ").circle(2.0).extrude(-(y1 - y0 + 24)).translate((x, y0 - 12, z)), name=f"M4_rod_{i+1}", color=C_STEEL)
        for k, y in enumerate((y0 - 3.2, y1)):
            asm.add(cq.Workplane("XZ").polygon(6, 7.7).circle(2.0).extrude(-3.2).translate((x, y, z)), name=f"M4_nut_{i+1}_{k+1}", color=C_STEEL)

def save(asm, parts, folder):
    import os; os.makedirs(f"{OUT}/{folder}", exist_ok=True)
    for name, wp in parts.items():
        cq.Assembly(name=name + "_part").add(wp, name=name, color=C_PRINT).save(f"{OUT}/{folder}/{name}.step", "STEP")
        cq.exporters.export(wp, f"{OUT}/{folder}/{name}.stl", tolerance=0.05, angularTolerance=0.2)
    asm.save(f"{OUT}/{folder}/{folder}_ASSEMBLY.step", "STEP")

on = [b for b in D["boards"] if b["face"] != "off"]
U_HALF = 22.86                                      # perfboard cut between hole columns: 45.72 mm wide (18 holes)
batt = next(b for b in D["boards"] if b["type"] == "BATT"); charges = [b for b in D["boards"] if b["type"] == "PYRO"]
report = {}

# ============================ V1 : slide-in rails ============================
pv0 = -3.81; pv1 = 219.71                           # perfboard enlarged ~6 mm past the parts at both ends, cut on hole-grid lines
yb0, yt1 = pv0 - (T_PLAT - POCKET), pv1 + (T_PLAT - POCKET)
rods1 = [(-19.0, -18.0), (19.0, -18.0)]
gw, gt = 0.30, 0.15                                 # groove clearance across / through thickness
rail_in, rail_out, rail_z0, rail_z1 = U_HALF - 3.0, U_HALF + 4.0, BACK - 3.0, FACE + 3.0
lower = platform(yb0, rods1, wires=[(-6.35, 4.0), (6.35, 4.0)])
lower = lower.cut(cq.Workplane("XY").box(2 * (U_HALF + gw), POCKET, PT + 2 * gt, centered=(True, False, False)).translate((0, pv0, BACK - gt)))
for s in (-1, 1):
    x0, x1 = (rail_in, rail_out) if s > 0 else (-rail_out, -rail_in)
    rail = cq.Workplane("XY").box(x1 - x0, pv1 - pv0, rail_z1 - rail_z0, centered=False).translate((x0, pv0, rail_z0))
    gx0, gx1 = (rail_in - 0.01, U_HALF + gw) if s > 0 else (-(U_HALF + gw), -(rail_in - 0.01))
    groove = cq.Workplane("XY").box(gx1 - gx0, pv1 - pv0 + 1, PT + 2 * gt, centered=False).translate((gx0, pv0, BACK - gt))
    lead = cq.Workplane("XY").box(gx1 - gx0 + 1.2, 4, PT + 1.6, centered=False).translate((gx0 - (0.6 if s < 0 else 0), pv1 - 4, BACK - 0.8))
    lower = lower.union(rail).cut(groove).cut(lead)
top1 = platform(pv1 - POCKET, rods1, wires=[(15.0, -12.0)], switches=[(-14, 14), (0, 18), (14, 14)])
top1 = top1.cut(cq.Workplane("XY").box(2 * (U_HALF + gw), POCKET, PT + 2 * gt, centered=(True, False, False)).translate((0, pv1 - POCKET, BACK - gt)))
for s in (-1, 1):
    x0, x1 = (rail_in - 0.3, rail_out + 0.3) if s > 0 else (-rail_out - 0.3, -rail_in + 0.3)
    top1 = top1.cut(cq.Workplane("XY").box(x1 - x0, POCKET, rail_z1 - rail_z0 + 0.6, centered=False).translate((x0, pv1 - POCKET, rail_z0 - 0.3)))
dyb1 = max(0.0, (yt1 + 4.0) - batt["v0"]); dyc1 = min(0.0, (yb0 - 6.0) - max(c["v1"] for c in charges))
a1 = cq.Assembly(name="AvBay_V1_slide_rails")
a1.add(lower, name="V1_lower_platform_with_rails", color=C_PRINT); a1.add(top1, name="V1_top_cap", color=C_PRINT)
a1.add(perfboard(U_HALF, pv0, pv1), name="perfboard_45.7x223.5", color=C_FR4)
rods_and_nuts(a1, rods1, yb0, yt1); electronics(a1, 1, dyb1, dyc1)
save(a1, {"V1_lower_platform_with_rails": lower, "V1_top_cap": top1}, "V1_slide_rails")
report["V1"] = dict(perfboard=f"{2*U_HALF:.2f} x {pv1-pv0:.2f} mm", stack=f"{yt1-yb0:.1f} mm", rods=rods1, battery_shift=dyb1, charge_shift=dyc1)

# ============================ V2 : backplate + grommets ============================
buz = next(b for b in D["boards"] if b["id"] == "BUZZER")
esp = next(b for b in D["boards"] if b["id"] == "ESP32")
bz_v0 = esp["v1"] + 2.0                              # buzzer moved to the FRONT, just past the ESP32 antenna keep-out
pv0b, pv1b = -3.81, 1.27 + math.ceil((bz_v0 + 23 + 3 - 1.27) / P) * P
ins = 3.6
holes = [(-(U_HALF - ins), pv0b + ins + 1.5), ((U_HALF - ins), pv0b + ins + 1.5), (-(U_HALF - ins), pv1b - ins), ((U_HALF - ins), pv1b - ins)]
GAP, BPT = 6.0, 3.0                                 # perfboard back -> backplate front gap (grommet + standoff), backplate thickness
bp_z1, bp_z0 = BACK - GAP, BACK - GAP - BPT
rods2 = [(-12.0, -22.0), (12.0, -22.0)]
yb0b, yt1b = pv0b - (T_PLAT - POCKET), pv1b + (T_PLAT - POCKET)
spine = platform(yb0b, rods2, wires=[(-6.35, 4.0), (6.35, 4.0)])
back = cq.Workplane("XY").box(2 * U_HALF, pv1b - pv0b, BPT, centered=(True, False, False)).translate((0, pv0b, bp_z0))
for x in (-8.0, 8.0):                                # stiffening ribs on the back of the spine
    back = back.union(cq.Workplane("XY").box(2.0, pv1b - pv0b, 3.0, centered=(True, False, False)).translate((x, pv0b, bp_z0 - 3.0)))
sd = next(b for b in D["boards"] if b["id"] == "SD")
back = back.cut(cq.Workplane("XY").box(sd["u1"] - sd["u0"] + 4, sd["v1"] - sd["v0"] + 4, 20, centered=False)
                .translate((sd["u0"] - 2, sd["v0"] - 2, bp_z0 - 8)))               # window: SD board stays on the back
for (x, y) in holes:
    back = back.union(cq.Workplane("XZ").circle(4.0).extrude(-1).translate((0, 0, 0)).rotate((0, 0, 0), (1, 0, 0), 0) if False else
                      cq.Workplane("XY").circle(4.0).extrude(GAP - 2.0).translate((x, y, bp_z1)))   # standoff (2 mm left for grommet)
    back = back.cut(cq.Workplane("XY").circle(1.35).extrude(GAP + BPT + 4).translate((x, y, bp_z0 - 3)))  # M3 tap/self-tap hole
spine = spine.union(back)
top2 = platform(pv1b - POCKET, rods2, wires=[(0.0, -18.0)], switches=[(-14, 14), (0, 18), (14, 14)])
top2 = top2.cut(cq.Workplane("XY").box(2 * U_HALF + 0.6, POCKET, BPT + 6.6, centered=(True, False, False)).translate((0, pv1b - POCKET, bp_z0 - 3.3)))
dyb2 = max(0.0, (yt1b + 4.0) - batt["v0"]); dyc2 = min(0.0, (yb0b - 6.0) - max(c["v1"] for c in charges))
a2 = cq.Assembly(name="AvBay_V2_backplate")
a2.add(spine, name="V2_lower_platform_with_backplate", color=C_PRINT); a2.add(top2, name="V2_top_cap", color=C_PRINT)
a2.add(perfboard(U_HALF, pv0b, pv1b, holes), name=f"perfboard_45.7x{pv1b-pv0b:.1f}_4holes", color=C_FR4)
for i, (x, y) in enumerate(holes):
    g = (cq.Workplane("XY").circle(4.6).extrude(1.2).translate((0, 0, -1.2))
         .union(cq.Workplane("XY").circle(3.25).extrude(PT)).union(cq.Workplane("XY").circle(4.6).extrude(1.2).translate((0, 0, PT)))
         .cut(cq.Workplane("XY").circle(1.6).extrude(PT + 4).translate((0, 0, -2))))
    a2.add(g, name=f"grommet_{i+1}", loc=L(V(x, y, BACK)), color=C_RUB)
    a2.add(cq.Workplane("XY").circle(1.5).extrude(GAP + PT + 6).translate((x, y, bp_z1 - 2)), name=f"M3_screw_{i+1}", color=C_STEEL)
a2.add(cq.Workplane("XY").circle(11.5).extrude(15).translate((0, bz_v0 + 11.5, FACE + 2.0)), name="BUZZER_front", color=Color(0.07, 0.07, 0.07))
rods_and_nuts(a2, rods2, yb0b, yt1b); electronics(a2, 2, dyb2, dyc2)
save(a2, {"V2_lower_platform_with_backplate": spine, "V2_top_cap": top2}, "V2_backplate")
report["V2"] = dict(perfboard=f"{2*U_HALF:.2f} x {pv1b-pv0b:.2f} mm", corner_holes=holes, stack=f"{yt1b-yb0b:.1f} mm", rods=rods2,
                    buzzer_front_v=bz_v0, battery_shift=dyb2, charge_shift=dyc2, sd_window=[sd["u0"]-2, sd["u1"]+2, sd["v0"]-2, sd["v1"]+2])
json.dump(report, open(f"{OUT}/mount_report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
