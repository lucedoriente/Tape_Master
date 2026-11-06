sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
# find wires with x near 182.88 and y between 120 and 150
wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(xy\s+([-\d\.]+)\s+([-\d\.]+)\)\)\)', text)
for x1, y1, x2, y2 in wires:
    if abs(float(x1) - 182.88) < 1.0 or abs(float(x2) - 182.88) < 1.0:
        if 120 <= float(y1) <= 150:
            print(f"Wire ({x1}, {y1}) -> ({x2}, {y2})")

# find labels near there
labels = re.findall(r'\((?:global_)?label\s+"([^"]+)"\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\)', text)
for l, x, y, rot in labels:
    if 180 <= float(x) <= 200 and 120 <= float(y) <= 150:
        print(f"Label {l} at ({x}, {y})")
