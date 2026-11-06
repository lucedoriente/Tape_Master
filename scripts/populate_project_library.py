import os
from test_all_resolved import resolve_symbol

kicad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
sym_path = os.path.join(kicad_dir, "Tape-Master.kicad_sym")

# Read current local syms (C2N_Connector and OLED_0.96_I2C)
with open(sym_path, "r", encoding="utf-8") as f:
    local_text = f.read()

def extract_from_local(sym_name):
    target = f'(symbol "{sym_name}"'
    s = local_text.find(target)
    if s == -1: return None
    nest = 0
    for i in range(s, len(local_text)):
        if local_text[i] == '(': nest += 1
        elif local_text[i] == ')':
            nest -= 1
            if nest == 0:
                return local_text[s:i+1]
    return None

c2n_raw = extract_from_local("C2N_Connector")
oled_raw = extract_from_local("OLED_0.96_I2C")

symbols_to_embed = [
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
    ("MCU_Module", "RaspberryPi_Pico")
]

embedded_syms = [c2n_raw, oled_raw]
for orig_lib, sym_name in symbols_to_embed:
    raw = resolve_symbol(orig_lib, sym_name)
    if raw:
        header_old = f'(symbol "{orig_lib}:{sym_name}"'
        header_new = f'(symbol "{sym_name}"'
        raw = raw.replace(header_old, header_new, 1)
        embedded_syms.append(raw)

syms_joined = "\n".join(embedded_syms)
full_lib = f"""(kicad_symbol_lib
	(version 20241209)
	(generator "kicad_symbol_editor")
	(generator_version "9.0")
{syms_joined}
)
"""

with open(sym_path, "w", encoding="utf-8") as f:
    f.write(full_lib)

print(f"Correctly populated {sym_path} with {len(embedded_syms)} native project symbols.")
