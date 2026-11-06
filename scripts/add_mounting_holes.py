import re

with open('C:/Program Files/KiCad/9.0/share/kicad/symbols/Mechanical.kicad_sym', 'r', encoding='utf-8') as f:
    mech_text = f.read()

m = re.search(r'\(symbol "MountingHole"\s*\(pin_names.*?\n  \)', mech_text, re.DOTALL)
if m:
    mh_sym = m.group(0)
    print("Found MountingHole symbol")
    with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
        sym_text = f.read()
    if '(symbol "MountingHole"' not in sym_text:
        # Insert before the last closing paren
        last_paren = sym_text.rfind(')')
        sym_text = sym_text[:last_paren] + "\n\t" + mh_sym + "\n)"
        with open('kicad/Tape-Master.kicad_sym', 'w', encoding='utf-8') as f:
            f.write(sym_text)
        print("Appended MountingHole to Tape-Master.kicad_sym")
    else:
        print("MountingHole already present")
