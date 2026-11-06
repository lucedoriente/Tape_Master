import os, re

sch_dir = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad"
for f in ["01_Power_Supply.kicad_sch", "02_MCU_Core.kicad_sch", "03_Analog_Ingest.kicad_sch", "04_Tape_Interfaces.kicad_sch"]:
    path = os.path.join(sch_dir, f)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # find ICs
    ics = re.findall(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(property\s+"Value"\s+"([^"]+)"', content)
    print(f"=== {f} ===")
    for lib, ref, val in ics:
        if ref.startswith("U") or ref.startswith("Q") or ref.startswith("D") or ref.startswith("RV"):
            print(f"  {ref}: {val} ({lib})")
