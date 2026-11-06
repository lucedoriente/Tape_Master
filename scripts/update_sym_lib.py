import os, re
sys_dir = os.path.dirname(__file__)
kicad_dir = os.path.abspath(os.path.join(sys_dir, "..", "kicad"))
sym_path = os.path.join(kicad_dir, "Tape-Master.kicad_sym")

import sys
sys.path.append(sys_dir)
from test_all_resolved import resolve_symbol

# Load existing sym_path
with open(sym_path, "r", encoding="utf-8") as f:
    text = f.read()

def get_sym_block(sym_text, sym_name):
    target = f'(symbol "{sym_name}"'
    s = sym_text.find(target)
    if s == -1: return None
    nest = 0
    for i in range(s, len(sym_text)):
        if sym_text[i] == '(': nest += 1
        elif sym_text[i] == ')':
            nest -= 1
            if nest == 0:
                return sym_text[s:i+1]
    return None

# Symbols to make sure are present in Tape-Master.kicad_sym:
needed = [
    ("Amplifier_Operational", "TLV2372"),
    ("Driver_LED", "TLC5916"),
]

new_syms = []
for orig_lib, sym_name in needed:
    if get_sym_block(text, sym_name) is None:
        raw = resolve_symbol(orig_lib, sym_name)
        if raw:
            # Replace header to local lib style
            raw_clean = raw.replace(f'(symbol "{orig_lib}:{sym_name}"', f'(symbol "{sym_name}"', 1)
            new_syms.append(raw_clean)
            print(f"Added {sym_name} to library")
        else:
            print(f"FAILED to resolve {orig_lib}:{sym_name}")
    else:
        print(f"{sym_name} already in library")

# For 74HCT06, based on 74LS06:
if get_sym_block(text, "74HCT06") is None:
    raw_ls06 = resolve_symbol("74xx", "74LS06")
    if raw_ls06:
        hct06 = raw_ls06.replace('(symbol "74xx:74LS06"', '(symbol "74HCT06"')
        hct06 = hct06.replace('"74LS06"', '"74HCT06"')
        hct06 = hct06.replace('"74LS06_', '"74HCT06_')
        hct06 = hct06.replace('Hex Inverter with Open Collector Outputs', 'High-Speed CMOS Hex Inverter with Open Collector Outputs')
        new_syms.append(hct06)
        print("Added 74HCT06 to library")
    else:
        print("FAILED to resolve 74LS06 for 74HCT06")
else:
    print("74HCT06 already in library")

if new_syms:
    # Insert before final ')'
    last_p = text.rfind(')')
    updated_text = text[:last_p] + "\n\t" + "\n\t".join(new_syms) + "\n)\n"
    with open(sym_path, "w", encoding="utf-8") as f:
        f.write(updated_text)
    print("Tape-Master.kicad_sym successfully updated!")
else:
    print("No updates needed for Tape-Master.kicad_sym")
