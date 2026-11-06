sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'TAPE_FILTERED', text)]
print(f"Found {len(matches)} occurrences of TAPE_FILTERED:")
for idx in matches:
    print(text[max(0, idx-100):min(len(text), idx+150)])
    print("="*40)
