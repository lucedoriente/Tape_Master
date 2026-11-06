import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

p31 = [p for p in board.FindFootprintByReference("U3").Pads() if p.GetPadName() == "31"][0]
print("Pin 31 (AZIMUTH_PEAK_ADC) pos:", p31.GetPosition().x/1e6, p31.GetPosition().y/1e6, "Net:", p31.GetNetname())

for tr in board.GetTracks():
    if tr.GetNetname() == p31.GetNetname():
        print(f"Track on {tr.GetLayerName()} from ({tr.GetStart().x/1e6:.2f}, {tr.GetStart().y/1e6:.2f}) to ({tr.GetEnd().x/1e6:.2f}, {tr.GetEnd().y/1e6:.2f})")
