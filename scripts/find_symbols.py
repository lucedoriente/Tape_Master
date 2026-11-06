import os, glob

sym_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
targets = ["LM3914", "7406", "74HC06", "AP2112", "NE5532", "OPA2134", "LM393", "PC817", "AQY21"]

found = {}
for p in glob.glob(os.path.join(sym_dir, "*.kicad_sym")):
    lib_name = os.path.splitext(os.path.basename(p))[0]
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
        for t in targets:
            if t in text:
                if t not in found: found[t] = []
                found[t].append(lib_name)

for t in targets:
    print(f"{t}: {found.get(t, ['NOT FOUND'])}")
