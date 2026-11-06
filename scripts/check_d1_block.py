sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\01_Power_Supply.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('(property "Reference" "D1"')
print(text[idx-50:idx+400])
