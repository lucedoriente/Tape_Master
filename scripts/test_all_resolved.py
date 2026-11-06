import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
local_sym_path = os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_sym")

def get_symbol_raw(lib_name, sym_name):
    if lib_name == "Tape-Master":
        path = local_sym_path
    else:
        path = os.path.join(symbols_dir, f"{lib_name}.kicad_sym")
    if not os.path.exists(path): return None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    target = f'(symbol "{sym_name}"'
    s = text.find(target)
    if s == -1: return None
    nest = 0
    for i in range(s, len(text)):
        if text[i] == '(': nest += 1
        elif text[i] == ')':
            nest -= 1
            if nest == 0:
                return text[s:i+1]
    return None

def resolve_symbol(lib_name, sym_name):
    raw = get_symbol_raw(lib_name, sym_name)
    if not raw: return None
    m = re.search(r'\(extends "([^"]+)"\)', raw)
    if not m:
        return raw.replace(f'(symbol "{sym_name}"', f'(symbol "{lib_name}:{sym_name}"', 1)
    
    parent_name = m.group(1)
    parent_raw = get_symbol_raw(lib_name, parent_name)
    if not parent_raw:
        return raw
    
    sub_syms = []
    for sub in re.finditer(rf'\(symbol "{parent_name}_([^"]+)"', parent_raw):
        s_idx = sub.start()
        nest = 0
        for i in range(s_idx, len(parent_raw)):
            if parent_raw[i] == '(': nest += 1
            elif parent_raw[i] == ')':
                nest -= 1
                if nest == 0:
                    sub_body = parent_raw[s_idx:i+1]
                    sub_body_renamed = sub_body.replace(f'(symbol "{parent_name}_', f'(symbol "{sym_name}_')
                    sub_syms.append(sub_body_renamed)
                    break
    
    cleaned = re.sub(r'\s*\(extends "[^"]+"\)', '', raw)
    last_paren = cleaned.rfind(')')
    full = cleaned[:last_paren] + "\n\t\t" + "\n\t\t".join(sub_syms) + "\n\t)"
    return full.replace(f'(symbol "{sym_name}"', f'(symbol "{lib_name}:{sym_name}"', 1)

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

for lib, sym in required:
    res = resolve_symbol(lib, sym)
    has_ext = "(extends" in res if res else "NONE"
    print(f"{lib}:{sym} -> len={len(res) if res else 0}, extends={has_ext}")
