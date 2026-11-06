import os

with open(r"C:\Program Files\KiCad\9.0\share\kicad\symbols\Amplifier_Operational.kicad_sym", "r", encoding="utf-8") as f:
    text = f.read()

s = text.find('(symbol "NE5532"')
print(text[s:s+2000])
