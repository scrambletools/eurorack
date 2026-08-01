# Eurorack Interposer — Fabrication Files

Production files for **JLCPCB**. 2-layer board, ~84.7 × 30 mm.

| File | Purpose |
|---|---|
| `eurorack-gerbers.zip` | **PCB fab** — gerbers + drills (upload this) |
| `eurorack-BOM.csv` / `.xlsx` | **Assembly BOM** — the SMD parts only |
| `eurorack-CPL.csv` | Placement file for the SMD parts |

## Assembly split

- **JLCPCB SMT (optional):** `C1–C4`, `D1`, `FB1`, `R2` — 5 BOM lines, 7
  placements. Cheap enough to simply hand-solder instead if preferred.
  If using assembly, **verify D1 (SMA diode) orientation in the preview** —
  no validated rotation correction exists for this board.
- **Hand-solder (all THT):** `J1` (power IDC), `J2/J3` (carrier sockets),
  `J4/J5` (hat headers), `J6/J7` (panel jacks), `J8` (audio header),
  `J10` (display socket), `U1` (K7805 buck module).
- **DNP:** `R3` (input attenuator shunt — populate with R2 swapped to a
  series value only if attenuating eurorack levels; see root README).

## Before ordering

- Bench-verify the PJ-3410 jack pad map (T/S/TN) with a meter on a sample.
- Caliper-check the carrier's mezzanine row spacing against J2/J3
  (designed at 17.75 mm; the fit-proven hat uses 17.577 mm — see root README).

Regenerate everything with `python3 tools/gen_fab.py` (KiCad closed).
