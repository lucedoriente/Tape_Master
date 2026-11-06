import os, re

def check(lib, pattern):
    with open(os.path.join(r"C:\Program Files\KiCad\9.0\share\kicad\symbols", lib), "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return re.findall(rf'\(symbol "([^\"]*{pattern}[^\"]*)"', text, re.IGNORECASE)

print("Connector MicroSD:", check("Connector.kicad_sym", "micro_sd"))
print("Device Rotary:", check("Device.kicad_sym", "rotary"))
