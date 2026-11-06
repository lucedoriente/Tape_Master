import re
from test_all_resolved import resolve_symbol

for sym in ["LM393", "74LS06"]:
    raw = resolve_symbol("Comparator" if sym=="LM393" else "74xx", sym)
    print(f"\nUnits in {sym}:")
    for m in re.finditer(rf'\(symbol "{sym}_(\d+)_(\d+)"', raw):
        u = m.group(1)
        v = m.group(2)
        s_idx = m.start()
        e_idx = raw.find('\n\t\t)', s_idx)
        sub = raw[s_idx:e_idx]
        pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', sub, re.DOTALL)
        print(f"  Unit {u}_{v}: {len(pins)} pins")
        for p in pins:
            print(f"     Pin {p[4]} ({p[3]}) at ({p[0]}, {p[1]}) rot {p[2]}")
