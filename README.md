# Eurorack Interposer — power, hat stacking, and panel jacks

A small 2-layer PCB that turns the **ESP32-P4-ETH carrier + Scramble Hat-trik**
stack into a eurorack module. It sits **between the carrier and the hat**:

```
        ┌───────────────┐
        │  Scramble Hat │   (rotated 180° vs. normal mounting)
        ├─ J4/J5 male ──┤
        │  THIS BOARD   │──▶ 10-pin eurorack power in, 5 V buck out,
        ├─ J2/J3 female─┤     3.5 mm in/out jacks to the faceplate
        │  ESP32-P4-ETH │
        └───────────────┘
```

## What it does

1. **Eurorack power** (J1, 2×5 shrouded IDC): takes +12 V from the bus,
   through reverse-polarity protection (D1) and a ferrite (FB1), into a
   K7805-1000R3 buck (U1) → **5 V** injected into the mezzanine +5 V pin,
   powering the carrier (and the hat through it). −12 V is brought onto the
   board but unused. **Do not power the carrier's USB-C at the same time.**
2. **Hat interposer** (J2/J3 female 8.5 mm stacking sockets down to the
   carrier; J4/J5 male headers up to the hat): a full 7+7 pass-through,
   **cross-wired so the hat mounts rotated 180°** relative to its normal
   orientation (XLR pointing the other way).
3. **Panel audio** (J6 in, J7 out, 3.5 mm mono threaded jacks, vertical
   nose-up mount): a fully **isolated** circuit — no connection to power or
   the mezzanine — that brings the jacks to header J8, from which wires run
   to the hat's J1/J2 hand-solder pads.

## Mezzanine crossover map

J4 sits directly above J2, J5 directly above J3, **all pin 1s oriented the
same way** (this matters — the crossover assumes it). Because the hat is
rotated 180°, its J3 lands on this board's J5 and its J4 on this board's J4,
pin order reversed; the routing below un-scrambles that:

| This J2 (carrier row A) | net | → appears on | This J3 (carrier row B) | net | → appears on |
|---|---|---|---|---|---|
| 1 | ASDOUT | J5.7 | 1 | +5V | J4.7 |
| 2 | LRCK | J5.6 | 2 | PASS_B2 | J4.6 |
| 3 | GND | J5.5 | 3 | GND | J4.5 |
| 4 | DSDIN | J5.4 | 4 | PASS_B4 | J4.4 |
| 5 | BCLK | J5.3 | 5 | +3V3 | J4.3 |
| 6 | MCLK | J5.2 | 6 | SCL | J4.2 |
| 7 | DET | J5.1 | 7 | SDA | J4.1 |

(PASS_B2/PASS_B4 are unused by the hat but passed through anyway.)

## Audio to the hat (J8)

J8 (1×4 male) **direct-mates the hat's J7 socket** (1×4 female, 8.5 mm
stacking — same series and stack height as the J2↔J4 / J3↔J5 mezzanine, so
all three connectors seat together). On the hat: populate J7 + R27 (forces
instrument mode), leave J1 off. Pin-for-pin when mated:

| J8 pin | net | hat J7 pin / net | note |
|---|---|---|---|
| 1 | AIN_T | 1 `GTIP` | input tip |
| 2 | AIN_S | 2 `PGND` | input ground |
| 3 | AOUT_S | 3 `AGND` | output ground |
| 4 | AOUT_T | 4 `HP_L_OUT` | output tip (left channel) |

Signals sit on the outer pins with **both grounds between them** — that
ordering is deliberate (kills output→input crosstalk across the header);
keep it if anything gets re-pinned. **Layout:** place J8 so it lands on the
hat's J7 with all pin 1s consistently oriented under the 180° hat rotation —
same rule as J4/J5.

Fallback: the same J8 pins can still be hand-wired to the hat pads
(AIN_T→J1 T, AIN_S→J1 S + R→S jumper, AOUT_T→J2 T, AOUT_S→J2 TN) with
shielded cable, shield landed at this board's end only.

## Display pass-through (J9 → J10)

The hat's **J6** display header (1 = GND/AGND, 2 = +3V3, 3 = SCL, 4 = SDA)
plugs into **J9** (1×4 female, 8.5 mm H85) on this board; **J10** (same
socket) presents the identical pinout for an I²C display (the usual
GND/VCC/SCL/SDA order of SSD1306-style OLED modules — verify your display's
order before plugging). J9→J10 is a 1:1 pass-through on dedicated `DISP_*`
nets, deliberately **not** tied to this board's ground — the display's
return flows through the hat's AGND like a directly-plugged display, so no
ground loop is added.

**Hat-side requirement:** for the stack, the hat's J6 male header must be
fitted on the hat's **bottom** side (pins pointing down at this board) —
JLC assembles it top-side by default, so eurorack builds should hand-fit J6
(ask for it excluded from assembly, or rework). **Layout:** J9 must land
directly under hat J6 with pin 1s consistently oriented under the 180° hat
rotation — same rule as J8; J10 near the faceplate wherever the display
mounts.

**Levels:** eurorack signals swing ±5 V (10 Vpp) but the hat's instrument
input runs from a 5 V rail — hot patches will clip. R2 (series, default 0 Ω)
+ R3 (shunt, DNP) form an optional input attenuator: populate e.g.
R2 = 100k / R3 = 47k for ≈ −10 dB into the hat's ~500 kΩ input. The output
level (hat DAC, ~2 Vpp max) is simply a bit quiet by modular standards.

**Grounding:** input sleeve ties to hat PGND, output sleeve to hat AGND —
the hat keeps these split. The jacks **must have plastic threaded noses**
(Thonkiconn-style) so the metal faceplate doesn't short the two sleeves
together; don't substitute metal-bushing jacks.

**Jacks:** XKB **PJ-3410** (LCSC C5146694) — a **vertical** PCB jack: the
nose points straight up off the board (total ≈ 19.5 mm above the PCB:
13 body + 2 flange + 4.5 thread), terminals exit the rear face down
through the board. PBT (plastic) threaded nose **M7.7 × 0.75**, so drill
the faceplate **≥ 7.8 mm** (not the 6 mm of a Thonkiconn).
**Mechanical consequence:** the jack faces must point at the faceplate, so
either the jack area of the board sits parallel to the panel, or the
mounting arrangement otherwise presents the noses through it — TBD during
layout. Footprint pads were taken from the LCSC/EasyEDA source footprint;
the pad map (T = terminal 5 tip spring, S = terminal 4 brass barrel,
TN = terminal 2 NC throw, 3 = floating) should be **bench-verified with a
meter on a sample** before ordering boards. Terminal 3 is intentionally
unconnected — expect one benign "pad not in netlist" note per jack at F8.

## Power header orientation

J1 pins 1–2 = **−12 V** (red-stripe end), 3–8 = GND, 9–10 = +12 V. Mark the
stripe end on silk. D1 blocks a reversed ribbon from applying −12 V to the
buck.

## Status

- Schematic + BOM done, ERC clean, netlist verified (crossover + isolation).
- PCB not yet laid out (footprints assigned, board is empty).
- Layout notes: J2/J3 spacing must match the carrier's two 1×7 rows —
  **copy the exact J3/J4 placement from the hat layout** (rows are
  ~17.553 mm apart center-to-center, *not* on a shared 2.54 mm grid);
  J4 above J2 and J5 above J3 at identical XY; jacks are vertical
  (nose-up) — plan how their noses reach the faceplate before placing.
