import os, re

fpath = r"C:\Program Files\KiCad\9.0\share\kicad\symbols\74xx.kicad_sym"
with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

symbols = re.findall(r'\(symbol\s+"(74[^"]*06[^"]*)"', content)
print("06 symbols in 74xx:", symbols)
