with open('kicad/03_Analog_Ingest.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re
wires = []
for m in re.finditer(r'\(wire\s+\(pts\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\s+\(xy\s+([-\d.]+)\s+([-\d.]+)\)\)', text):
    wires.append(((float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))))

# BFS from (121.92, 132.08)
start = (121.92, 132.08)
visited_pts = {start}
queue = [start]
net_wires = []

while queue:
    curr = queue.pop(0)
    for w in wires:
        p1, p2 = w
        if p1 == curr and p2 not in visited_pts:
            visited_pts.add(p2)
            queue.append(p2)
            net_wires.append(w)
        elif p2 == curr and p1 not in visited_pts:
            visited_pts.add(p1)
            queue.append(p1)
            net_wires.append(w)

print(f"Total points in net: {len(visited_pts)}")
print(f"Total wires in net: {len(net_wires)}")
for w in net_wires:
    print(" ", w)


