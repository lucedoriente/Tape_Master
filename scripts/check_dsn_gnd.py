with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.dsn", "r", encoding="utf-8") as f:
    text = f.read()

import re
net_gnd = re.search(r'\(net\s+GND\b[\s\S]*?\n\s*\)', text)
if net_gnd:
    print(net_gnd.group(0)[:500])
else:
    print("Net GND not found in network section of DSN!")
