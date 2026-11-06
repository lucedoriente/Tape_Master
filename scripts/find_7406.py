import os, re

with open(r"C:\Program Files\KiCad\9.0\share\kicad\symbols\74xx.kicad_sym", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'\(symbol "([^\"]*06[^\"]*)"', text)
print("Matches in 74xx:", set(matches))
