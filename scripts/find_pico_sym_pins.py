import re

sym_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_sym"
with open(sym_file, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('(symbol "RaspberryPi_Pico"')
if idx != -1:
    end = text.find('\n  (symbol ', idx + 10)
    if end == -1: end = text.rfind('\n)')
    sym_def = text[idx:end]
    pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(length\s+[-\d\.]+\)\s+\(name\s+"([^"]+)"\s+[^)]+\)\s+\(number\s+"([^"]+)"', sym_def)
    print("RaspberryPi_Pico Pins:")
    for px, py, rot, name, num in pins:
        print(f"  Pin {num:2s}: {name:20s} at ({px:6s}, {py:6s})")
