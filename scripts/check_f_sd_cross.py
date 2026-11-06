import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\temp_bak.kicad_pcb")

print("Tracks on F.Cu intersecting X:[83, 91], Y:[33, 37]:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "F.Cu":
        s, e = tr.GetStart(), tr.GetEnd()
        x1, y1 = s.x/1e6, s.y/1e6
        x2, y2 = e.x/1e6, e.y/1e6
        if max(x1, x2) >= 83 and min(x1, x2) <= 91 and max(y1, y2) >= 33 and min(y1, y2) <= 37:
            print(f"{tr.GetNetname():20s}: ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")
