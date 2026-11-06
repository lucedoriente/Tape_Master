with open('kicad/Tape-Master.net', 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

import re
parts = text.split('(comp (ref "')[1:]
comps = {}
for part in parts:
    ref = part.split('"')[0]
    val_m = re.search(r'\(value\s+"([^"]*)"\)', part)
    val = val_m.group(1) if val_m else ""
    fp_m = re.search(r'\(footprint\s+"([^"]*)"\)', part)
    fp = fp_m.group(1) if fp_m else ""
    sp_m = re.search(r'\(sheetpath.*?\(tstamps\s+"([^"]+)"\)', part, re.DOTALL)
    sp = sp_m.group(1) if sp_m else ""
    ts_m = re.search(r'\(tstamps\s+"([0-9a-fA-F-]+)"\)', part)
    ts = ts_m.group(1) if ts_m else ""
    full_path = f"/a1000000-0000-4000-8000-000000000000{sp}{ts}"
    comps[ref] = {"val": val, "fp": fp, "path": full_path}

print(f"Total physical components: {len(comps)}")
print("Sample comp:", list(comps.items())[0])
