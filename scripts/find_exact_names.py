import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"

def search_lib(lib_name, pattern):
    path = os.path.join(symbols_dir, f"{lib_name}.kicad_sym")
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return re.findall(rf'\(symbol "([^\"]*{pattern}[^\"]*)"', text, re.IGNORECASE)

print("LM3914 in Driver_LED:", search_lib("Driver_LED", "3914"))
print("Micro_SD in Connector_Card:", search_lib("Connector_Card", "SD"))
print("Schottky dual in Device:", search_lib("Device", "Schottky"))
print("NMOS in Device:", search_lib("Device", "NMOS"))
print("NPN in Device:", search_lib("Device", "NPN"))
print("Rotary in Rotary_Encoder:", search_lib("Rotary_Encoder", "Rotary"))
