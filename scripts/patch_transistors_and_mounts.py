import re

# 1. Update Tape-Master.kicad_sym for Q_NMOS and Q_NPN
with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    text = f.read()

# Update Q_NMOS
# G -> 1, S -> 2, D -> 3
q_nmos_block = re.search(r'\(symbol "Q_NMOS".*?\n\t\)', text, re.DOTALL)
if q_nmos_block:
    old_b = q_nmos_block.group(0)
    new_b = old_b
    # Replace (name "G" ... (number "G" -> (number "1"
    new_b = re.sub(r'\(name "G"(.*?)\(number "G"', r'(name "G"\1(number "1"', new_b, flags=re.DOTALL)
    # Replace (name "S" ... (number "S" -> (number "2"
    new_b = re.sub(r'\(name "S"(.*?)\(number "S"', r'(name "S"\1(number "2"', new_b, flags=re.DOTALL)
    # Replace (name "D" ... (number "D" -> (number "3"
    new_b = re.sub(r'\(name "D"(.*?)\(number "D"', r'(name "D"\1(number "3"', new_b, flags=re.DOTALL)
    text = text.replace(old_b, new_b)
    print("Updated Q_NMOS in sym lib")

# Update Q_NPN
# B -> 1, E -> 2, C -> 3
q_npn_block = re.search(r'\(symbol "Q_NPN".*?\n\t\)', text, re.DOTALL)
if q_npn_block:
    old_b = q_npn_block.group(0)
    new_b = old_b
    new_b = re.sub(r'\(name "B"(.*?)\(number "B"', r'(name "B"\1(number "1"', new_b, flags=re.DOTALL)
    new_b = re.sub(r'\(name "E"(.*?)\(number "E"', r'(name "E"\1(number "2"', new_b, flags=re.DOTALL)
    new_b = re.sub(r'\(name "C"(.*?)\(number "C"', r'(name "C"\1(number "3"', new_b, flags=re.DOTALL)
    text = text.replace(old_b, new_b)
    print("Updated Q_NPN in sym lib")

with open('kicad/Tape-Master.kicad_sym', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved Tape-Master.kicad_sym")
