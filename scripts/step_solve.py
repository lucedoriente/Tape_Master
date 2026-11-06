import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # Buttons pitch 10mm: Y=32, 42, 52, 62, 72
    "SW2": ((103.0, 32.0), 90),
    "R14": ((112.5, 32.0), 90),
    "SW3": ((103.0, 42.0), 90),
    "R15": ((112.5, 42.0), 90),
    "SW4": ((103.0, 52.0), 90),
    "R16": ((112.5, 52.0), 90),
    "SW5": ((103.0, 62.0), 90),
    "R17": ((112.5, 62.0), 90),
    "SW6": ((103.0, 72.0), 90),

    # Q1 and gate resistors
    "Q1":  ((64.0, 74.0), 0),
    "R37": ((64.0, 78.5), 90),
    "R38": ((64.0, 83.0), 90),

    # Remote U10, R48, J7
    "U10": ((88.0, 75.0), 0),
    "R48": ((88.0, 82.0), 90),
    "J7":  ((104.0, 83.0), 0),

    # Audio out filter C29, C30, R46, R47
    "C29": ((75.0, 75.0), 0),
    "C30": ((75.0, 80.0), 0),
    "R46": ((71.0, 75.0), 90),
    "R47": ((71.0, 80.0), 90),
    "R44": ((67.0, 75.0), 90),
    "C28": ((67.0, 80.0), 0),
    "R45": ((67.0, 85.0), 90),
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
