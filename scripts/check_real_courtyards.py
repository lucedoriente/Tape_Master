import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)
fps = list(board.Footprints())

for fp in fps:
    fp.BuildCourtyardCaches()

overlaps = []
for i in range(len(fps)):
    fp1 = fps[i]
    c1 = fp1.GetCourtyard(pcbnew.F_CrtYd)
    if not c1 or c1.IsEmpty():
        c1 = fp1.GetCourtyard(pcbnew.B_CrtYd)
    if not c1 or c1.IsEmpty():
        continue
    bb1 = c1.BBox()
    
    for j in range(i + 1, len(fps)):
        fp2 = fps[j]
        c2 = fp2.GetCourtyard(pcbnew.F_CrtYd)
        if not c2 or c2.IsEmpty():
            c2 = fp2.GetCourtyard(pcbnew.B_CrtYd)
        if not c2 or c2.IsEmpty():
            continue
        bb2 = c2.BBox()
        
        if bb1.Intersects(bb2):
            overlaps.append((fp1.GetReference(), fp2.GetReference()))

print(f"Total true courtyard intersections: {len(overlaps)}")
for o in overlaps:
    print("  Overlap:", o)
