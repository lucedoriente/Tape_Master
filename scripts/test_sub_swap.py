import subprocess, re

# In flat_hierarchy.kicad_sch, replace "pic_programmer.kicad_sch" with "../../01_Power_Supply.kicad_sch"
with open('kicad/test_flat_dir/flat_hierarchy.kicad_sch', 'r') as f:
    text = f.read()

# Let's replace the uuid of the sheet with our s1_uuid and file with 01_Power_Supply.kicad_sch
# What if we just copy 01_Power_Supply.kicad_sch to test_flat_dir/pic_programmer.kicad_sch?
import shutil
shutil.copy('kicad/01_Power_Supply.kicad_sch', 'kicad/test_flat_dir/pic_programmer.kicad_sch')

with open('kicad/test_flat_dir/pic_programmer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace project and path
text = text.replace('"Tape-Master"', '"flat_hierarchy"')
text = text.replace('/a1000000-0000-4000-8000-000000000000/a1000000-0000-4000-8000-000000000001', '/3bb135b1-15ed-43fe-a7bd-da79c3cfcb8b/00000000-0000-0000-0000-000048553e53')

with open('kicad/test_flat_dir/pic_programmer.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(text)

cmd = [r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', 'kicad/test_flat_dir/flat_hierarchy.kicad_sch', '-o', 'kicad/test_flat_dir/out3.net']
res = subprocess.run(cmd, capture_output=True, text=True)

with open('kicad/test_flat_dir/out3.net') as f:
    t3 = f.read()

comps = re.findall(r'\(comp\s+\(ref "([^"]+)"\)', t3)
print('Components count after replacing project & path:', len(comps))
print('Comps:', sorted(comps))

