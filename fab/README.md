# Eurorack Interposer — Fabrication Files

Production files for **JLCPCB**. 2-layer board, ~84.7 × 30 mm.

| File | Purpose |
|---|---|
| `eurorack-gerbers.zip` | **PCB fab** — gerbers + drills (upload this) |
| `eurorack-BOM.csv` / `.xlsx` | **Assembly BOM** — the SMD parts only |
| `eurorack-CPL.csv` | Placement file for the SMD parts |

## Assembly split

- **JLCPCB SMT (optional):** `C1–C7`, `D1/D2`, `FB1/FB2`, `R2–R7`, `U2`,
  `NT1` — 19 placements. If using assembly, **verify orientation of D1/D2
  (SMA) and U2 (SOIC-8 pin 1) in the preview** — no validated rotation
  corrections exist for this board.
- **Hand-solder (all THT):** `J1` (power IDC), `J2/J3` (carrier sockets),
  `J4/J5` (hat headers), `J6/J7` (panel jacks), `J8` (audio header),
  `J10` (display socket), `U1` (K7805 buck module).
- **DNP:** none. (R2/R3 = 100k/39k eurorack input pad; for guitar-level
  sources instead fit R2 = 0 Ω and omit R3 — see root README.)

## Before ordering

- Bench-verify the PJ-3410 jack pad map (T/S/TN) with a meter on a sample.
- Caliper-check the carrier's mezzanine row spacing against J2/J3
  (designed at 17.75 mm; the fit-proven hat uses 17.577 mm — see root README).

Regenerate everything with `python3 tools/gen_fab.py` (KiCad closed).
