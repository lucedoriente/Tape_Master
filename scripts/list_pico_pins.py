import re
from test_all_resolved import resolve_symbol

raw = resolve_symbol("MCU_Module", "RaspberryPi_Pico")
pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', raw, re.DOTALL)
for p in sorted(pins, key=lambda x: int(x[4]) if x[4].isdigit() else 99):
    print(f"Pin {p[4]:<3}: {p[3]:<16} at ({float(p[0]):>6.2f}, {float(p[1]):>6.2f}) rot {p[2]}")
