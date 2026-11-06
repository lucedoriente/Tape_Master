import pcbnew

b = pcbnew.LoadBoard('kicad/Tape-Master.kicad_pcb')

updates = {
    # Buttons rotated 90 deg along top edge
    'SW2': ((58.5, 8.0), 90),
    'SW3': ((67.5, 8.0), 90),
    'SW4': ((76.5, 8.0), 90),
    'SW5': ((85.5, 8.0), 90),
    
    # Q1, Q2, C30 moved out of J4 courtyard
    'Q1': ((75.0, 35.0), 0),
    'Q2': ((80.0, 35.0), 0),
    'C30': ((75.0, 40.0), 0),
    
    # U7 region moved and rotated inside board boundary
    'U7': ((73.0, 71.5), 90),
    'RV2': ((83.0, 78.5), 0),
    'C25': ((73.0, 78.5), 0),
    'R33': ((88.0, 78.5), 0),
    'D2': ((73.0, 46.0), 0),
    'R19': ((77.5, 46.0), 0),
    'D3': ((73.0, 50.0), 0),
    'R20': ((77.5, 50.0), 0),
    'D4': ((73.0, 54.0), 0),
    'R21': ((77.5, 54.0), 0),
    'D5': ((73.0, 58.0), 0),
    'R22': ((77.5, 58.0), 0),
}

# Clear any old tracks/vias before new auto-routing
for t in list(b.GetTracks()):
    b.Delete(t)

for fp in b.Footprints():
    ref = fp.GetReference()
    if ref in updates:
        pos, rot = updates[ref]
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(pos[0]), pcbnew.FromMM(pos[1])))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)

b.Save('kicad/Tape-Master.kicad_pcb')
print('Flawless placement applied and saved to kicad/Tape-Master.kicad_pcb')
