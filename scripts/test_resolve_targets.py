import os, sys
sys.path.append(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts")
from test_all_resolved import resolve_symbol

for lib, sym in [("Amplifier_Operational", "TLV2372"), ("Driver_LED", "TLC5916"), ("74xx", "74LS06")]:
    raw = resolve_symbol(lib, sym)
    print(f"Resolve {lib}:{sym}: len = {len(raw) if raw else 'None'}")
