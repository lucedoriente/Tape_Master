import pcbnew, os, sys

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # 2. Power Supply & VBIAS
    "D1":  ((66.0, 13.0), 0),
    "C1":  ((60.0, 15.0), 0),
    "C2":  ((55.0, 15.0), 0),
    "C3":  ((50.0, 15.0), 0),
    "C7":  ((71.0, 14.0), 0),

    # 3. MicroSD
    "J2":  ((88.0, 8.5), 0),
    "R5":  ((75.0, 15.0), 90),
    "R6":  ((78.0, 15.0), 90),
    "R7":  ((75.0, 19.0), 90),
    "R8":  ((78.0, 19.0), 90),

    # 4. Buttons (pitch 11mm, ending at Y=66.0)
    "SW2": ((104.0, 22.0), 90),
    "R14": ((112.5, 22.0), 90),
    "SW3": ((104.0, 33.0), 90),
    "R15": ((112.5, 33.0), 90),
    "SW4": ((104.0, 44.0), 90),
    "R16": ((112.5, 44.0), 90),
    "SW5": ((104.0, 55.0), 90),
    "R17": ((112.5, 55.0), 90),
    "SW6": ((104.0, 66.0), 90),

    # 5. Audio Out J6, Remote J7, Opto U10
    "J6":  ((82.0, 81.0), 0),
    "R44": ((71.0, 74.0), 90),
    "C28": ((75.0, 74.0), 0),
    "R45": ((71.0, 79.0), 90),

    "C29": ((89.0, 75.0), 0),
    "C30": ((89.0, 80.0), 0),
    "R46": ((89.0, 85.0), 90),
    "R47": ((93.0, 85.0), 90),

    "J7":  ((106.0, 81.0), 0),
    "U10": ((97.0, 75.0), 0),
    "R48": ((97.0, 81.0), 90)
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
print("Applied final fixes.")
