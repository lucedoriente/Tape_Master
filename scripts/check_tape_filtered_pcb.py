import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

u5 = board.FindFootprintByReference("U5")
u3 = board.FindFootprintByReference("U3")

print("U5 pos:", u5.GetPosition().x/1e6, u5.GetPosition().y/1e6)
p7 = [p for p in u5.Pads() if p.GetPadName() == "7"][0]
print("U5 Pin 7 (TAPE_FILTERED) pos:", p7.GetPosition().x/1e6, p7.GetPosition().y/1e6, "Net:", p7.GetNetname())

p34 = [p for p in u3.Pads() if p.GetPadName() == "34"][0]
print("U3 Pin 34 (GPIO28_ADC2) pos:", p34.GetPosition().x/1e6, p34.GetPosition().y/1e6, "Net:", p34.GetNetname())

# Also check U8 Pin 3 or wherever TAPE_FILTERED goes currently
for tr in board.GetTracks():
    if tr.GetNetname() == p7.GetNetname():
        print("Track on", tr.GetLayerName(), "from", tr.GetStart().x/1e6, tr.GetStart().y/1e6, "to", tr.GetEnd().x/1e6, tr.GetEnd().y/1e6)
