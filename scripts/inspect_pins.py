import re

with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    text = f.read()

# Find RaspberryPi_Pico symbol
pico_start = text.find('(symbol "RaspberryPi_Pico"')
if pico_start != -1:
    pico_end = text.find('\n\t)', pico_start)
    pico = text[pico_start:pico_end+3]
    for pm in re.finditer(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', pico, re.DOTALL):
        pnum = pm.group(6)
        ptype = pm.group(1)
        pname = pm.group(5)
        if pnum in ['1', '2', '3', '8', '13', '18', '23', '28', '33', '38', '39', '40']:
            print(f"Pico Pin {pnum}: name={pname}, type={ptype}, at=({pm.group(2)}, {pm.group(3)})")

# Find C2N_Edge_Connector
c2n_start = text.find('(symbol "C2N_Edge_Connector"')
if c2n_start != -1:
    c2n_end = text.find('\n\t)', c2n_start)
    c2n = text[c2n_start:c2n_end+3]
    for pm in re.finditer(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', c2n, re.DOTALL):
        print(f"C2N Pin {pm.group(6)}: name={pm.group(5)}, type={pm.group(1)}")
