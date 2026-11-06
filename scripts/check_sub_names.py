with open(r"kicad\Tape-Master.kicad_sym", "r", encoding="utf-8") as f:
    text = f.read()

import re
root_syms = []
for m in re.finditer(r'\(symbol "([^"]+)"', text):
    s = m.group(1)
    if not re.search(r'_\d+_\d+$', s):
        root_syms.append(s)
print(f"Total root symbols: {len(root_syms)}")
print(root_syms)

