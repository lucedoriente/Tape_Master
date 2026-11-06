import re
from test_all_resolved import resolve_symbol

raw = resolve_symbol("MCU_Module", "RaspberryPi_Pico")
for m in re.finditer(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', raw, re.DOTALL):
    if m.group(6) in ["33", "36", "38", "39", "40", "3", "8", "13", "18", "23", "28"]:
        print(f"Pin {m.group(6)} ({m.group(5)}): {m.group(1)}")
