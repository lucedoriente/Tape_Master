import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\temp_bak.kicad_pcb")

for tr in board.GetTracks():
    if "SD_" in tr.GetNetname() and tr.GetLayerName() == "B.Cu":
        s, e = tr.GetStart(), tr.GetEnd()
        print(f"{tr.GetNetname():15s}: ({s.x/1e6:.2f}, {s.y/1e6:.2f}) -> ({e.x/1e6:.2f}, {e.y/1e6:.2f})")
