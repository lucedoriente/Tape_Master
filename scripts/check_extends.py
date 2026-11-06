import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"

def check_extends(lib_name, sym_name):
    path = os.path.join(symbols_dir, f"{lib_name}.kicad_sym")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    target = f'(symbol "{sym_name}"'
    s = text.find(target)
    if s == -1: return None
    end = text.find('\n  )', s)
    blk = text[s:end+4]
    m = re.search(r'\(extends "([^"]+)"\)', blk)
    return m.group(1) if m else "NO_EXTENDS"

for lib, sym in [("Amplifier_Operational", "NE5532"), ("Comparator", "LM393"), ("74xx", "74LS06"), ("Regulator_Linear", "AP2112K-3.3")]:
    ext = check_extends(lib, sym)
    print(f"{lib}:{sym} -> {ext}")
