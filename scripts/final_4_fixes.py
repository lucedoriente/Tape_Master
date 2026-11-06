import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # Move R42, R43 away from R37, R38
    "R42": ((58.0, 74.0), 90),
    "R43": ((58.0, 87.0), 90),

    # J6 at X=81.0, and C29, C30 to the right of J6
    "J6":  ((81.0, 81.0), 0),
    "C29": ((88.0, 74.5), 0),
    "C30": ((88.0, 79.5), 0),
    "R46": ((88.0, 84.5), 90),
    "R47": ((92.0, 84.5), 90),

    "U10": ((94.0, 75.0), 0),
    "R48": ((94.0, 81.0), 90),
    "J7":  ((104.0, 83.0), 0)
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
