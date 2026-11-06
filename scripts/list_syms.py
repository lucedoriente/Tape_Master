sym_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_sym"
with open(sym_file, "r", encoding="utf-8") as f:
    text = f.read()

import re
sym_names = re.findall(r'\(symbol\s+"([^"]+)"', text)
print("Symbols in Tape-Master.kicad_sym:")
for s in sym_names:
    print(" ", s)
