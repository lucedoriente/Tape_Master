import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

print("Tracks on B.Cu intersecting the bounding box X:[35, 96], Y:[33, 46]:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "B.Cu":
        p1 = tr.GetStart()
        p2 = tr.GetEnd()
        x1, y1 = p1.x/1e6, p1.y/1e6
        x2, y2 = p2.x/1e6, p2.y/1e6
        # check overlap with box
        if max(x1, x2) >= 35 and min(x1, x2) <= 96 and max(y1, y2) >= 33 and min(y1, y2) <= 46:
            print(f"  Net={tr.GetNetname():25s} ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")
