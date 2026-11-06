import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

print(f"Total zones: {len(board.Zones())}")
for i, z in enumerate(board.Zones()):
    print(f"Zone {i}: Net={z.GetNetname()}, Layer={z.GetLayerName()}, AssignedPriority={z.GetAssignedPriority()}")
