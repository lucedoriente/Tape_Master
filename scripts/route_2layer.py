import pcbnew
import numpy as np
import heapq

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

# Grid resolution: 0.25 mm
RES = 0.25 # mm
X_MIN, X_MAX = 30.0, 100.0
Y_MIN, Y_MAX = 15.0, 55.0

W = int((X_MAX - X_MIN) / RES)
H = int((Y_MAX - Y_MIN) / RES)

def to_grid(x, y):
    return int((x - X_MIN) / RES), int((y - Y_MIN) / RES)

def to_world(gx, gy):
    return X_MIN + gx * RES, Y_MIN + gy * RES

# Clearance: 0.25 mm
CLEARANCE_MM = 0.25

# 2 layers: layer 0 = F.Cu, layer 1 = B.Cu
grid = np.zeros((2, W, H), dtype=np.uint8)

# Populate obstacles from pads
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
                                if 0 <= nx < W and 0 <= ny < H:
                                    grid[layer_idx, nx, ny] = 1

# Populate obstacles from tracks & vias
for tr in board.GetTracks():
    if tr.GetNetname() == "TAPE_FILTERED":
        continue
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
                            if 0 <= nx < W and 0 <= ny < H:
                                grid[l, nx, ny] = 1
    else:
        layer_id = tr.GetLayer()
        layer_idx = 0 if layer_id == pcbnew.F_Cu else (1 if layer_id == pcbnew.B_Cu else -1)
        if layer_idx != -1:
            p1 = tr.GetStart()
            p2 = tr.GetEnd()
            x1, y1 = p1.x / 1e6, p1.y / 1e6
            x2, y2 = p2.x / 1e6, p2.y / 1e6
            dist = np.hypot(x2 - x1, y2 - y1)
            steps = max(1, int(dist / (RES / 2)))
            tr_r = (tr.GetWidth() / 2e6) + CLEARANCE_MM
            r_pix = int(np.ceil(tr_r / RES))
        for s in range(steps + 1):
            t = s / steps
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            gx, gy = to_grid(x, y)
            for dx in range(-r_pix, r_pix + 1):
                for dy in range(-r_pix, r_pix + 1):
                    if dx*dx + dy*dy <= r_pix*r_pix:
                        nx, ny = gx + dx, gy + dy
                        if 0 <= nx < W and 0 <= ny < H:
                            grid[layer_idx, nx, ny] = 1

print(f"2-layer grid: {W}x{H}x2. Obstacles F: {np.sum(grid[0])}, B: {np.sum(grid[1])}")

# Dijkstra
start_gx, start_gy = to_grid(95.78, 35.24)
goal_gx, goal_gy = to_grid(36.0, 44.91)

pq = [(0, 1, start_gx, start_gy)]
costs = {(1, start_gx, start_gy): 0}
parent = {}
VIA_COST = 20.0

found_state = None
while pq:
    cost, l, cx, cy = heapq.heappop(pq)
    if l == 0 and np.hypot(cx - goal_gx, cy - goal_gy) <= 1.5:
        found_state = (l, cx, cy)
        break
    if cost > costs.get((l, cx, cy), float('inf')):
        continue
    
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
    if grid[0, cx, cy] == 0 and grid[1, cx, cy] == 0:
        nc = cost + VIA_COST
        if nc < costs.get((nl, cx, cy), float('inf')):
            costs[(nl, cx, cy)] = nc
            parent[(nl, cx, cy)] = (l, cx, cy)
            heapq.heappush(pq, (nc, nl, cx, cy))

print("2-layer Path found:", found_state is not None)
if found_state:
    curr = found_state
    raw_path = []
    while curr in parent:
        l, gx, gy = curr
        x, y = to_world(gx, gy)
        raw_path.append((l, x, y))
        curr = parent[curr]
    raw_path.append((1, 95.78, 35.24))
    raw_path.reverse()
    print(f"Path has {len(raw_path)} steps.")
    vias = [raw_path[i] for i in range(len(raw_path)-1) if raw_path[i][0] != raw_path[i+1][0]]
    print(f"Number of vias: {len(vias)}")
    for v in vias:
        print("  Via at:", v[1], v[2])
