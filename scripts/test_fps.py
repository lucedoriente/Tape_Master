import pcbnew, re, os

with open('kicad/Tape-Master.net', 'r', encoding='utf-8') as f:
    text = f.read()

comps = re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)\s+\(value\s+"([^"]+)"\)\s+\(footprint\s+"([^"]+)"\)', text)
print(f'Total components: {len(comps)}')

missing = []
for ref, val, fp in comps:
    if ':' in fp:
        lib, name = fp.split(':', 1)
    else:
        lib, name = '', fp
    if lib == 'Tape-Master':
        lpath = os.path.abspath('kicad/Tape-Master.pretty')
    else:
        lpath = f'C:/Program Files/KiCad/9.0/share/kicad/footprints/{lib}.pretty'
    loaded = pcbnew.FootprintLoad(lpath, name)
    if not loaded:
        missing.append((ref, fp))

print(f'Missing footprints: {len(missing)}')
if missing:
    for m in missing:
        print('  Missing:', m)
