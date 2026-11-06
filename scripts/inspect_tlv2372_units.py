import re, sys
sys.path.append(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts")
from test_all_resolved import resolve_symbol

raw = resolve_symbol("Amplifier_Operational", "TLV2372")
units = re.findall(r'\(symbol "TLV2372_(\d+)_(\d+)"(.*?)\)\n\t\t\)', raw, re.DOTALL)
for u1, u2, body in units:
    print(f"--- Unit {u1}_{u2} ---")
    pins = re.findall(r'\(pin\s+(\w+)\s+\w+.*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', body, re.DOTALL)
    for ptype, pname, pnum in pins:
        print(f"  Pin {pnum}: {pname} ({ptype})")
