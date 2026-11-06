import pcbnew, os, math

kicad_dir = os.path.abspath("kicad")
pcb_path = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

# Build courtyard caches
for fp in board.Footprints():
    fp.BuildCourtyardCaches()

fixed = {"H1", "H2", "H3", "H4", "J1", "J3", "J4", "J5", "J6", "J7", "U3", "DISP1", "SW1", "J2"}

def get_crt(fp):
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    if not c or c.IsEmpty():
        c = fp.GetCourtyard(pcbnew.B_CrtYd)
    return c

print("Starting physics relaxation...")

for iteration in range(200):
    fps = list(board.Footprints())
    overlaps = []
    
    for i in range(len(fps)):
        fp1 = fps[i]
        c1 = get_crt(fp1)
        if not c1 or c1.IsEmpty(): continue
        bb1 = c1.BBox()
        
        for j in range(i + 1, len(fps)):
            fp2 = fps[j]
            c2 = get_crt(fp2)
            if not c2 or c2.IsEmpty(): continue
            bb2 = c2.BBox()
            
            if bb1.Intersects(bb2):
                overlaps.append((fp1, fp2, bb1, bb2))
                
                # Calculate repulsive vector
                cx1 = (bb1.GetX() + bb1.GetRight()) / 2.0 / 1e6
                cy1 = (bb1.GetY() + bb1.GetBottom()) / 2.0 / 1e6
                cx2 = (bb2.GetX() + bb2.GetRight()) / 2.0 / 1e6
                cy2 = (bb2.GetY() + bb2.GetBottom()) / 2.0 / 1e6
                
                dx = cx2 - cx1
                dy = cy2 - cy1
                dist = math.hypot(dx, dy)
                if dist < 0.1:
                    dx = 0.5
                    dy = 0.5
                    dist = 0.707
                
                # Overlap depth
                overlap_x = min(bb1.GetRight(), bb2.GetRight()) - max(bb1.GetX(), bb2.GetX())
                overlap_y = min(bb1.GetBottom(), bb2.GetBottom()) - max(bb1.GetY(), bb2.GetY())
                overlap_depth = min(overlap_x, overlap_y) / 1e6 + 0.5 # push clear by at least 0.5mm
                
                nx = dx / dist
                ny = dy / dist
                
                # Push fp1 and fp2 apart
                ref1 = fp1.GetReference()
                ref2 = fp2.GetReference()
                
                if ref1 not in fixed and ref2 not in fixed:
                    p1 = fp1.GetPosition()
                    p2 = fp2.GetPosition()
                    fp1.SetPosition(pcbnew.VECTOR2I(int(p1.x - nx * overlap_depth * 0.5 * 1e6),
                                                   int(p1.y - ny * overlap_depth * 0.5 * 1e6)))
                    fp2.SetPosition(pcbnew.VECTOR2I(int(p2.x + nx * overlap_depth * 0.5 * 1e6),
                                                   int(p2.y + ny * overlap_depth * 0.5 * 1e6)))
                elif ref1 not in fixed:
                    p1 = fp1.GetPosition()
                    fp1.SetPosition(pcbnew.VECTOR2I(int(p1.x - nx * overlap_depth * 1e6),
                                                   int(p1.y - ny * overlap_depth * 1e6)))
                elif ref2 not in fixed:
                    p2 = fp2.GetPosition()
                    fp2.SetPosition(pcbnew.VECTOR2I(int(p2.x + nx * overlap_depth * 1e6),
                                                   int(p2.y + ny * overlap_depth * 1e6)))
    
    # Clamp all movable components to board area (X: 3.5..96.5, Y: 3.5..81.5)
    for fp in fps:
        ref = fp.GetReference()
        if ref not in fixed:
            p = fp.GetPosition()
            x_mm = p.x / 1e6
            y_mm = p.y / 1e6
            x_clamped = max(4.0, min(96.0, x_mm))
            y_clamped = max(4.0, min(81.0, y_mm))
            if x_clamped != x_mm or y_clamped != y_mm:
                fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_clamped), pcbnew.FromMM(y_clamped)))
        fp.BuildCourtyardCaches()
        
    print(f"Iteration {iteration+1}: {len(overlaps)} overlaps remaining.")
    if len(overlaps) == 0:
        print("ALL COURTYARD COLLISIONS RESOLVED!")
        break

pcbnew.SaveBoard(pcb_path, board)
print("Saved relaxed PCB!")
