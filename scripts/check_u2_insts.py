import re

with open(r"kicad\01_Power_Supply.kicad_sch", "r", encoding="utf-8") as f:
    text = f.read()

for m in re.finditer(r'\(symbol \(lib_id "([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)[^\)]*\)\s+\(unit\s+(\d+)\).*?\(property "Reference"\s+"([^"]+)"', text, re.DOTALL):
    print(f"Inst: {m.group(5)} lib={m.group(1)} at ({m.group(2)}, {m.group(3)}) unit={m.group(4)}")
