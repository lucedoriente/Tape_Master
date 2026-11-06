import subprocess, re

with open('kicad/test_single/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    sym_text = f.read()

from production_sch_builder import symbols_raw

header = '''(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "a1000000-0000-4000-8000-000000000001")
  (paper "A3")
  (lib_symbols
'''

footer = '''  )
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''

for sname, sraw in sorted(symbols_raw.items()):
    content = header + sraw + footer
    with open('kicad/test_single/test_single.kicad_sch', 'w', encoding='utf-8') as f:
        f.write(content)
    res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/test_single/test_single.kicad_sch'], capture_output=True, text=True)
    ok = (res.returncode == 0 or "violations" in res.stdout)
    if not ok:
        print(f"FAILED on symbol: {sname}")
    else:
        print(f"OK: {sname}")
