import os, re

sch_dir = r"..\FDD_Tester\kicad"
for f in os.listdir(sch_dir):
    if f.endswith(".kicad_sch"):
        path = os.path.join(sch_dir, f)
        with open(path, "r", encoding="utf-8") as fp:
            text = fp.read()
        m = re.search(r'\(symbol \(lib_id "[^"]+"\)[^\)]*\(unit 2\).*?\n  \)', text, re.DOTALL)
        if m:
            print(f"Found (unit 2) in {f}:")
            print(m.group(0)[:800])
            break
