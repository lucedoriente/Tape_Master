import os

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
local_sym_path = os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_sym")

def extract_symbol(lib_name, sym_name):
    if lib_name == "Tape-Master":
        path = local_sym_path
    else:
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
                # Replace symbol header with library-qualified name
                header_old = f'(symbol "{sym_name}"'
                header_new = f'(symbol "{lib_name}:{sym_name}"'
                return raw.replace(header_old, header_new, 1)
    return None

required = [
    ("power", "+5V"),
    ("power", "+3V3"),
    ("power", "GND"),
    ("power", "PWR_FLAG"),
    ("Connector", "USB_C_Receptacle_USB2.0_16P"),
    ("Connector_Generic", "Conn_01x02"),
    ("Connector_Generic", "Conn_01x06"),
    ("Connector_Audio", "AudioJack3"),
    ("Connector", "Micro_SD_Card_Det1"),
    ("Device", "Polyfuse"),
    ("Device", "D_Schottky"),
    ("Device", "D_Schottky_Dual_CommonCathode_AAK"),
    ("Device", "D_Schottky_Dual_Series_ACK"),
    ("Device", "R"),
    ("Device", "R_Potentiometer"),
    ("Device", "C"),
    ("Device", "C_Polarized"),
    ("Device", "LED"),
    ("Device", "Q_NMOS"),
    ("Device", "Q_NPN"),
    ("Device", "RotaryEncoder_Switch"),
    ("Switch", "SW_Push"),
    ("Regulator_Linear", "AP2112K-3.3"),
    ("Amplifier_Operational", "NE5532"),
    ("Driver_LED", "LM3914N"),
    ("Comparator", "LM393"),
    ("74xx", "74LS06"),
    ("Isolator", "PC817"),
    ("MCU_Module", "RaspberryPi_Pico"),
    ("Tape-Master", "C2N_Connector"),
    ("Tape-Master", "OLED_0.96_I2C")
]

missing = []
for lib, sym in required:
    res = extract_symbol(lib, sym)
    if not res:
        missing.append((lib, sym))
    else:
        print(f"OK: {lib}:{sym} ({len(res)} bytes)")

if missing:
    print("FAILED on:", missing)
else:
    print("All 31 symbols extracted perfectly!")
