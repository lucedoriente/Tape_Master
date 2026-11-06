import pcbnew
import numpy as np
import heapq
import subprocess

board_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
test_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master-test-route.kicad_pcb"

board = pcbnew.LoadBoard(board_path)
net = board.FindNet("TAPE_FILTERED")

RES = 0.25
X_MIN, X_MAX = 30.0, 100.0
Y_MIN, Y_MAX = 15.0, 55.0
W = int((X_MAX - X_MIN) / RES)
H = int((Y_MAX - Y_MIN) / RES)

def to_grid(x, y): return int(round((x - X_MIN) / RES)), int(round((y - Y_MIN) / RES))
def to_world(gx, gy): return X_MIN + gx * RES, Y_MIN + gy * RES

CLEARANCE_MM = 0.32
VIA_CLR_MM = 0.55
VIA_CLR_PIX = int(np.ceil(VIA_CLR_MM / RES))
grid = np.zeros((2, W, H), dtype=np.uint8)

# 1. Pads
for fp in board.GetFootprints():
    for p in fp.Pads():
        pos = p.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        if X_MIN <= px <= X_MAX and Y_MIN <= py <= Y_MAX:
            if (abs(px - 95.78) < 0.8 and abs(py - 35.24) < 0.8) or (abs(px - 36.0) < 0.8 and abs(py - 44.91) < 0.8):
                continue
            gx, gy = to_grid(px, py)
            sz = max(p.GetSize().x, p.GetSize().y) / 2e6 + CLEARANCE_MM
            r_pix = int(np.ceil(sz / RES))
            for layer_idx, layer_id in enumerate([pcbnew.F_Cu, pcbnew.B_Cu]):
                if p.IsOnLayer(layer_id):
                    for dx in range(-r_pix, r_pix + 1):
                        for dy in range(-r_pix, r_pix + 1):
                            if dx*dx + dy*dy <= r_pix*r_pix:
                                nx, ny = gx + dx, gy + dy
                                if 0 <= nx < W and 0 <= ny < H: grid[layer_idx, nx, ny] = 1

# 2. Tracks & Vias
for tr in board.GetTracks():
    if tr.GetNetname() == 'TAPE_FILTERED': continue
    if isinstance(tr, pcbnew.PCB_VIA):
        pos = tr.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        if X_MIN <= px <= X_MAX and Y_MIN <= py <= Y_MAX:
            gx, gy = to_grid(px, py)
            sz = tr.GetWidth(pcbnew.F_Cu) / 2e6 + CLEARANCE_MM
            r_pix = int(np.ceil(sz / RES))
            for l in [0, 1]:
                for dx in range(-r_pix, r_pix + 1):
                    for dy in range(-r_pix, r_pix + 1):
                        if dx*dx + dy*dy <= r_pix*r_pix:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < W and 0 <= ny < H: grid[l, nx, ny] = 1
    else:
        layer_id = tr.GetLayer()
        layer_idx = 0 if layer_id == pcbnew.F_Cu else (1 if layer_id == pcbnew.B_Cu else -1)
        if layer_idx != -1:
            p1, p2 = tr.GetStart(), tr.GetEnd()
            x1, y1 = p1.x / 1e6, p1.y / 1e6
            x2, y2 = p2.x / 1e6, p2.y / 1e6
            dist = np.hypot(x2 - x1, y2 - y1)
            steps = max(1, int(dist / (RES / 2)))
            tr_r = (tr.GetWidth() / 2e6) + CLEARANCE_MM
            r_pix = int(np.ceil(tr_r / RES))
            for s in range(steps + 1):
                t = s / steps
                x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
                gx, gy = to_grid(x, y)
                for dx in range(-r_pix, r_pix + 1):
                    for dy in range(-r_pix, r_pix + 1):
                        if dx*dx + dy*dy <= r_pix*r_pix:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < W and 0 <= ny < H: grid[layer_idx, nx, ny] = 1

# Precompute via blocked mask
combined = (grid[0] > 0) | (grid[1] > 0)
via_blocked = np.zeros((W, H), dtype=bool)
r_via = int(np.ceil(VIA_CLR_MM / RES))
for dx in range(-r_via, r_via + 1):
    for dy in range(-r_via, r_via + 1):
        if dx*dx + dy*dy <= r_via*r_via:
            src_x_min = max(0, -dx)
            src_x_max = min(W, W - dx)
            src_y_min = max(0, -dy)
            src_y_max = min(H, H - dy)
            dst_x_min = max(0, dx)
            dst_x_max = min(W, W + dx)
            dst_y_min = max(0, dy)
            dst_y_max = min(H, H + dy)
            via_blocked[dst_x_min:dst_x_max, dst_y_min:dst_y_max] |= combined[src_x_min:src_x_max, src_y_min:src_y_max]

start_gx, start_gy = to_grid(95.78, 35.24)
goal_gx, goal_gy = to_grid(36.0, 44.91)

pq = [(0, 0, start_gx, start_gy), (0, 1, start_gx, start_gy)]
costs = {(0, start_gx, start_gy): 0, (1, start_gx, start_gy): 0}
parent = {}
via_cost = 60.0
found_state = None

while pq:
    cost, l, cx, cy = heapq.heappop(pq)
    if l == 0 and cx == goal_gx and cy == goal_gy:
        found_state = (l, cx, cy)
        break
    if cost > costs.get((l, cx, cy), float('inf')): continue
    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < W and 0 <= ny < H and grid[l, nx, ny] == 0:
            step_cost = 1.414 if (dx != 0 and dy != 0) else 1.0
            nc = cost + step_cost
            if nc < costs.get((l, nx, ny), float('inf')):
                costs[(l, nx, ny)] = nc
                parent[(l, nx, ny)] = (l, cx, cy)
                heapq.heappush(pq, (nc, l, nx, ny))
    nl = 1 - l
    if not via_blocked[cx, cy]:
        nc = cost + via_cost
        if nc < costs.get((nl, cx, cy), float('inf')):
            costs[(nl, cx, cy)] = nc
            parent[(nl, cx, cy)] = (l, cx, cy)
            heapq.heappush(pq, (nc, nl, cx, cy))

if not found_state:
    print("ERROR: No path found!")
    exit(1)

curr = found_state
raw_path = []
while curr in parent:
    raw_path.append(curr)
    curr = parent[curr]
raw_path.append(curr)
raw_path.reverse()

# Reconstruct into segments and vias
segments = [] # list of (layer, (x1, y1), (x2, y2))
vias = [] # list of (x, y)

# Connect start pad precisely
actual_start = (raw_path[0][0], 95.78, 35.24)
p0 = (raw_path[0][0], *to_world(raw_path[0][1], raw_path[0][2]))
if np.hypot(actual_start[1] - p0[1], actual_start[2] - p0[2]) > 1e-4:
    segments.append((actual_start[0], (actual_start[1], actual_start[2]), (p0[1], p0[2])))

i = 0
while i < len(raw_path) - 1:
    l1, gx1, gy1 = raw_path[i]
    l2, gx2, gy2 = raw_path[i+1]
    if l1 != l2:
        wx, wy = to_world(gx1, gy1)
        vias.append((wx, wy))
        i += 1
    else:
        # Extend line as long as direction is constant and on same layer
        dx = gx2 - gx1
        dy = gy2 - gy1
        j = i + 1
        while j < len(raw_path) - 1:
            next_l, next_gx, next_gy = raw_path[j+1]
            if next_l == l1 and (next_gx - raw_path[j][1]) == dx and (next_gy - raw_path[j][2]) == dy:
                j += 1
            else:
                break
        wx1, wy1 = to_world(gx1, gy1)
        wx2, wy2 = to_world(raw_path[j][1], raw_path[j][2])
        segments.append((l1, (wx1, wy1), (wx2, wy2)))
        i = j

# Connect last point to exact R34 pad 1 (36.00, 44.9125)
actual_end = (0, 36.00, 44.9125)
last_pt = (segments[-1][0], segments[-1][2][0], segments[-1][2][1])
if np.hypot(last_pt[1] - actual_end[1], last_pt[2] - actual_end[2]) > 1e-4:
    segments.append((0, (last_pt[1], last_pt[2]), (actual_end[1], actual_end[2])))

print(f"Generated {len(segments)} segments and {len(vias)} vias.")

for s in segments:
    layer_id = pcbnew.F_Cu if s[0] == 0 else pcbnew.B_Cu
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(int(round(s[1][0] * 1e6)), int(round(s[1][1] * 1e6))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(s[2][0] * 1e6)), int(round(s[2][1] * 1e6))))
    t.SetWidth(int(round(0.25 * 1e6)))
    t.SetLayer(layer_id)
    t.SetNet(net)
    board.Add(t)

for v in vias:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(int(round(v[0] * 1e6)), int(round(v[1] * 1e6))))
    via.SetWidth(int(round(0.6 * 1e6)))
    via.SetDrill(int(round(0.3 * 1e6)))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetNet(net)
    board.Add(via)

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(test_path)
print("Saved test board to:", test_path)
