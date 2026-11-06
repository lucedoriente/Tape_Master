import re, os

sym_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_sym"
with open(sym_path, "r", encoding="utf-8") as f:
    text = f.read()

symbols = re.findall(r'\(symbol\s+"([^"]+)"', text)
print("Symbols in Tape-Master.kicad_sym:", symbols)
