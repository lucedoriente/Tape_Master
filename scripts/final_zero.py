import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # Buttons pitch 11mm: Y = 26, 37, 48, 59, 70
    "SW2": ((103.0, 26.0), 90),
    "R14": ((112.5, 26.0), 90),
    "SW3": ((103.0, 37.0), 90),
    "R15": ((112.5, 37.0), 90),
    "SW4": ((103.0, 48.0), 90),
    "R16": ((112.5, 48.0), 90),
    "SW5": ((103.0, 59.0), 90),
    "R17": ((112.5, 59.0), 90),
    "SW6": ((103.0, 70.0), 90),

    # J6 clear spacing
    "C28": ((74.5, 80.0), 0),
    "R44": ((74.5, 75.0), 90),
    "R45": ((74.5, 85.0), 90),

    "J6":  ((83.0, 81.0), 0),

    "C29": ((91.5, 75.0), 0),
    "C30": ((91.5, 80.0), 0),
    "R46": ((91.5, 85.0), 90),
    "R47": ((95.0, 85.0), 90),
}

for fp in board.Footprints():
    ref = fp.GetReference()
    if ref in updates:
        pos, rot = updates[ref]
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(pos[0]), pcbnew.FromMM(pos[1])))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)

board.Save(pcb_path)
print("Updated.")
