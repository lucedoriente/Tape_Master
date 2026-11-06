import os, shutil, subprocess, re

os.makedirs('kicad/test_single', exist_ok=True)
shutil.copy('kicad/sym-lib-table', 'kicad/test_single/sym-lib-table')
shutil.copy('kicad/Tape-Master.kicad_sym', 'kicad/test_single/Tape-Master.kicad_sym')

# Read 01_Power_Supply.kicad_sch
with open('kicad/01_Power_Supply.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace sheet path with root path / in instances
text = re.sub(r'\(path "/a1000000-0000-4000-8000-000000000000/a1000000-0000-4000-8000-000000000001"', '(path "/"', text)
text = text.replace('"Tape-Master"', '"test_single"')

# Add sheet_instances at end: (sheet_instances (path "/" (page "1")))
text = re.sub(r'\s*\(sheet_instances.*?\n\s*\)', '', text, flags=re.DOTALL)
last_idx = text.rfind(')')
text = text[:last_idx] + '  (sheet_instances\n    (path "/" (page "1"))\n  )\n)\n'

with open('kicad/test_single/test_single.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(text)

# Minimal kicad_pro
pro_text = '''{
  "meta": { "filename": "test_single.kicad_pro", "version": 3 },
  "sheets": [ ["a1000000-0000-4000-8000-000000000001", ""] ]
}'''
with open('kicad/test_single/test_single.kicad_pro', 'w', encoding='utf-8') as f:
    f.write(pro_text)

cmd = [r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', 'kicad/test_single/test_single.kicad_sch', '-o', 'kicad/test_single/out.net']
res = subprocess.run(cmd, capture_output=True, text=True)
print("Single sheet netlist export exit code:", res.returncode)
print("stdout:", res.stdout)
print("stderr:", res.stderr)

with open('kicad/test_single/out.net') as f:
    out = f.read()

comps = re.findall(r'\(comp\s+\(ref "([^"]+)"\)', out)
print("Components count in single sheet:", len(comps))
if comps:
    print("Sample components:", comps[:15])
