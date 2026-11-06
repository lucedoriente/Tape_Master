import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
path = os.path.join(symbols_dir, "Amplifier_Operational.kicad_sym")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

s = text.find('(symbol "LM2904"')
nest = 0
for i in range(s, len(text)):
    if text[i] == '(': nest += 1
    elif text[i] == ')':
        nest -= 1
        if nest == 0:
            raw = text[s:i+1]
            break

for m in re.finditer(r'\(symbol "(LM2904_[^"]+)"', raw):
    subname = m.group(1)
    s_idx = m.start()
    sub_nest = 0
    for j in range(s_idx, len(raw)):
        if raw[j] == '(': sub_nest += 1
        elif raw[j] == ')':
            sub_nest -= 1
            if sub_nest == 0:
                body = raw[s_idx:j+1]
                pins = re.findall(r'\(number\s+"([^"]+)".*?\(name\s+"([^"]+)"', body, re.DOTALL)
                print(f"Sub-symbol {subname}: {pins}")
                break
