sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
labels = re.findall(r'\((?:global_)?label\s+"([^"]+)"\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\)', text)
for l, x, y, rot in labels:
    if "AZIMUTH" in l or "REMOTE" in l:
        print(f"Label {l} at ({x}, {y})")
