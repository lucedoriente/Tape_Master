import os, re

scripts_dir = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts"
for f in os.listdir(scripts_dir):
    if f.endswith(".py"):
        with open(os.path.join(scripts_dir, f), "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
        if "295" in content or ("gnd" in content.lower() and "track" in content.lower()):
            print(f, "mentions GND and track")
