with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("(zone") or line.strip().startswith("(zone"):
            print(line[:100])
