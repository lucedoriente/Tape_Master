import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

pads = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        if "TAPE_FILTERED" in p.GetNetname():
            pads.append((fp.GetReference(), p.GetPadName(), p.GetNetname(), p.GetPosition().x/1e6, p.GetPosition().y/1e6))

print("Pads with TAPE_FILTERED:")
for p in pads:
    print(" ", p)

tracks = []
for tr in board.GetTracks():
    if "TAPE_FILTERED" in tr.GetNetname():
        tracks.append((tr.GetLayerName(), tr.GetNetname(), tr.GetStart().x/1e6, tr.GetStart().y/1e6, tr.GetEnd().x/1e6, tr.GetEnd().y/1e6))

print("Tracks with TAPE_FILTERED:")
for t in tracks:
    print(" ", t)
