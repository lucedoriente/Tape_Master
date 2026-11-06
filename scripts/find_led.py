import os, re

with open(r"C:\Program Files\KiCad\9.0\share\kicad\symbols\Device.kicad_sym", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'\(symbol "([^\"]*LED[^\"]*)"', text)
print("LED symbols in Device:", set(matches))
