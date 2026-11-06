with open(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.dsn", "r", encoding="utf-8") as f:
    text = f.read()

import re
protects = re.findall(r'\(protect\b[^\)]*\)', text)
print("Protect tags:", len(protects))
if protects:
    print(protects[:5])
