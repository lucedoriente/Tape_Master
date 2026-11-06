import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\temp_bak.kicad_pcb")

print("Tracks intersecting Y:[20, 24], X:[30, 96] on F.Cu:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "F.Cu":
        s, e = tr.GetStart(), tr.GetEnd()
        x1, y1 = s.x/1e6, s.y/1e6
        x2, y2 = e.x/1e6, e.y/1e6
        if max(x1, x2) >= 30 and min(x1, x2) <= 96 and max(y1, y2) >= 20 and min(y1, y2) <= 24:
            print(f"  F.Cu {tr.GetNetname():20s} ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")

print("Tracks intersecting Y:[20, 24], X:[30, 96] on B.Cu:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "B.Cu":
        s, e = tr.GetStart(), tr.GetEnd()
        x1, y1 = s.x/1e6, s.y/1e6
        x2, y2 = e.x/1e6, e.y/1e6
        if max(x1, x2) >= 30 and min(x1, x2) <= 96 and max(y1, y2) >= 20 and min(y1, y2) <= 24:
            print(f"  B.Cu {tr.GetNetname():20s} ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")
