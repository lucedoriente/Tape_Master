with open(r"kicad\01_Power_Supply.kicad_sch", "r", encoding="utf-8") as f:
    text = f.read()

for line in text.splitlines():
    if "97.46" in line:
        print(line)
