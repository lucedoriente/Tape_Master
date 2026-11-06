sch_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_path, "r", encoding="utf-8") as f:
    text = f.read()

import re

# find symbol RaspberryPi_Pico definition in lib_symbols or in instances
# let's find the symbol instantiation for U3
u3_match = re.search(r'\(symbol\s+\(lib_id\s+"[^"]+:RaspberryPi_Pico[^"]*"\)\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\)[\s\S]*?\(property\s+"Reference"\s+"U3"', text)
if u3_match:
    print("Found U3 at:", u3_match.group(1), u3_match.group(2))

# print all wires and labels that touch U3 region
x_base = float(u3_match.group(1))
y_base = float(u3_match.group(2))
print("Searching wires near", x_base, y_base)

# find all pins in lib_symbol for RaspberryPi_Pico
lib_sym_match = re.search(r'\(symbol\s+"RaspberryPi_Pico"[\s\S]*?\n  \)', text)
if lib_sym_match:
    pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(length\s+[-\d\.]+\)\s+\(name\s+"([^"]+)"\s+[^)]+\)\s+\(number\s+"([^"]+)"', lib_sym_match.group(0))
    for px, py, rot, name, num in pins:
        # absolute schematic pos
        abs_x = x_base + float(px)
        abs_y = y_base - float(py) # kicad y is inverted in symbol def
        print(f"Pin {num} ({name}): local=({px},{py}) approx sch=({abs_x:.2f}, {abs_y:.2f})")
