import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    "R38": ((23.0, 73.5), 90),
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
