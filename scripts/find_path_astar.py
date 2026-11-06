import pcbnew
import numpy as np
from collections import deque

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

# Grid resolution: 0.2 mm
RES = 0.2 # mm
X_MIN, X_MAX = 30.0, 100.0
Y_MIN, Y_MAX = 20.0, 55.0

W = int((X_MAX - X_MIN) / RES)
H = int((Y_MAX - Y_MIN) / RES)

def to_grid(x, y):
    return int((x - X_MIN) / RES), int((y - Y_MIN) / RES)

def to_world(gx, gy):
    return X_MIN + gx * RES, Y_MIN + gy * RES

# We will route on B.Cu!
# Let's map all obstacles on B.Cu within the bounding box
# Clearance required: 0.3mm (track width 0.25mm -> radius 0.125mm + clearance 0.2mm = 0.325mm clearance from obstacle centers)
CLEARANCE_MM = 0.45
CLR_PIX = int(np.ceil(CLEARANCE_MM / RES))

# Grid for B.Cu: 0 = free, 1 = obstacle
grid_b = np.zeros((W, H), dtype=np.uint8)

# 1. Pads intersecting B.Cu
for fp in board.GetFootprints():
    for p in fp.Pads():
        # Check if pad is on B.Cu (thru_hole or SMD on B.Cu)
        if p.IsOnLayer(pcbnew.B_Cu):
            pos = p.GetPosition()
            px, py = pos.x / 1e6, pos.y / 1e6
            if X_MIN - 2 <= px <= X_MAX + 2 and Y_MIN - 2 <= py <= Y_MAX + 2:
                # ignore endpoint pads
                if (abs(px - 95.78) < 0.5 and abs(py - 35.24) < 0.5):
                    continue # start pad!
                gx, gy = to_grid(px, py)
                # pad size
                sz = max(p.GetSize().x, p.GetSize().y) / 2e6 + CLEARANCE_MM
                r_pix = int(np.ceil(sz / RES))
                for dx in range(-r_pix, r_pix + 1):
                    for dy in range(-r_pix, r_pix + 1):
                        if dx*dx + dy*dy <= r_pix*r_pix:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                grid_b[nx, ny] = 1

# 2. Tracks on B.Cu
for tr in board.GetTracks():
    if tr.GetLayerName() == "B.Cu":
        p1 = tr.GetStart()
        p2 = tr.GetEnd()
        x1, y1 = p1.x / 1e6, p1.y / 1e6
        x2, y2 = p2.x / 1e6, p2.y / 1e6
        # Rasterize segment with clearance
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
                            grid_b[nx, ny] = 1

print(f"Grid built: {W}x{H}, obstacle cells: {np.sum(grid_b)} / {W*H} ({np.sum(grid_b)/(W*H)*100:.1f}%)")

# Start at Pin 34: (95.78, 35.24)
start_gx, start_gy = to_grid(95.78, 35.24)
# Goal: near R34 at (36.0, 44.91)
# Since R34 is on F.Cu, we can place a via near (37.0, 44.91) where it's free
goal_gx, goal_gy = to_grid(37.5, 44.91)

print("Start cell:", start_gx, start_gy, "free:", grid_b[start_gx, start_gy] == 0)
print("Goal cell:", goal_gx, goal_gy, "free:", grid_b[goal_gx, goal_gy] == 0)

# BFS / Dijkstra
q = deque([(start_gx, start_gy)])
parent = {}
visited = set([(start_gx, start_gy)])
found = False

# 8 directions
dirs = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]

while q:
    cx, cy = q.popleft()
    if np.hypot(cx - goal_gx, cy - goal_gy) <= 2:
        found = True
        goal_gx, goal_gy = cx, cy
        break
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < W and 0 <= ny < H and grid_b[nx, ny] == 0:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                parent[(nx, ny)] = (cx, cy)
                q.append((nx, ny))

print("Path found:", found)
if found:
    curr = (goal_gx, goal_gy)
    path = []
    while curr in parent:
        path.append(to_world(*curr))
        curr = parent[curr]
    path.append(to_world(start_gx, start_gy))
    path.reverse()
    print(f"Path length: {len(path)} points")
    print("Start:", path[0], "End:", path[-1])
