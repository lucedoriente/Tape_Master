import pcbnew
board = pcbnew.LoadBoard(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")
for z in board.Zones():
    print("Zone:", z.GetNetname(), [m for m in dir(z) if 'Rule' in m or 'Keep' in m or 'Area' in m])
    break
