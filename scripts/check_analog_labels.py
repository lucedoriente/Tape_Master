import os, re

sch_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(sch_path, "r", encoding="utf-8") as f:
    text = f.read()

# find labels
labels = re.findall(r'\((?:global_)?label\s+"([^"]+)"', text)
print("Analog Ingest Labels:")
for l in sorted(set(labels)):
    print(" ", l)
