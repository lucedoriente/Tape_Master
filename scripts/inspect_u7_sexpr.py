with open('kicad/Tape-Master.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('(property "Reference" "U7"')
if idx != -1:
    idx2 = text.find('(pad "9"', idx)
    print(text[idx2:idx2+1200])
