import subprocess, re

with open('kicad/test_flat_dir/pic_sockets.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract J1 from 01_Power_Supply.kicad_sch
with open('kicad/01_Power_Supply.kicad_sch', 'r', encoding='utf-8') as f:
    s1 = f.read()

idx = s1.find('(property "Reference" "J1"')
s = s1.rfind('(symbol', 0, idx)
e = s1.find('  )', idx)
e = s1.find('  )', e + 1)
j1_str = s1[s:e+3]

# Adapt path and project to flat_hierarchy
j1_str = j1_str.replace('"Tape-Master"', '"flat_hierarchy"')
j1_str = j1_str.replace('/a1000000-0000-4000-8000-000000000000/a1000000-0000-4000-8000-000000000001', '/3bb135b1-15ed-43fe-a7bd-da79c3cfcb8b/00000000-0000-0000-0000-000048553e7c')
# Also check lib_id: flat_hierarchy doesn't have Tape-Master:USB_C... so let's change lib_id to flat_hierarchy:CONN_1
j1_str = re.sub(r'\(lib_id "Tape-Master:[^"]+"', '(lib_id "flat_hierarchy:CONN_1"', j1_str)

# Insert before the last ) in pic_sockets.kicad_sch
with open('kicad/test_flat_dir/pic_sockets.kicad_sch', 'r', encoding='utf-8') as f:
    ps = f.read()

last_idx = ps.rfind(')')
ps_new = ps[:last_idx] + "\n" + j1_str + "\n)\n"

with open('kicad/test_flat_dir/pic_sockets.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(ps_new)

cmd = [r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe', 'sch', 'export', 'netlist', 'kicad/test_flat_dir/flat_hierarchy.kicad_sch', '-o', 'kicad/test_flat_dir/out_j1.net']
res = subprocess.run(cmd, capture_output=True, text=True)

with open('kicad/test_flat_dir/out_j1.net') as f:
    out = f.read()

comps = re.findall(r'\(comp\s+\(ref "([^"]+)"\)', out)
print("J1 in comps?", 'J1' in comps)
print("Total comps:", len(comps))

