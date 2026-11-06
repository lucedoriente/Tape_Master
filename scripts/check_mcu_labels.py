sch_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_path, "r", encoding="utf-8") as f:
    text = f.read()

import re
labels = re.findall(r'\((?:global_)?label\s+"([^"]+)"', text)
print("MCU Core Labels:")
for l in sorted(set(labels)):
    print(" ", l)
