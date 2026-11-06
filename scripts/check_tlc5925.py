import os, re

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
path = os.path.join(symbols_dir, "Driver_LED.kicad_sym")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = '(symbol "TLC5925"'
s = text.find(target)
print("TLC5925 in Driver_LED?", s != -1)
if s != -1:
    print(text[s:s+500])
