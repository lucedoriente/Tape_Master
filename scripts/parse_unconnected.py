with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\drc_check.rpt", "r", encoding="utf-8") as f:
    text = f.read()

import re
items = re.findall(r'\[unconnected_items\]:[\s\S]*?(?=\[|\Z|\*\*)', text)
print(f"Total unconnected items: {len(items)}")
for i, item in enumerate(items):
    lines = [l.strip() for l in item.strip().splitlines() if l.strip()]
    print(f"{i+1}: {' -> '.join(lines[1:])}")
