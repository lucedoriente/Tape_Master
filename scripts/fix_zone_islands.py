import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

for z in board.Zones():
    if not z.GetIsRuleArea():
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

board.Save(pcb_file)
print("Updated zones with ISLAND_REMOVAL_MODE_ALWAYS and filled.")
