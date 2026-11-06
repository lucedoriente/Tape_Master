import re

path = r"..\IC-Test-Board\shields\Shield-03-Audio-Lab\Shield-03-Audio-Lab.kicad_sch"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

for m in re.finditer(r'\(unit\s+2\)', text):
    s = text.rfind('(symbol ', 0, m.start())
    e = text.find('\n  )', m.start())
    print(text[s:e+4])
    break
