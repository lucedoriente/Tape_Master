sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
for m in re.finditer(r'\((?:global_)?label\s+"TAPE_FILTERED"[\s\S]*?\)', text):
    print(m.group(0))
