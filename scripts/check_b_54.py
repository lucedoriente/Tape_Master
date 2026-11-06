import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\temp_bak.kicad_pcb")

print("Tracks on B.Cu intersecting X:[35, 98], Y:[52, 56]:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "B.Cu":
        s, e = tr.GetStart(), tr.GetEnd()
        x1, y1 = s.x/1e6, s.y/1e6
        x2, y2 = e.x/1e6, e.y/1e6
        if max(x1, x2) >= 35 and min(x1, x2) <= 98 and max(y1, y2) >= 52 and min(y1, y2) <= 56:
            print(f"{tr.GetNetname():25s}: ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")
