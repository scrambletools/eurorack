#!/usr/bin/env python3
"""gen_fab.py — regenerate the JLCPCB production files for the eurorack interposer.

Writes into fab/:
  - gerbers (F/B copper, masks, paste, silk, edge) + PTH/NPTH drills
  - eurorack-gerbers.zip                (upload this for PCB fab)
  - eurorack-BOM.csv / .xlsx            (SMD assembled parts only, from BOM.csv)
  - eurorack-CPL.csv                    (placement for the SMD parts)

Assembly model: JLCPCB places the SMD parts only (C1-C4, D1, FB1, R2; R3 is
DNP). Every through-hole part — all connectors, both jacks, and the K7805
module — is hand-soldered, so THT parts are dropped from the assembly BOM
and CPL automatically via their `through_hole` footprint attribute.

    Verify the polarized parts in JLCPCB's assembly preview — D1/D2 (SMA
    diodes) and U2 (SOIC-8 pin 1) carry no validated rotation corrections.

Usage:   python3 tools/gen_fab.py
Needs:   kicad-cli on PATH; openpyxl for the .xlsx BOM (optional).
Adapted from the hat's tools/gen_fab.py.
"""
import csv, os, re, subprocess, sys, zipfile

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = "eurorack"
PCB   = os.path.join(ROOT, f"{BOARD}.kicad_pcb")
BOM   = os.path.join(ROOT, "BOM.csv")
FAB   = os.path.join(ROOT, "fab")

GERBER_LAYERS = ("F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,"
                 "F.Silkscreen,B.Silkscreen,Edge.Cuts")

# JLCPCB rotation corrections (degrees added after the bottom-side transform).
# None validated for this board's parts yet; D1 (SMA) is the only polarized
# SMD part — check it in the preview.
ROTATION_PATTERNS = []
BY_REF = {}


def sh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(args)}\n{r.stderr or r.stdout}")


def gen_gerbers():
    os.makedirs(FAB, exist_ok=True)
    sh("kicad-cli", "pcb", "export", "gerbers", "--no-protel-ext", "--no-x2",
       "--subtract-soldermask", "-l", GERBER_LAYERS, "-o", FAB + os.sep, PCB)
    sh("kicad-cli", "pcb", "export", "drill", "--format", "excellon",
       "--excellon-separate-th", "--excellon-units", "mm",
       "--drill-origin", "absolute", "-o", FAB + os.sep, PCB)
    zp = os.path.join(FAB, f"{BOARD}-gerbers.zip")
    if os.path.exists(zp):
        os.remove(zp)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(FAB)):
            if f.endswith(".gbr") or f in (f"{BOARD}-NPTH.drl", f"{BOARD}-PTH.drl"):
                z.write(os.path.join(FAB, f), f)
    print(f"  gerbers + drills + {BOARD}-gerbers.zip")


def gen_bom():
    rows = list(csv.reader(open(BOM)))
    out = [["Comment", "Designator", "Footprint", "JLCPCB Part #（optional）"]]
    for r in rows[1:]:
        if len(r) < 10:
            continue
        if r[9].strip().upper() == "DNP" or r[8].strip().upper() in ("TH", "THT"):
            continue
        out.append([r[0], r[1], r[5], r[6]])
    with open(os.path.join(FAB, f"{BOARD}-BOM.csv"), "w", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(out)
    try:
        import openpyxl
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Sheet"
        for r in out:
            ws.append([c if c != "" else None for c in r])
        wb.save(os.path.join(FAB, f"{BOARD}-BOM.xlsx"))
        print(f"  {BOARD}-BOM.csv/.xlsx  ({len(out)-1} assembled parts)")
    except ImportError:
        print(f"  {BOARD}-BOM.csv  ({len(out)-1} parts)  [no openpyxl -> skipped .xlsx]")


def footprints():
    t = open(PCB).read()
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
        s = m.start() + 1; d = 0; i = s
        while i < len(t):
            c = t[i]
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
                if d == 0:
                    break
            i += 1
        b = t[s:i + 1]
        ref = re.search(r'\(property "Reference" "([^"]+)"', b)
        if not ref or ref.group(1).startswith("#"):
            continue
        at = re.search(r'\n\t\t\(at ([\-0-9.]+) ([\-0-9.]+)(?: ([\-0-9.]+))?\)', b)
        attr = re.search(r'\n\t\t\(attr ([^\)]*)\)', b)
        yield {
            "ref": ref.group(1).split()[0],   # "J6 (input)" -> "J6"
            "name": m.group(1).split(":")[-1],
            "top": re.search(r'\n\t\t\(layer "([^"]+)"\)', b).group(1) == "F.Cu",
            "x": float(at.group(1)), "y": float(at.group(2)),
            "rot": float(at.group(3) or 0),
            "attr": attr.group(1) if attr else "",
        }


def correction(ref, name):
    if ref in BY_REF:
        return BY_REF[ref]
    for pat, deg in ROTATION_PATTERNS:
        if re.search(pat, name):
            return deg
    return 0


def sort_key(f):
    return (f["ref"][0], int(re.sub(r"\D", "", f["ref"]) or 0))


def gen_cpl():
    out = [["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]]
    excluded = []
    for fp in sorted(footprints(), key=sort_key):
        if ("dnp" in fp["attr"] or "exclude_from_pos_files" in fp["attr"]
                or "through_hole" in fp["attr"]):
            excluded.append(fp["ref"]); continue
        base = fp["rot"] if fp["top"] else (180 - fp["rot"]) % 360
        rot = int(round((base + correction(fp["ref"], fp["name"])) % 360))
        out.append([fp["ref"], f"{fp['x']:.4f}mm", f"{-fp['y']:.4f}mm",
                    "Top" if fp["top"] else "Bottom", rot])
    with open(os.path.join(FAB, f"{BOARD}-CPL.csv"), "w", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(out)
    print(f"  {BOARD}-CPL.csv  ({len(out)-1} placed; excluded DNP/THT {sorted(excluded)})")
    print("  no validated rotation corrections -> verify D1/D2 (SMA) and U2 (SOIC-8) in the preview")


if __name__ == "__main__":
    print("Regenerating fab/ ...")
    gen_gerbers()
    gen_bom()
    gen_cpl()
    print("Done. Upload gerbers.zip (+ BOM/CPL if using JLC assembly for the SMD parts).")
