import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"

def extract_symbol_from_lib(lib_name, sym_name):
    path = os.path.join(symbols_dir, f"{lib_name}.kicad_sym")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    target = f'(symbol "{sym_name}"'
    s = text.find(target)
    if s == -1:
        return None
    nest = 0
    for i in range(s, len(text)):
        if text[i] == '(': nest += 1
        elif text[i] == ')':
            nest -= 1
            if nest == 0:
                raw = text[s:i+1]
                return raw
    return None

targets = [
    ("power", "+5V"), ("power", "+3V3"), ("power", "GND"), ("power", "PWR_FLAG"),
    ("MCU_Module", "RaspberryPi_Pico"),
    ("Amplifier_Operational", "NE5532"),
    ("Comparator", "LM393"),
    ("Driver_LED", "LM3914"),
    ("74xx", "74LS06"),
    ("Regulator_Linear", "AP2112K-3.3"),
    ("Isolator", "PC817"),
    ("Connector", "USB_C_Receptacle_USB2.0_16P"),
    ("Connector_Generic", "Conn_01x02"),
    ("Connector_Generic", "Conn_01x04"),
    ("Connector_Generic", "Conn_01x06"),
    ("Connector_Audio", "AudioJack3"),
    ("Connector_Card", "Micro_SD_Card_Det"),
    ("Device", "R"),
    ("Device", "R_Potentiometer"),
    ("Device", "C"),
    ("Device", "C_Polarized"),
    ("Device", "LED"),
    ("Device", "D_Schottky"),
    ("Device", "D_Schottky_x2_KCom_AAK"),
    ("Device", "Q_NMOS_GSD"),
    ("Device", "Q_NPN_BCE"),
    ("Device", "Polyfuse"),
    ("Rotary_Encoder", "RotaryEncoder_Switch"),
    ("Switch", "SW_Push")
]

found = {}
missing = []
for lib, sym in targets:
    res = extract_symbol_from_lib(lib, sym)
    if res:
        found[(lib, sym)] = res
    else:
        missing.append((lib, sym))

print(f"Found {len(found)} symbols.")
if missing:
    print("Missing symbols:", missing)
else:
    print("ALL symbols found!")
