import os, re

with open(r"C:\Program Files\KiCad\9.0\share\kicad\symbols\Display_Character.kicad_sym", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'\(symbol "([^\"]*BARGRAPH[^\"]*)"', text)
print("Bargraph matches:", set(matches))
matches2 = re.findall(r'\(symbol "([^\"]*10[^\"]*)"', text)
print("10-element matches:", [m for m in set(matches2) if 'led' in m.lower() or 'bar' in m.lower()])
