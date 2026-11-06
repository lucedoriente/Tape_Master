import re

with open('kicad/Tape-Master.net', encoding='utf-8') as f:
    text = f.read()

comps = re.findall(r'\(comp\s+\(ref "([^"]+)"\)', text)
print(f"Total components in Tape-Master.net: {len(comps)}")
print("Components:", sorted(comps))

nets = re.findall(r'\(net\s+\(code\s+"\d+"\)\s+\(name\s+"([^"]+)"\)', text)
print(f"Total nets in Tape-Master.net: {len(nets)}")
print("Sample nets:", nets[:20])
