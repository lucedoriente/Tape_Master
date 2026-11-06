sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
# find pin 34 of U3
# In lib_symbols, pin 34 is GPIO28_ADC2
# Let's find wires or no_connect near pin 34 position
# U3 is at 160.02, 119.38
# Let's search all no_connect in 02_MCU_Core
ncs = re.findall(r'\(no_connect\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(uuid\s+"([^"]+)"\)\)', text)
print("No connects in MCU Core:")
for x, y, u in ncs:
    print(f"  at ({x}, {y}) uuid={u}")
