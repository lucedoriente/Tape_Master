import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
path = os.path.join(symbols_dir, "Driver_LED.kicad_sym")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = '(symbol "TLC5916"'
s = text.find(target)
if s != -1:
    nest = 0
    for i in range(s, len(text)):
        if text[i] == '(': nest += 1
        elif text[i] == ')':
            nest -= 1
            if nest == 0:
                print(text[s:i+1][:1500])
                break
