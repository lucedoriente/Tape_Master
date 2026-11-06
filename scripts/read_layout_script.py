with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\scripts\build_pcb_layout_120x90.py", "r", encoding="utf-8") as f:
    text = f.read()

print("Length:", len(text))
for line in text.splitlines()[:50]:
    print(line)
