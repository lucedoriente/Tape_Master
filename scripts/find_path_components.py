import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

print("Components between X=35..96 and Y=25..45:")
for fp in board.GetFootprints():
    pos = fp.GetPosition()
    x = pos.x / 1e6
    y = pos.y / 1e6
    if 35 <= x <= 96 and 25 <= y <= 45:
        print(f"  {fp.GetReference():6s} ({fp.GetValue():15s}) at ({x:.2f}, {y:.2f})")
