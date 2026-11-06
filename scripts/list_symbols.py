import os, re

sym_file = r'C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_sym'
with open(sym_file, 'r', encoding='utf-8') as f:
    text = f.read()

symbols = re.findall(r'\(symbol\s+"([^"]+)"', text)
print('Symbols in Tape-Master.kicad_sym:', len(symbols))
top_level = [s for s in symbols if ':' not in s and not s.endswith('_1_1')]
for s in sorted(list(set(top_level))):
    print(' ', s)
