with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb", "r", encoding="utf-8") as f:
    text = f.read()

import re
zones = re.findall(r'\(zone[\s\S]*?\n  \)', text)
print(f"Found {len(zones)} zones in PCB:")
for i, z in enumerate(zones):
    print(f"=== Zone {i} ===")
    print(z[:400])
