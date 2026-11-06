import re

with open('kicad/Tape-Master.kicad_sym', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace C2N pin 1 power_out with passive
text, n1 = re.subn(
    r'(\(symbol\s+"C2N_Connector_1_1"\s*\(pin\s+)power_out(\s+line)',
    r'\1passive\2',
    text
)
print(f"C2N replacements: {n1}")

# Replace Pico pin 33 AGND power_out with passive
text, n2 = re.subn(
    r'(\(pin\s+)power_out(\s+line\s*\(at\s+22\.86\s+-22\.86\s+180\)\s*\(length\s+3\.81\)\s*\(name\s+"AGND")',
    r'\1passive\2',
    text
)
print(f"Pico AGND replacements: {n2}")

with open('kicad/Tape-Master.kicad_sym', 'w', encoding='utf-8') as f:
    f.write(text)

print('Tape-Master.kicad_sym updated successfully!')
