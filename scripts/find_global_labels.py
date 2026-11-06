sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
gls = re.findall(r'\(global_label\s+"([^"]+)"', text)
print("Global labels in 03_Analog_Ingest:")
for g in sorted(set(gls)):
    print(" ", g)
