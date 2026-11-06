import pcbnew, os, sys

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

updates = {
    # 1. Analog
    "C20": ((31.0, 57.0), 0),

    # 2. Power Supply
    "C7":  ((69.0, 16.0), 0),

    # 3. MicroSD
    "R5":  ((72.0, 6.0), 90),
    "R6":  ((75.0, 6.0), 90),
    "R7":  ((72.0, 11.0), 90),
    "R8":  ((75.0, 11.0), 90),

    # 4. Encoder & Buttons
    "SW1": ((101.0, 14.0), 0),
    "SW2": ((103.0, 33.0), 90),
    "R14": ((112.5, 33.0), 90),
    "SW3": ((103.0, 43.0), 90),
    "R15": ((112.5, 43.0), 90),
    "SW4": ((103.0, 53.0), 90),
    "R16": ((112.5, 53.0), 90),
    "SW5": ((103.0, 63.0), 90),
    "R17": ((112.5, 63.0), 90),
    "SW6": ((103.0, 73.0), 90),

    # 5. Bottom Tape Audio & Remote
    "C28": ((74.5, 74.0), 0),
    "C29": ((93.0, 74.0), 0),
    "C30": ((93.0, 78.5), 0),
    "R46": ((97.0, 83.0), 90),
    "R47": ((97.0, 87.0), 90),
    "U10": ((92.0, 76.0), 0),
    "R48": ((92.0, 82.0), 90)
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
print("Fixes applied.")
