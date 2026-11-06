import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

for tr in board.GetTracks():
    if tr.GetNetname() == "AZIMUTH_PEAK_ADC":
        print(f"Layer {tr.GetLayerName()}: ({tr.GetStart().x/1e6:.2f}, {tr.GetStart().y/1e6:.2f}) -> ({tr.GetEnd().x/1e6:.2f}, {tr.GetEnd().y/1e6:.2f})")
