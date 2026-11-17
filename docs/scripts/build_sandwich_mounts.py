"""Removable avionics-bay mounts for the SANDWICH layout (two perfboards back to back, parts facing out).
Frame (same as the 3D viewer): X = across the boards (U), Y = rocket axis (nose up), Z = board normal (sensor side +Z).
  Board 1 (sensors, FETs, buzzer): sensor face Z = -4.49, back face -6.89.
  Board 2 (ESP32, SD, buck): inner face Z = -14.89, outer face -17.29, parts hang toward -Z.
  6x M3 hex standoffs 8 mm (Z -14.89 .. -6.89) at U = +-19.05, V = 5.08 / 78.74 / 152.40.
Tube ID 64, platforms dia 63.4, 5 mm thick.
V1 'slide-in rails': board 1 is 50.8 wide; its edges run in grooves of two full-length rails (one print with the lower
    platform). The whole sandwich slides down from the top, board 1 sits in pockets top and bottom.
V2 'backplate frame': board 1 is 58.4 wide and bolts through 6 rubber grommets (3 per side, <= 76 mm apart) to a printed
    frame behind its edges. The frame's centre is open, so board 2 nests inside it and the sandwich lifts straight off.
Both: 2x M4 threaded rods + nuts in front of board 1 clamp lower platform and top cap; wire pass-throughs; 3 switch holes.
usage: sandwich_mounts.py <models_root> <layout_sandwich.json> <out_dir> [public]"""
import sys, os, json, math, cadquery as cq
from cadquery import Color, Location as L, Vector as V
from OCP.gp import gp_Trsf
S, LAY, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PUBLIC = len(sys.argv) > 4 and sys.argv[4] == "public"
D = json.load(open(LAY))
P, PT = 2.54, 2.4
F1, B1 = D["BTOP"]["1"], D["BTOP"]["1"] - PT          # board 1 faces: -4.49 / -6.89
F2, B2 = D["BTOP"]["2"], D["BTOP"]["2"] - PT          # board 2 faces: -14.89 / -17.29
R_PLAT, T_PLAT, POCKET, R_CLIP = 63.4 / 2, 5.0, 3.0, 31.4
STEP = {"BMI270": "out/BMI270_7Semi-EVE-Breakout_marked.step", "LSM6DSO": "out/LSM6DSO_SmartElex-6DoF_marked.step",
        "BMP280": "public_out/BMP280_GY-BMP280_public.step" if PUBLIC else "out/BMP280_GY-BMP280-GrabCAD_marked.step",
        "MS5611": "public_out/MS5611_GY-63_public.step" if PUBLIC else "out/MS5611_GY-63-GrabCAD_marked.step",
        "ESP32": "public_out/ESP32-DevKitC-V4_public.step" if PUBLIC else "out/ESP32-DevKitC-V4-GrabCAD_marked.step",
        "SDCARD": "out/SD_Waveshare_MicroSD_Board.step", "TO220": "dl/k3d/Package_TO_SOT_THT.3dshapes/TO-220-3_Vertical.step"}
C_PRINT, C_FR4, C_RUB, C_STEEL, C_NYL = Color(.30, .45, .62), Color(.72, .55, .30), Color(.05, .05, .05), Color(.75, .75, .78), Color(.85, .85, .80)
SP = [(b["bu0"] + b["bu1"]) / 2 for b in D["boards"] if b["type"] == "SPACER"]
STANDOFFS = [((b["bu0"] + b["bu1"]) / 2, (b["bv0"] + b["bv1"]) / 2) for b in D["boards"] if b["type"] == "SPACER"]
batt = next(b for b in D["boards"] if b["type"] == "BATT"); charges = [b for b in D["boards"] if b["type"] == "PYRO"]
CLIP = cq.Workplane("XZ").circle(R_CLIP).extrude(-400).translate((0, -100, 0))     # nothing printed past R 31.4

def step_asm(t):
    try: return cq.Assembly.importStep(f"{S}/{STEP[t]}")
    except ValueError: return cq.Assembly(name=t).add(cq.importers.importStep(f"{S}/{STEP[t]}"), name=t + "_body", color=Color(.1, .1, .1))
def mat_loc(m, dy=0.0):
    t = gp_Trsf(); t.SetValues(m[0], m[4], m[8], m[12], m[1], m[5], m[9], m[13] + dy, m[2], m[6], m[10], m[14]); return cq.Location(t)
def prim(b):
    bx = b["box"]
    if b["cyl"]:  return cq.Workplane("XZ").circle(bx[0] / 2).extrude(-bx[1]).translate((bx[0] / 2, 0, bx[2] / 2))
    if b["cylZ"]: return cq.Workplane("XY").circle(bx[0] / 2).extrude(bx[2]).translate((bx[0] / 2, bx[1] / 2, 0))
    return cq.Workplane().box(*bx, centered=False)

def electronics(asm, dy_batt, dy_charge):
    for b in D["boards"]:
        if b["type"] == "SPACER": continue
        dy = dy_batt if b["type"] == "BATT" else dy_charge if b["type"] == "PYRO" else 0.0
        if b["type"] in STEP: asm.add(step_asm(b["type"]), name=b["id"], loc=mat_loc(b["m"], dy))
        else:
            col = {"BATT": Color(.17, .48, .85), "PYRO": Color(.70, .15, .12), "BUZZ": Color(.07, .07, .07), "BUCK": Color(.12, .48, .23)}[b["type"]]
            asm.add(prim(b), name=b["id"], loc=mat_loc(b["m"], dy), color=col)
    for i, (x, y) in enumerate(STANDOFFS):           # nylon hex standoffs + M3 screws through both boards
        asm.add(cq.Workplane("XY").polygon(6, 5.5 / math.cos(math.pi / 6)).circle(1.6).extrude(F2 - F2 + (B1 - F2)).translate((x, y, F2)),
                name=f"M3x8_standoff_{i+1}", color=C_NYL)
        asm.add(cq.Workplane("XY").circle(1.5).extrude(F1 - B2 + 1.5).translate((x, y, B2 - 1.5))
                .union(cq.Workplane("XY").circle(2.75).extrude(1.8).translate((x, y, F1))), name=f"M3_standoff_screw_{i+1}", color=C_STEEL)

def perfboard(u_half, v0, v1, extra=(), dia=6.5):
    pb = cq.Workplane("XY").box(2 * u_half, v1 - v0, PT, centered=(True, False, False))
    big = [(x, y) for x, y in extra]
    pts = [(-P / 2 + k * P, j * P) for k in range(-20, 21) for j in range(-5, 120)
           if abs(-P / 2 + k * P) < u_half - 1.0 and v0 + 1.0 < j * P < v1 - 1.0
           and all(math.hypot(-P / 2 + k * P - x, j * P - y) > dia / 2 + 0.9 for x, y in big)
           and all(math.hypot(-P / 2 + k * P - x, j * P - y) > 0.5 for x, y in STANDOFFS)]
    pb = pb.faces(">Z").workplane(centerOption="ProjectedOrigin", origin=(0, 0, 0)).pushPoints(pts).hole(1.0)
    pb = pb.faces(">Z").workplane(centerOption="ProjectedOrigin", origin=(0, 0, 0)).pushPoints(STANDOFFS).hole(3.2)
    if big: pb = pb.faces(">Z").workplane(centerOption="ProjectedOrigin", origin=(0, 0, 0)).pushPoints(big).hole(dia)
    return pb.translate((0, v0, 0))

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
    os.makedirs(f"{OUT}/{folder}", exist_ok=True)
    for name, wp in parts.items():
        cq.Assembly(name=name + "_part").add(wp, name=name, color=C_PRINT).save(f"{OUT}/{folder}/{name}.step", "STEP")
        cq.exporters.export(wp, f"{OUT}/{folder}/{name}.stl", tolerance=0.05, angularTolerance=0.2)
    asm.save(f"{OUT}/{folder}/{folder}_ASSEMBLY.step", "STEP")

# ---- common sizes ----
PV0, PV1 = -3.81, 168.91                             # board 1 length (cut on hole-grid lines), 172.7 mm
QV0, QV1, QU = 1.27, 158.75, 22.86                   # board 2: 45.72 x 157.5, clear of both platforms
RODS = [(-19.0, 13.0), (19.0, 13.0)]                 # in front of board 1: clear of FETs (|u|<11.5), buzzer and both boards
LOW_WIRES = [(-6.35, 6.0), (6.35, 6.0)]              # charge wires up to the FETs (front of board 1)
TOP_WIRES = [(4.0, (B1 + F2) / 2), (0.0, -24.0)]     # battery feed down the gap between the boards; battery -> buck (board 2 outer side)
SWITCHES = [(-10.0, 20.0), (0.0, 22.0), (10.0, 20.0)]
report = {}

def board2(notches=()):
    b = perfboard(QU, QV0, QV1)
    for (x, y) in notches:                           # edge notch so the frame boss passes when the sandwich lifts off
        x0 = min(abs(x) - 4.7, QU); b = b.cut(cq.Workplane("XY").box(QU - x0 + 1, 11.0, PT + 2, centered=False)
                                              .translate((x0 if x > 0 else -QU - 1, y - 5.5, -1)))
    return b.translate((0, 0, B2))

# ============================ V1 : slide-in rails ============================
U1 = 25.4                                            # board 1: 50.8 wide (20 holes), edges ride in the rails
gw, gt, depth = 0.30, 0.15, 2.8                      # groove clearance across / through thickness, edge engagement
yb0, yt1 = PV0 - (T_PLAT - POCKET), PV1 + (T_PLAT - POCKET)
rail_in, rail_out, rz0, rz1 = U1 - depth, U1 + gw + 3.0, B1 - 3.0, F1 + 3.0
lower = platform(yb0, RODS, LOW_WIRES)
lower = lower.cut(cq.Workplane("XY").box(2 * (U1 + gw), POCKET, PT + 2 * gt, centered=(True, False, False)).translate((0, PV0, B1 - gt)))
for s in (-1, 1):
    x0, x1 = (rail_in, rail_out) if s > 0 else (-rail_out, -rail_in)
    rail = cq.Workplane("XY").box(x1 - x0, PV1 - PV0, rz1 - rz0, centered=False).translate((x0, PV0, rz0))
    gx0, gx1 = (rail_in - 0.01, U1 + gw) if s > 0 else (-(U1 + gw), -(rail_in - 0.01))
    groove = cq.Workplane("XY").box(gx1 - gx0, PV1 - PV0 + 1, PT + 2 * gt, centered=False).translate((gx0, PV0, B1 - gt))
    lead = cq.Workplane("XY").box(gx1 - gx0 + 1.2, 4, PT + 1.6, centered=False).translate((gx0 - (0.6 if s < 0 else 0), PV1 - 4, B1 - 0.8))
    lower = lower.union(rail).cut(groove).cut(lead)
lower = lower.intersect(CLIP)
top1 = platform(PV1 - POCKET, RODS, TOP_WIRES, SWITCHES)
top1 = top1.cut(cq.Workplane("XY").box(2 * (U1 + gw), POCKET, PT + 2 * gt, centered=(True, False, False)).translate((0, PV1 - POCKET, B1 - gt)))
for s in (-1, 1):
    x0, x1 = (rail_in - 0.3, rail_out + 0.3) if s > 0 else (-rail_out - 0.3, -rail_in + 0.3)
    top1 = top1.cut(cq.Workplane("XY").box(x1 - x0, POCKET, rz1 - rz0 + 0.6, centered=False).translate((x0, PV1 - POCKET, rz0 - 0.3)))
dyb1 = max(0.0, (yt1 + 2.0) - batt["v0"]); dyc1 = min(0.0, (yb0 - 4.0) - max(c["v1"] for c in charges))
a1 = cq.Assembly(name="AvBay_Sandwich_V1_slide_rails")
a1.add(lower, name="S1_lower_platform_with_rails", color=C_PRINT); a1.add(top1, name="S1_top_cap", color=C_PRINT)
a1.add(perfboard(U1, PV0, PV1).translate((0, 0, B1)), name=f"board1_{2*U1:.1f}x{PV1-PV0:.1f}", color=C_FR4)
a1.add(board2(), name=f"board2_{2*QU:.1f}x{QV1-QV0:.1f}", color=C_FR4)
rods_and_nuts(a1, RODS, yb0, yt1); electronics(a1, dyb1, dyc1)
save(a1, {"S1_lower_platform_with_rails": lower, "S1_top_cap": top1}, "Sandwich_V1_slide_rails")
report["V1"] = dict(board1=f"{2*U1:.2f} x {PV1-PV0:.2f} mm (20 x 68 holes)", board2=f"{2*QU:.2f} x {QV1-QV0:.2f} mm",
                    stack_platforms=f"{yt1-yb0:.1f} mm", rods=RODS, battery_shift=round(dyb1, 2), charge_shift=round(dyc1, 2),
                    ext={"1": [-U1, U1, PV0, PV1], "2": [-QU, QU, QV0, QV1]})

# ============================ V2 : backplate frame + grommets ============================
U2, GU = 29.21, 24.13                                # board 1: 58.42 wide; grommet column on a hole line
GROM = [(s * GU, y) for y in (38.10, 101.60, 162.56) for s in (-1, 1)]     # clear of standoffs (>= 10 mm) and of the SD board's lift path
NOTCH = [(x, y) for x, y in GROM if QV0 < y < QV1]                          # board 2 needs edge notches at the lower two rows
fz1 = B1 - 1.2                                       # frame boss top: grommet's lower flange sits on it
fb0, fb1, fu0 = fz1 - 1.0, fz1 - 6.0, QU + 0.6       # frame bar (behind board 1's edges, outside board 2's footprint)
yb0b = PV0 - 1.0 - T_PLAT                            # board floats 1 mm above the lower platform
yt0b = PV1 + 1.0                                     # top cap underside
spine = platform(yb0b, RODS, LOW_WIRES)
for s in (-1, 1):
    x0, x1 = (fu0, R_CLIP) if s > 0 else (-R_CLIP, -fu0)
    bar = cq.Workplane("XY").box(x1 - x0, yt0b + POCKET - (yb0b + T_PLAT), fb0 - fb1, centered=False).translate((x0, yb0b + T_PLAT, fb1))
    for (x, y) in GROM:
        if x * s > 0:
            bar = bar.union(cq.Workplane("XY").circle(4.2).extrude(fz1 - fb0).translate((x, y, fb0)))
    spine = spine.union(bar)
for (x, y) in GROM:
    spine = spine.cut(cq.Workplane("XY").circle(1.25).extrude(12).translate((x, y, fb1 - 3)))        # M3 self-tap into the boss
spine = spine.intersect(CLIP)
top2 = platform(yt0b, RODS, TOP_WIRES, SWITCHES)
for s in (-1, 1):                                    # pockets for the frame bar tops
    x0, x1 = (fu0 - 0.3, R_CLIP + 1) if s > 0 else (-R_CLIP - 1, -fu0 + 0.3)
    top2 = top2.cut(cq.Workplane("XY").box(x1 - x0, POCKET, fb0 - fb1 + 0.6, centered=False).translate((x0, yt0b, fb1 - 0.3)))
yt1b = yt0b + T_PLAT
dyb2 = max(0.0, (yt1b + 2.0) - batt["v0"]); dyc2 = min(0.0, (yb0b - 4.0) - max(c["v1"] for c in charges))
a2 = cq.Assembly(name="AvBay_Sandwich_V2_backplate_frame")
a2.add(spine, name="S2_lower_platform_with_frame", color=C_PRINT); a2.add(top2, name="S2_top_cap", color=C_PRINT)
a2.add(perfboard(U2, PV0, PV1, GROM).translate((0, 0, B1)), name=f"board1_{2*U2:.1f}x{PV1-PV0:.1f}_6grommets", color=C_FR4)
a2.add(board2(NOTCH), name=f"board2_{2*QU:.1f}x{QV1-QV0:.1f}", color=C_FR4)
for i, (x, y) in enumerate(GROM):
    g = (cq.Workplane("XY").circle(4.6).extrude(1.2).translate((0, 0, -1.2))
         .union(cq.Workplane("XY").circle(3.25).extrude(PT)).union(cq.Workplane("XY").circle(4.6).extrude(1.2).translate((0, 0, PT)))
         .cut(cq.Workplane("XY").circle(1.6).extrude(PT + 4).translate((0, 0, -2))))
    a2.add(g, name=f"grommet_{i+1}", loc=L(V(x, y, B1)), color=C_RUB)
    a2.add(cq.Workplane("XY").circle(1.5).extrude(F1 + 1.2 - (fb1 + 1.0)).translate((x, y, fb1 + 1.0))
           .union(cq.Workplane("XY").circle(2.75).extrude(1.8).translate((x, y, F1 + 1.2))), name=f"M3_grommet_screw_{i+1}", color=C_STEEL)
rods_and_nuts(a2, RODS, yb0b, yt1b); electronics(a2, dyb2, dyc2)
save(a2, {"S2_lower_platform_with_frame": spine, "S2_top_cap": top2}, "Sandwich_V2_backplate_frame")
report["V2"] = dict(board2_notches=f"{len(NOTCH)} edge notches 11 mm long, {QU-(GU-4.7):.2f} mm deep", board1=f"{2*U2:.2f} x {PV1-PV0:.2f} mm (23 x 68 holes) + 6 x dia 6.5 grommet holes", board2=f"{2*QU:.2f} x {QV1-QV0:.2f} mm",
                    grommets=GROM, stack_platforms=f"{yt1b-yb0b:.1f} mm", rods=RODS, battery_shift=round(dyb2, 2), charge_shift=round(dyc2, 2),
                    ext={"1": [-U2, U2, PV0, PV1], "2": [-QU, QU, QV0, QV1]})
report["standoffs"] = STANDOFFS
json.dump(report, open(f"{OUT}/mount_report.json", "w"), indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("ext", "grommets")} if isinstance(v, dict) else v for k, v in report.items()}, indent=1))
