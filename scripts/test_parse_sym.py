import subprocess, sys
sys.path.append('scripts')
from production_sch_builder import symbols_raw

raw = symbols_raw['Tape-Master:+3V3']
# Strip escaped quotes
raw_clean = raw.replace('\\"', "'")

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

with open('kicad/test_single/test_single.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(header + raw_clean + footer)

res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/test_single/test_single.kicad_sch'], capture_output=True, text=True)
print("With cleaned quotes exit code:", res.returncode)
print("stdout:", res.stdout)
print("stderr:", res.stderr)
