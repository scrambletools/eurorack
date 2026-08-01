#!/usr/bin/env python3
"""Print the constrained footprint placements for the eurorack module.

The module's mezzanine sockets must copy the hat's J3/J4 geometry (that IS
the carrier row geometry), and J8/J9 must land exactly under hat J7/J6 when
the hat is mounted rotated 180 degrees. Rather than hand-copying
coordinates, this reads the hat board and prints every constrained
placement in the hat's coordinate frame (place module J2 at the printed
position, or shift ALL printed positions by one common offset).

The 180-degree mapping: a hat point p lands at (2C - p) on the module,
where 2C = hat J3 pad 1 + hat J4 pad 7 (the rotation centre C is the
mezzanine centroid). Rotations: mapped parts keep their pad row on the
same line but run the opposite direction, so their rotation is the hat
rotation + 180.

Usage: python3.14 tools/map_hat.py [path-to-hat-kicad_pcb]
(needs KiCad's pcbnew python module)
"""
import sys
import pcbnew

HAT = sys.argv[1] if len(sys.argv) > 1 else "../ES8389-Hat/scramble_hat.kicad_pcb"

b = pcbnew.LoadBoard(HAT)
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}

def pad(ref, num):
    for p in fps[ref].Pads():
        if p.GetNumber() == str(num):
            pos = p.GetPosition()
            return (pos.x / 1e6, pos.y / 1e6)
    raise KeyError(f"{ref} pad {num}")

def fppos(ref):
    p = fps[ref].GetPosition()
    return (p.x / 1e6, p.y / 1e6, fps[ref].GetOrientationDegrees())

j3p1, j4p7 = pad("J3", 1), pad("J4", 7)
two_c = (j3p1[0] + j4p7[0], j3p1[1] + j4p7[1])

def mapped(ref):
    x, y, rot = fppos(ref)
    return (two_c[0] - x, two_c[1] - y, (rot + 180) % 360)

j3, j4 = fppos("J3"), fppos("J4")
print(f"hat J3 pin1 {j3p1}  J4 pin7 {j4p7}")
print(f"row spacing dy={j4[1]-j3[1]:.3f} mm  dx={j4[0]-j3[0]:.3f} mm"
      f"  (produced boards: dy=17.577 dx=0.000 -- investigate any difference!)")
print()
print("module placements (hat coordinate frame; shift all together if desired):")
print(f"  J2 (socket, carrier row A): ({j3[0]:.3f}, {j3[1]:.3f}) rot {j3[2]:.0f}")
print(f"  J3 (socket, carrier row B): ({j4[0]:.3f}, {j4[1]:.3f}) rot {j4[2]:.0f}")
print(f"  J4 (male up, same XY as J2): ({j3[0]:.3f}, {j3[1]:.3f}) rot {j3[2]:.0f}")
print(f"  J5 (male up, same XY as J3): ({j4[0]:.3f}, {j4[1]:.3f}) rot {j4[2]:.0f}")
for mod, hat in (("J8", "J7"), ("J9", "J6")):
    x, y, rot = mapped(hat)
    print(f"  {mod} (under hat {hat}):        ({x:.3f}, {y:.3f}) rot {rot:.0f}")

bb = b.GetBoardEdgesBoundingBox()
hx0, hy0 = bb.GetLeft() / 1e6, bb.GetTop() / 1e6
hx1, hy1 = bb.GetRight() / 1e6, bb.GetBottom() / 1e6
mx0, my0 = two_c[0] - hx1, two_c[1] - hy1
mx1, my1 = two_c[0] - hx0, two_c[1] - hy0
print()
print(f"hat outline over the module: ({mx0:.2f}, {my0:.2f}) to ({mx1:.2f}, {my1:.2f})")
print("  -> tall module parts (jacks, J10/display, buck) must sit OUTSIDE this"
      " rectangle;\n     inside it keep top-side parts under ~6 mm"
      " (8.5 mm stack minus hat bottom-side parts)")
