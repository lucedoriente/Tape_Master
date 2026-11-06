import re

with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts\build_full_production_system.py", "r", encoding="utf-8") as f:
    text = f.read()

pico_conns = re.findall(r's2\.connect_pin_stub\("U3",\s*"(\d+)",\s*"([^"]+)"', text)
for pin, net in sorted(pico_conns, key=lambda x: int(x[0])):
    print(f"Pico Pin {pin}: {net}")
