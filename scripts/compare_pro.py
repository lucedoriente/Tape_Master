import json

with open(r'C:\Program Files\KiCad\9.0\share\kicad\demos\flat_hierarchy\flat_hierarchy.kicad_pro') as f:
    demo_pro = json.load(f)

with open('kicad/Tape-Master.kicad_pro') as f:
    our_pro = json.load(f)

print("Demo top keys:", list(demo_pro.keys()))
print("Our top keys:", list(our_pro.keys()))

print("\nDemo schematic:", demo_pro.get("schematic"))
print("Our schematic:", our_pro.get("schematic"))

print("\nDemo sheets:", demo_pro.get("sheets"))
print("Our sheets:", our_pro.get("sheets"))
