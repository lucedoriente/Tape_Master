import pcbnew

board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

# Let's inspect obstacles between X=36..96 and Y=33..46 on F.Cu
print("--- F.Cu obstacles ---")
for tr in board.GetTracks():
    if tr.GetLayerName() == "F.Cu":
        s = tr.GetStart()
        e = tr.GetEnd()
        x1, y1 = s.x/1e6, s.y/1e6
        x2, y2 = e.x/1e6, e.y/1e6
        if max(x1, x2) >= 36 and min(x1, x2) <= 96 and max(y1, y2) >= 33 and min(y1, y2) <= 46:
            if tr.GetNetname() != "GND":
                print(f"  {tr.GetNetname():20s} ({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f}) w={tr.GetWidth()/1e6:.2f}")

for fp in board.GetFootprints():
    for p in fp.Pads():
        pos = p.GetPosition()
        x, y = pos.x/1e6, pos.y/1e6
        if 36 <= x <= 96 and 33 <= y <= 46:
            if p.GetNetname() != "GND":
                print(f"  Pad {fp.GetReference()}-{p.GetPadName()} Net={p.GetNetname()} at ({x:.2f}, {y:.2f})")
