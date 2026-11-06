import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # Buttons
    "SW5": ((103.0, 56.0), 90),
    "R17": ((112.5, 56.0), 90),
    "SW6": ((103.0, 66.0), 90),

    # R42, R43 between J5 and D2..D5
    "R42": ((43.0, 75.0), 90),
    "R43": ((43.0, 80.0), 90),

    # U10 at X=65.0, PWM filter at X=76.0, J6 at X=83.0
    "U10": ((65.0, 75.0), 0),
    "R48": ((65.0, 82.0), 90),

    "R44": ((76.0, 75.0), 90),
    "C28": ((76.0, 80.0), 0),
    "R45": ((76.0, 85.0), 90),

    "J6":  ((83.0, 81.0), 0),
    "C29": ((90.0, 75.0), 0),
    "C30": ((90.0, 80.0), 0),
    "R46": ((90.0, 85.0), 90),
    "R47": ((94.0, 85.0), 90),
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
