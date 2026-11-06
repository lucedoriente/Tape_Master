import os, re
from test_all_resolved import resolve_symbol

symbols_to_check = [
    ("power", "+5V"), ("power", "+3V3"), ("power", "GND"), ("power", "PWR_FLAG"),
    ("Device", "R"), ("Device", "C"), ("Device", "C_Polarized"),
    ("Device", "D_Schottky"), ("Device", "LED"), ("Switch", "SW_Push"),
    ("Connector_Generic", "Conn_01x02"), ("Connector_Generic", "Conn_01x06"),
    ("Tape-Master", "C2N_Connector"), ("Tape-Master", "OLED_0.96_I2C"),
    ("Regulator_Linear", "AP2112K-3.3"),
    ("Amplifier_Operational", "NE5532"),
    ("Comparator", "LM393"),
    ("74xx", "74LS06"),
    ("Isolator", "PC817"),
    ("Connector", "USB_C_Receptacle_USB2.0_16P"),
    ("Connector", "Micro_SD_Card_Det1"),
    ("Connector_Audio", "AudioJack3"),
    ("MCU_Module", "RaspberryPi_Pico"),
    ("Driver_LED", "LM3914N")
]

for lib, sym in symbols_to_check:
    raw = resolve_symbol(lib, sym)
    print(f"\n=================== {lib}:{sym} ===================")
    # Find all pin definitions: (pin <type> <shape> (at <x> <y> <rot>) ... (name "<name>") (number "<num>"))
    pins = []
    # Match pin blocks
    for m in re.finditer(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', raw):
        ptype = m.group(1)
        x = float(m.group(2))
        y = float(m.group(3))
        rot = float(m.group(4))
        # Find number and name after this match
        sub = raw[m.end():m.end()+300]
        num_m = re.search(r'\(number\s+"([^"]+)"', sub)
        name_m = re.search(r'\(name\s+"([^"]+)"', sub)
        num = num_m.group(1) if num_m else "?"
        name = name_m.group(1) if name_m else "?"
        pins.append((num, name, ptype, x, y, rot))
    for p in pins[:12]:
        print(f"  Pin {p[0]:<4} {p[1]:<16} {p[2]:<12} at ({p[3]:>6.2f}, {p[4]:>6.2f}) rot {p[5]}")
    if len(pins) > 12:
        print(f"  ... and {len(pins) - 12} more pins (total {len(pins)})")
