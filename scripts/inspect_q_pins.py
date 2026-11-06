import re

with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    text = f.read()

for sym in ['Q_NMOS_GSD', 'Q_NMOS', 'Q_NPN_BCE', 'Q_NPN']:
    idx = text.find(f'(symbol "{sym}"')
    if idx != -1:
        end = text.find('\n\t)', idx)
        body = text[idx:end+3]
        pins = re.findall(r'\(pin\s+\w+\s+\w+.*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', body, re.DOTALL)
        print(sym, 'pins:', pins)

# Also check audio jacks
for sym in ['AudioJack3_Ground_Switch', 'AudioJack3']:
    idx = text.find(f'(symbol "{sym}"')
    if idx != -1:
        end = text.find('\n\t)', idx)
        body = text[idx:end+3]
        pins = re.findall(r'\(pin\s+\w+\s+\w+.*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', body, re.DOTALL)
        print(sym, 'pins:', pins)
