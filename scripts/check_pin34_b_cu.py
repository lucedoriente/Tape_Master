import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

pos34 = board.FindFootprintByReference("U3").Pads()[33].GetPosition() # pin 34 is 0-indexed or find by padname

for tr in board.GetTracks():
    if tr.GetLayerName() == "B.Cu":
        dist = min((tr.GetStart() - pos34).EuclideanNorm(), (tr.GetEnd() - pos34).EuclideanNorm())
        if dist < 8e6:
            print(f"B.Cu track: Net={tr.GetNetname()} ({tr.GetStart().x/1e6:.2f}, {tr.GetStart().y/1e6:.2f}) -> ({tr.GetEnd().x/1e6:.2f}, {tr.GetEnd().y/1e6:.2f})")
