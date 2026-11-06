with open('kicad/Tape-Master.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip existing sheet_instances if present
import re
text = re.sub(r'\s*\(sheet_instances.*?\n\s*\)', '', text, flags=re.DOTALL)

# Add complete sheet_instances to root
idx = text.rfind(')')
new_root = text[:idx] + '''  (sheet_instances
    (path "/" (page "1"))
    (path "/a1000000-0000-4000-8000-000000000001" (page "2"))
    (path "/a1000000-0000-4000-8000-000000000002" (page "3"))
    (path "/a1000000-0000-4000-8000-000000000003" (page "4"))
    (path "/a1000000-0000-4000-8000-000000000004" (page "5"))
  )
)
'''

with open('kicad/Tape-Master.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(new_root)

# Add sheet_instances to sheet 1..4
sheets = [
    ("01_Power_Supply.kicad_sch", "a1000000-0000-4000-8000-000000000001", "2"),
    ("02_MCU_Core.kicad_sch", "a1000000-0000-4000-8000-000000000002", "3"),
    ("03_Analog_Ingest.kicad_sch", "a1000000-0000-4000-8000-000000000003", "4"),
    ("04_Tape_Interfaces.kicad_sch", "a1000000-0000-4000-8000-000000000004", "5")
]

for sfile, suuid, pnum in sheets:
    with open(f'kicad/{sfile}', 'r', encoding='utf-8') as f:
        stext = f.read()
    stext = re.sub(r'\s*\(sheet_instances.*?\n\s*\)', '', stext, flags=re.DOTALL)
    sidx = stext.rfind(')')
    snew = stext[:sidx] + f'''  (sheet_instances
    (path "/{suuid}" (page "{pnum}"))
  )
)
'''
    with open(f'kicad/{sfile}', 'w', encoding='utf-8') as f:
        f.write(snew)

print("Updated sheet_instances across all files.")

