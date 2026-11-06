import pcbnew, os, sys

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # 5. TAPE DECK INTERFACES & OUTPUTS (X: 48..105, Y: 72..88)
    "U9":  ((54.0, 80.0), 0),
    "C31": ((54.0, 86.5), 0),
    "R42": ((48.0, 78.0), 90),
    "R43": ((48.0, 83.0), 90),

    "Q1":  ((61.0, 76.0), 0),
    "R37": ((61.0, 81.0), 90),
    "R38": ((61.0, 85.5), 90),

    "U10": ((67.0, 75.0), 0),
    "R48": ((67.0, 82.0), 90),

    "R44": ((74.0, 75.0), 90),
    "C28": ((74.0, 80.0), 0),
    "R45": ((74.0, 85.0), 90),

    "J6":  ((82.0, 81.0), 0),

    "C29": ((90.0, 75.0), 0),
    "C30": ((90.0, 80.0), 0),
    "R46": ((90.0, 85.0), 90),
    "R47": ((94.0, 85.0), 90),

    "J7":  ((102.0, 81.0), 0),

    # SW6 at Y=66.0 (well above J7)
    "SW6": ((103.0, 66.0), 90)
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
