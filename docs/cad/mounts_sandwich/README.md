# Bay mounts for the sandwich layout (17 Nov 2026)

Two perfboards back to back, both with parts facing out:
- **Board 1** (sensor side) carries the 6 sensors, FET A and FET B, and the buzzer.
- **Board 2** (back side) carries the ESP32, the SD card and the buck.
- Six M3 × 8 hex standoffs (nylon) join the boards at U ±19.05, V 5.08 / 78.74 / 152.40 mm.

Frame: X runs across the boards, Y along the rocket axis (nose up), Z is the board normal (sensor side +Z).

Print the parts in PETG at 4 walls and 40 % infill. Each part prints flat on its platform disc.

| | V1 slide-in rails | V2 backplate frame + grommets |
|---|---|---|
| Printed parts | S1_lower_platform_with_rails, S1_top_cap | S2_lower_platform_with_frame, S2_top_cap |
| Board 1 | 50.80 × 172.72 mm (20 × 68 holes) | 58.42 × 172.72 mm (23 × 68 holes), plus 6 holes Ø6.5 at U ±24.13, V 38.1 / 101.6 / 162.56 |
| Board 2 | 45.72 × 157.48 mm | Same size, plus 4 edge notches (11 mm long, 3.4 mm deep) at V 38.1 and 101.6 |
| How the boards are held | Board 1's edges run in grooves in the rails (2.8 mm engagement, 0.3 mm clearance) and sit in pockets top and bottom | Board 1 bolts through 6 rubber grommets (M3 × 10 self-tapping into a printed boss), with supports at most 76 mm apart |
| Removal | Remove the top cap, then pull the sandwich up and out | Remove 6 screws, then lift the sandwich straight off toward the sensor side |
| Platform to platform | 176.7 mm | 184.7 mm |

**Both versions**
- Two M4 threaded rods with nuts run in front of board 1, at (±19, +13) mm.
- Wire holes Ø6:
  - Lower platform: charge wires at (±6.35, +6).
  - Top cap: the battery feed down the gap between the boards at (4, −10.9), and the battery-to-buck wire at (0, −24).
- Three Ø6.5 switch holes in the top cap, at (−10, 20), (0, 22) and (10, 20).

**Checks:** the printed parts don't touch any board, part, standoff or screw, and nothing extends past R 31.4 mm.

**Files:** STEP and STL for each printed part, a full assembly STEP (zipped), and a preview showing the front, the side, and a cross-section at Y = 100 mm. `sandwich_mounts.py` rebuilds everything from `layout_sandwich_from_viewer.json`.
