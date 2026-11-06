import re

path = r"..\IC-Test-Board\shields\Shield-03-Audio-Lab\Shield-03-Audio-Lab.kicad_sch"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'\(symbol \(lib_id "[^"]+"\)[^\)]*\(unit 2\).*?\n  \)', text, re.DOTALL)
if m:
    print(m.group(0))
