import re

with open('kicad/01_Power_Supply.kicad_sch', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'\(symbol\s+\(lib_id "Tape-Master:R".*?\n  \)', text, re.DOTALL)
r_comp = m.group(0)

# Modify instances to root
r_comp = r_comp.replace('/a1000000-0000-4000-8000-000000000000/a1000000-0000-4000-8000-000000000001', '/a1000000-0000-4000-8000-000000000000')

with open('kicad/Tape-Master.kicad_sch', encoding='utf-8') as f:
    root = f.read()

root_with_r = root.rstrip()[:-1] + "\n" + r_comp + "\n)\n"
with open('kicad/Tape-Master.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(root_with_r)

print("Added test R to root sheet.")
