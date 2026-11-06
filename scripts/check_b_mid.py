import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\temp_bak.kicad_pcb")

print("Tracks on B.Cu intersecting X:[60, 83], Y:[33, 37]:")
for tr in board.GetTracks():
    if tr.GetLayerName() == "B.Cu":
        s, e = tr.GetStart(), tr.GetEnd()
        x1, y1 = s.x/1e6, s.y/1e6
        x2, y2 = e.x/1e6, e.y/1e6
        if max(x1, x2) >= 60 and min(x1, x2) <= 83 and max(y1, y2) >= 33 and min(y1, y2) <= 37:
            print(f"{tr.GetNetname():25s}: ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")

print("Pads on B.Cu in X:[60, 83], Y:[33, 37]:")
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.B_Cu):
            pos = p.GetPosition()
            px, py = pos.x/1e6, pos.y/1e6
            if 60 <= px <= 83 and 33 <= py <= 37:
                print(f"  {fp.GetReference()}-{p.GetPadName()} at ({px:.2f}, {py:.2f})")
