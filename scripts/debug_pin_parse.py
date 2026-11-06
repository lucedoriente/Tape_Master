import os, re

with open("kicad/Tape-Master.kicad_sym", "r", encoding="utf-8") as f:
    text = f.read()

import re

for m in re.finditer(r'\(symbol "([^"]+)"', text):
    sname_raw = m.group(1)
    if re.search(r'_\d+_\d+$', sname_raw):
        continue
    s_idx = m.start()
    nest = 0
    raw = ""
    for i in range(s_idx, len(text)):
        if text[i] == '(': nest += 1
        elif text[i] == ')':
            nest -= 1
            if nest == 0:
                raw = text[s_idx:i+1]
                break
    prefixed_raw = re.sub(r'\(symbol "(?!Tape-Master:)', '(symbol "Tape-Master:', raw)
    subs = re.findall(r'\(symbol "([^"]+)"', prefixed_raw)
    print(f"{sname_raw:30s} -> {subs[:3]}")
    break


