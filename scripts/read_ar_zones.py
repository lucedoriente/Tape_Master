with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts\auto_route_production_board.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("# 8. Add and Fill GND")
print(text[idx:])
