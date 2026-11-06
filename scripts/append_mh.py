with open('C:/Program Files/KiCad/9.0/share/kicad/symbols/Mechanical.kicad_sym', 'r', encoding='utf-8') as f:
    lines = f.readlines()

mh_lines = lines[1483:1566]
mh_text = ''.join(mh_lines)

with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    sym_text = f.read()

if '(symbol "MountingHole"' not in sym_text:
    last_paren = sym_text.rfind(')')
    sym_text = sym_text[:last_paren] + '\n\t' + mh_text + '\n)'
    with open('kicad/Tape-Master.kicad_sym', 'w', encoding='utf-8') as f:
        f.write(sym_text)
    print('Added MountingHole to Tape-Master.kicad_sym')
else:
    print('MountingHole already in Tape-Master.kicad_sym')
