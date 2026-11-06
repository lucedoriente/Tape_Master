sch_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\02_MCU_Core.kicad_sch"
with open(sch_file, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('58e48222-7ba4-47d6-bd84-36ace4b549b1')
if idx != -1:
    print(text[max(0, idx-300):min(len(text), idx+300)])
