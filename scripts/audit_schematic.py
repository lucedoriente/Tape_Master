import os, re

kpath = r'C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad'

for f in ['01_Power_Supply.kicad_sch', '02_MCU_Core.kicad_sch', '03_Analog_Ingest.kicad_sch', '04_Tape_Interfaces.kicad_sch']:
    filepath = os.path.join(kpath, f)
    with open(filepath, 'r', encoding='utf-8') as s:
        text = s.read()
    print(f'=== {f} ===')
    symbols = re.findall(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(property\s+"Value"\s+"([^"]+)"', text)
    for lib_id, ref, val in symbols:
        if not ref.startswith('#'):
            print(f'  {ref:8s}: {val:20s} [{lib_id}]')
