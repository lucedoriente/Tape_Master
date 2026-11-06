sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\03_Analog_Ingest.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('87.63 139.70')
print(text[idx-50:idx+250])
