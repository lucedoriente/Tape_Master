import re

sch_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect all labels and pins connected to U3
pico_block = ""
idx = text.find('(property "Reference" "U3"')
if idx != -1:
    start = text.rfind('(symbol', 0, idx)
    end = text.find('\n  )', idx)
    pico_block = text[start:end+4]

# Also inspect wires around U3
wires = re.findall(r'\(wire\s+\(pts\s+\(xy\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(xy\s+([-\d\.]+)\s+([-\d\.]+)\)\)\)', text)
labels = re.findall(r'\(label\s+"([^"]+)"\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\)', text)

print("Labels in MCU Core:")
for l, x, y, rot in sorted(labels):
    print(f"  {l} at ({x}, {y}, rot={rot})")
