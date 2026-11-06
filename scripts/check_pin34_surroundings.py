import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

u3 = board.FindFootprintByReference("U3")
p34 = [p for p in u3.Pads() if p.GetPadName() == "34"][0]
pos34 = p34.GetPosition()
print(f"Pin 34 at ({pos34.x/1e6:.2f}, {pos34.y/1e6:.2f})")

# Check all tracks within 5mm of pin 34
for tr in board.GetTracks():
    dist = min((tr.GetStart() - pos34).EuclideanNorm(), (tr.GetEnd() - pos34).EuclideanNorm())
    if dist < 5e6:
        print(f"Near track: Net={tr.GetNetname()}, Layer={tr.GetLayerName()}, ({tr.GetStart().x/1e6:.2f}, {tr.GetStart().y/1e6:.2f}) -> ({tr.GetEnd().x/1e6:.2f}, {tr.GetEnd().y/1e6:.2f})")
