with open(r"kicad\01_Power_Supply.kicad_sch", "r", encoding="utf-8") as f:
    text = f.read()

s = text.find('(symbol "Amplifier_Operational:NE5532"')
e = text.find('\n    (symbol "', s+10)
if e == -1: e = text.find('\n  )', s)
print(text[s:e])
