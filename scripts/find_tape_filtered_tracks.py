import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

u5 = board.FindFootprintByReference("U5")
p7 = [p for p in u5.Pads() if p.GetPadName() == "7"][0]
print("TAPE_FILTERED Net:", p7.GetNetname())

for tr in board.GetTracks():
    if tr.GetNetname() == p7.GetNetname():
        print(f"Track on {tr.GetLayerName()} from ({tr.GetStart().x/1e6:.2f}, {tr.GetStart().y/1e6:.2f}) to ({tr.GetEnd().x/1e6:.2f}, {tr.GetEnd().y/1e6:.2f})")
