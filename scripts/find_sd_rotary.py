import os, glob

symbols_dir = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
for p in glob.glob(os.path.join(symbols_dir, "*.kicad_sym")):
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
        if "MicroSD" in text or "microSD" in text or "RotaryEncoder" in text:
            print("Found in", os.path.basename(p))
            for line in text.splitlines():
                if line.startswith("  (symbol "):
                    if any(k in line.lower() for k in ["microsd", "rotaryencoder"]):
                        print("  ", line.strip())
