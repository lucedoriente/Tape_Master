import os, glob, re

kicad_sym_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"

targets = ["TLV2372", "74HCT06", "74HC595", "TLC5916", "TLC5925", "TLC5940"]

for fname in os.listdir(kicad_sym_dir):
    if not fname.endswith(".kicad_sym"):
        continue
    fpath = os.path.join(kicad_sym_dir, fname)
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    for t in targets:
        if re.search(r'\(symbol\s+"' + t + r'["_]', content):
            print(f"Found {t} in {fname}")
