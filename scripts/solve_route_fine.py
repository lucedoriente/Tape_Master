import pcbnew
import numpy as np
import heapq

board_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
test_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master-test-route.kicad_pcb"

board = pcbnew.LoadBoard(board_path)
net = board.FindNet("TAPE_FILTERED")

RES = 0.1 # 100 um resolution
X_MIN, X_MAX = 30.0, 98.0
Y_MIN, Y_MAX = 15.0, 55.0
W = int(round((X_MAX - X_MIN) / RES))
H = int(round((Y_MAX - Y_MIN) / RES))

def to_grid(x, y): return int(round((x - X_MIN) / RES)), int(round((y - Y_MIN) / RES))
def to_world(gx, gy): return round(X_MIN + gx * RES, 4), round(Y_MIN + gy * RES, 4)

# Track clearance: 0.25 mm (guarantee > 0.20 mm DRC netclass)
TR_RADIUS = 0.10
TR_CLR = 0.25

# Via diameter: 0.60 mm -> radius 0.30 mm
# Via drill: 0.30 mm -> radius 0.15 mm
VIA_RADIUS = 0.30
VIA_CLR = 0.28

# 2 layers: 0 = F.Cu, 1 = B.Cu
# We will maintain:
# tr_blocked[layer, x, y] = whether a track center can be at (x, y)
# via_blocked[x, y] = whether a via center can be at (x, y)
tr_blocked = np.zeros((2, W, H), dtype=bool)
via_blocked = np.zeros((W, H), dtype=bool)

# Target connections: start at (95.78, 35.24), goal at (36.00, 44.9125)
START = (95.78, 35.24)
GOAL = (36.00, 44.9125)

# 1. Footprint pads
for fp in board.GetFootprints():
    for p in fp.Pads():
        pos = p.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        if X_MIN - 2 <= px <= X_MAX + 2 and Y_MIN - 2 <= py <= Y_MAX + 2:
            # Check if this is the start or goal pad
            is_start = (abs(px - START[0]) < 0.5 and abs(py - START[1]) < 0.5)
            is_goal = (abs(px - GOAL[0]) < 0.5 and abs(py - GOAL[1]) < 0.5)
            
            p_size = np.hypot(p.GetSize().x, p.GetSize().y) / 2e6
            p_drill = max(p.GetDrillSize().x, p.GetDrillSize().y) / 2e6 if p.GetDrillSize().x > 0 else 0
            
            # For each layer
            for layer_idx, layer_id in enumerate([pcbnew.F_Cu, pcbnew.B_Cu]):
                if p.IsOnLayer(layer_id):
                    # If this pad belongs to TAPE_FILTERED, ignore it for track blocking (so we can connect)
                    if p.GetNetname() == "TAPE_FILTERED":
                        continue
                    
                    # Block tracks
                    r_tr = p_size + TR_RADIUS + TR_CLR
                    r_pix = int(np.ceil(r_tr / RES))
                    gx, gy = to_grid(px, py)
                    for dx in range(-r_pix, r_pix + 1):
                        for dy in range(-r_pix, r_pix + 1):
                            if (dx*RES)**2 + (dy*RES)**2 <= r_tr**2:
                                nx, ny = gx + dx, gy + dy
                                if 0 <= nx < W and 0 <= ny < H:
                                    tr_blocked[layer_idx, nx, ny] = True
            
            # Block vias from pads
            # Via copper clearance
            if not is_start and not is_goal:
                r_via = p_size + VIA_RADIUS + VIA_CLR
                if p_drill > 0:
                    # Hole clearance: 0.18 mm constraint + drill radii
                    r_hole = p_drill + 0.15 + 0.20
                    r_via = max(r_via, r_hole)
                r_pix = int(np.ceil(r_via / RES))
                gx, gy = to_grid(px, py)
                for dx in range(-r_pix, r_pix + 1):
                    for dy in range(-r_pix, r_pix + 1):
                        if (dx*RES)**2 + (dy*RES)**2 <= r_via**2:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                via_blocked[nx, ny] = True

# 2. Existing tracks & vias
for tr in board.GetTracks():
    if tr.GetNetname() == "TAPE_FILTERED":
        continue
    if isinstance(tr, pcbnew.PCB_VIA):
        pos = tr.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        v_r = tr.GetWidth(pcbnew.F_Cu) / 2e6
        v_drill = tr.GetDrillValue() / 2e6
        gx, gy = to_grid(px, py)
        # Block tracks on both layers
        r_tr = v_r + TR_RADIUS + TR_CLR
        r_pix = int(np.ceil(r_tr / RES))
        for dx in range(-r_pix, r_pix + 1):
            for dy in range(-r_pix, r_pix + 1):
                if (dx*RES)**2 + (dy*RES)**2 <= r_tr**2:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        tr_blocked[0, nx, ny] = True
                        tr_blocked[1, nx, ny] = True
        # Block vias (via-to-via clearance)
        r_via = v_r + VIA_RADIUS + VIA_CLR
        r_hole = v_drill + 0.15 + 0.20 # 0.18mm hole clearance + 0.02mm margin
        r_via_max = max(r_via, r_hole)
        r_pix = int(np.ceil(r_via_max / RES))
        for dx in range(-r_pix, r_pix + 1):
            for dy in range(-r_pix, r_pix + 1):
                if (dx*RES)**2 + (dy*RES)**2 <= r_via_max**2:
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        via_blocked[nx, ny] = True
    else:
        layer_id = tr.GetLayer()
        layer_idx = 0 if layer_id == pcbnew.F_Cu else (1 if layer_id == pcbnew.B_Cu else -1)
        if layer_idx != -1:
            p1, p2 = tr.GetStart(), tr.GetEnd()
            x1, y1 = p1.x / 1e6, p1.y / 1e6
            x2, y2 = p2.x / 1e6, p2.y / 1e6
            tr_w = tr.GetWidth() / 2e6
            dist = np.hypot(x2 - x1, y2 - y1)
            steps = max(1, int(dist / (RES / 2)))
            r_tr = tr_w + TR_RADIUS + TR_CLR
            r_pix_tr = int(np.ceil(r_tr / RES))
            r_via = tr_w + VIA_RADIUS + VIA_CLR
            r_pix_via = int(np.ceil(r_via / RES))
            for s in range(steps + 1):
                t = s / steps
                x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
                gx, gy = to_grid(x, y)
                # Block tracks on this layer
                for dx in range(-r_pix_tr, r_pix_tr + 1):
                    for dy in range(-r_pix_tr, r_pix_tr + 1):
                        if (dx*RES)**2 + (dy*RES)**2 <= r_tr**2:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                tr_blocked[layer_idx, nx, ny] = True
                # Block vias
                for dx in range(-r_pix_via, r_pix_via + 1):
                    for dy in range(-r_pix_via, r_pix_via + 1):
                        if (dx*RES)**2 + (dy*RES)**2 <= r_via**2:
                            nx, ny = gx + dx, gy + dy
                            if 0 <= nx < W and 0 <= ny < H:
                                via_blocked[nx, ny] = True

# Also, via is blocked if either layer track is blocked at that cell
via_blocked |= tr_blocked[0] | tr_blocked[1]

print(f"Grid {W}x{H} (res {RES}mm). Free F: {np.sum(~tr_blocked[0])}, Free B: {np.sum(~tr_blocked[1])}, Free Via: {np.sum(~via_blocked)}")

start_gx, start_gy = to_grid(*START)
goal_gx, goal_gy = to_grid(*GOAL)

# Dijkstra
pq = [(0, 0, start_gx, start_gy), (0, 1, start_gx, start_gy)]
costs = {(0, start_gx, start_gy): 0, (1, start_gx, start_gy): 0}
parent = {}
via_cost = 50.0
found_state = None

while pq:
    cost, l, cx, cy = heapq.heappop(pq)
    # Check if close to goal on F.Cu
    if l == 0 and np.hypot(cx - goal_gx, cy - goal_gy) <= 2:
        found_state = (l, cx, cy)
        break
    if cost > costs.get((l, cx, cy), float('inf')):
        continue
    
    # 8-direction step
    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < W and 0 <= ny < H and not tr_blocked[l, nx, ny]:
            step_cost = 1.414 if (dx != 0 and dy != 0) else 1.0
            nc = cost + step_cost
            if nc < costs.get((l, nx, ny), float('inf')):
                costs[(l, nx, ny)] = nc
                parent[(l, nx, ny)] = (l, cx, cy)
                heapq.heappush(pq, (nc, l, nx, ny))
    
    # Via transition
    nl = 1 - l
    if not via_blocked[cx, cy]:
        nc = cost + via_cost
        if nc < costs.get((nl, cx, cy), float('inf')):
            costs[(nl, cx, cy)] = nc
            parent[(nl, cx, cy)] = (l, cx, cy)
            heapq.heappush(pq, (nc, nl, cx, cy))

print("Path found:", found_state is not None)
if not found_state:
    exit(1)

curr = found_state
raw_path = []
while curr in parent:
    raw_path.append(curr)
    curr = parent[curr]
raw_path.append(curr)
raw_path.reverse()

# Reconstruct into segments and vias
segments = []
vias = []

# Connect start pad
actual_start = (raw_path[0][0], *START)
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

# Connect last point to exact goal
actual_end = (0, *GOAL)
last_pt = (segments[-1][0], segments[-1][2][0], segments[-1][2][1])
if np.hypot(last_pt[1] - actual_end[1], last_pt[2] - actual_end[2]) > 1e-4:
    segments.append((0, (last_pt[1], last_pt[2]), (actual_end[1], actual_end[2])))

print(f"Generated {len(segments)} segments and {len(vias)} vias.")
for v in vias:
    print(f"  Via at ({v[0]:.2f}, {v[1]:.2f})")

# Clean existing TAPE_FILTERED tracks that might have been added in test
for tr in list(board.GetTracks()):
    # only remove if it's connected to U3 pin 34
    p1, p2 = tr.GetStart(), tr.GetEnd()
    if tr.GetNetname() == "TAPE_FILTERED" and (p1.x > 80e6 or p2.x > 80e6):
        board.Remove(tr)

for s in segments:
    layer_id = pcbnew.F_Cu if s[0] == 0 else pcbnew.B_Cu
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(int(round(s[1][0] * 1e6)), int(round(s[1][1] * 1e6))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(s[2][0] * 1e6)), int(round(s[2][1] * 1e6))))
    t.SetWidth(int(round(0.20 * 1e6))) # 0.2mm track width
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

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(test_path)
print("Saved to:", test_path)
