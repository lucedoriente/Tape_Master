with open(r'C:\Program Files\KiCad\9.0\share\kicad\demos\flat_hierarchy\flat_hierarchy.kicad_sch') as f:
    flat = f.read()

with open('kicad/Tape-Master.kicad_sch') as f:
    ours = f.read()

print("--- Flat hierarchy root ---")
print(flat[:800])
print("\n--- Our root ---")
print(ours[:800])
