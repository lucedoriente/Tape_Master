import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

print("Tracks on F.Cu intersecting X:[80, 96], Y:[30, 40]:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "F.Cu":
        p1 = tr.GetStart()
        p2 = tr.GetEnd()
        x1, y1 = p1.x/1e6, p1.y/1e6
        x2, y2 = p2.x/1e6, p2.y/1e6
        if max(x1, x2) >= 80 and min(x1, x2) <= 96 and max(y1, y2) >= 30 and min(y1, y2) <= 40:
            print(f"  Net={tr.GetNetname():25s} ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")
