sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
idx = text.find('(symbol "RaspberryPi_Pico"')
end = text.find('\n  )', idx)
pico_sym = text[idx:end]
for line in pico_sym.splitlines():
    if any(f'"{i}"' in line for i in [31, 32, 33, 34, 35, 36, 37, 38, 39, 40]):
        print(line)
