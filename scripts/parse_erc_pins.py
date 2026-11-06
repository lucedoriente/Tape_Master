import re

with open("Tape-Master-erc.rpt", "r", encoding="utf-8") as f:
    text = f.read()

# Find all pin coordinates reported by ERC
pins_reported = re.findall(r'@\(([-\d.]+)\s+mm,\s+([-\d.]+)\s+mm\):\s+Symbol\s+(\S+)\s+Pin\s+(\S+)', text)
print(f"Total pins reported: {len(pins_reported)}")
for p in pins_reported[:15]:
    print(f"Ref {p[2]} Pin {p[3]}: ({p[0]}, {p[1]})")
