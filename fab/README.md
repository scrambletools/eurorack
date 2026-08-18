# Eurorack Interposer — Fabrication Files

Production files for **JLCPCB**. 2-layer board, ~84.7 × 30 mm.

| File | Purpose |
|---|---|
| `eurorack-gerbers.zip` | **PCB fab** — gerbers + drills (upload this) |
| `eurorack-BOM.csv` / `.xlsx` | **Assembly BOM** — every part (SMD + THT) |
| `eurorack-CPL.csv` | Placement file — every assembled part |

## Assembly

**JLCPCB places everything** — 28 placements: the 18 SMD parts
(`C1–C7`, `D1/D2`, `FB1/FB2`, `R2–R7`, `U2`) plus all through-hole
(`J1` power IDC, `J2/J3` carrier sockets, `J4/J5` hat headers,
`J6/J7` panel jacks, `J8`, `J10`, `U1` K7805 buck). Notes:

- THT sits on **both sides** (top: J4/J5/J6/J7/J8/J10; bottom:
  J1/J2/J3/U1) — expect JLC to quote the THT as hand-soldered on
  their line at checkout.
- **Verify orientation in the preview** — no validated rotation
  corrections exist for this board: `D1/D2` (SMA cathode band),
  `U2` (SOIC-8 pin 1), `J1` (shroud key toward the marked −12 V end),
  `U1` (K7805 pin 1 = Vin), `J6/J7` (asymmetric jack pad pattern).
- Excluded from assembly: `NT1` only (net tie — copper, not a part).
- **DNP:** none. (R2/R3 = 100k/39k eurorack input pad; for guitar-level
  sources instead fit R2 = 0 Ω and omit R3 — see root README.)

## Before ordering

- Bench-verify the PJ-3410 jack pad map (T/S/TN) with a meter on a sample.
- Caliper-check the carrier's mezzanine row spacing against J2/J3
  (designed at 17.75 mm; the fit-proven hat uses 17.577 mm — see root README).

Regenerate everything with `python3 tools/gen_fab.py` (KiCad closed).
