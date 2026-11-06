import math, re
from test_all_resolved import resolve_symbol

def parse_symbol_pins(raw):
    # Map unit -> {pin_num: (x, y, rot)}
    units = {}
    # First check default unit (unit 0 or unnumbered)
    for m in re.finditer(r'\(symbol "([^"]+)"', raw):
        sname = m.group(1)
        s_idx = m.start()
        # Find matching closing paren
        nest = 0
        for i in range(s_idx, len(raw)):
            if raw[i] == '(': nest += 1
            elif raw[i] == ')':
                nest -= 1
                if nest == 0:
                    sub = raw[s_idx:i+1]
                    break
        parts = sname.split('_')
        # Check if ends with _unit_variant e.g. NE5532_1_1
        unit = 0
        if len(parts) >= 2 and parts[-2].isdigit():
            unit = int(parts[-2])
        if unit not in units: units[unit] = {}
        for pm in re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(number\s+"([^"]+)"', sub, re.DOTALL):
            px = float(pm.group(1))
            py = float(pm.group(2))
            prot = float(pm.group(3))
            pnum = pm.group(4)
            units[unit][pnum] = (px, py, prot)
    return units

# Transformation for KiCad schematic placement:
# Symbol coordinate system: X right, Y up
# Schematic coordinate system: X right, Y down
# When placed at (sx, sy) with angle rot (degrees counterclockwise):
# Cartesian:
# x' = px * cos(rot) - py * sin(rot)
# y' = px * sin(rot) + py * cos(rot)
# Schematic:
# X = sx + x'
# Y = sy - y'

def transform_pin(px, py, sx, sy, rot):
    rad = math.radians(rot)
    cos_a = round(math.cos(rad), 4)
    sin_a = round(math.sin(rad), 4)
    x_prime = px * cos_a - py * sin_a
    y_prime = px * sin_a + py * cos_a
    sch_x = round(sx + x_prime, 2)
    sch_y = round(sy - y_prime, 2)
    return (sch_x, sch_y)

# Let's test with J1 Pin A4 (px=15.24, py=15.24, sx=40, sy=60, rot=0)
print("J1 Pin A4:", transform_pin(15.24, 15.24, 40.0, 60.0, 0)) # Should be (55.24, 44.76)
# J1 Pin S1 (px=-7.62, py=-22.86, sx=40, sy=60, rot=0)
print("J1 Pin S1:", transform_pin(-7.62, -22.86, 40.0, 60.0, 0)) # Should be (32.38, 82.86)
# R1 Pin 1 (px=0, py=3.81, sx=65, sy=70.16, rot=90)
print("R1 Pin 1:", transform_pin(0, 3.81, 65.0, 70.16, 90)) # Should be (61.19, 70.16)
