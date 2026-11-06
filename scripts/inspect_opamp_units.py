import re
from test_all_resolved import resolve_symbol

raw = resolve_symbol("Amplifier_Operational", "NE5532")

# Find units and pins in NE5532
for m in re.finditer(r'\(symbol "NE5532_(\d+)_(\d+)"', raw):
    u = m.group(1)
    v = m.group(2)
    s_idx = m.start()
    e_idx = raw.find('\n\t\t)', s_idx)
    sub = raw[s_idx:e_idx]
    pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"', sub, re.DOTALL)
    print(f"Unit {u}_{v}: {len(pins)} pins")
    for p in pins:
        print(f"   Pin {p[4]} ({p[3]}) at ({p[0]}, {p[1]}) rot {p[2]}")
