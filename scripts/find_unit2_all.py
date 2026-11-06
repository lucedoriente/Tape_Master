import os, re

scratch_dir = r".."
for root, dirs, files in os.walk(scratch_dir):
    for f in files:
        if f.endswith(".kicad_sch"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    text = fp.read()
                if "(unit 2)" in text:
                    print("Found in:", p)
                    m = re.search(r'\(symbol \(lib_id "[^"]+"\)[^\)]*\(unit 2\).*?\n  \)', text, re.DOTALL)
                    if m:
                        print(m.group(0)[:600])
                        exit(0)
            except Exception:
                pass
