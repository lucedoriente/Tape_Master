sym_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_sym"
with open(sym_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
idx = text.find('(symbol "RaspberryPi_Pico_1_1"')
end = text.find('\n  )', idx)
print(text[idx:end])
