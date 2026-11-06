import subprocess, re

with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('(symbol "+3V3"')
nest = 0
idx_end = -1
for i in range(idx, len(text)):
    if text[i] == '(': nest += 1
    elif text[i] == ')':
        nest -= 1
        if nest == 0:
            idx_end = i + 1
            break
raw = text[idx:idx_end]

# Replace ONLY the first (symbol "+3V3" with (symbol "Tape-Master:+3V3"
# Keep sub-symbols as (symbol "+3V3_0_1" etc!
raw_fixed = raw.replace('(symbol "+3V3"', '(symbol "Tape-Master:+3V3"', 1)

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
    f.write(header + raw_fixed + footer)

res = subprocess.run([r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'erc', 'kicad/test_single/test_single.kicad_sch'], capture_output=True, text=True)
print("With ONLY root symbol prefixed exit code:", res.returncode)
print("stdout:", res.stdout)
print("stderr:", res.stderr)
