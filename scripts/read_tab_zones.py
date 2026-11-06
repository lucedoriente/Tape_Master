with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

import re
zones = re.findall(r'\t\(zone[\s\S]*?\n\t\)', text)
print("Found zones at tab 1:", len(zones))
for i, z in enumerate(zones):
    print(f"=== Zone {i} ===")
    lines = z.splitlines()[:15]
    print("\n".join(lines))
