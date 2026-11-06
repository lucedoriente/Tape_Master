sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\01_Power_Supply.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect D1, U1, C1 in 01_Power_Supply.kicad_sch
for target in ["D1", "U1", "C1", "F1", "J1"]:
    idx = text.find(f'(property "Reference" "{target}"')
    if idx != -1:
        start = text.rfind('(symbol', 0, idx)
        end = text.find('\n  )', idx)
        print(f"=== {target} ===")
        print(text[start:end+4])
