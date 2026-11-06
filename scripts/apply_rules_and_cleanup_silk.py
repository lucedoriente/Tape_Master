import pcbnew, os

kicad_dir = os.path.abspath("kicad")
pcb_path = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")
board = pcbnew.LoadBoard(pcb_path)

# 1. Update Board Design Settings to match JLCPCB / PCBWay standards
ds = board.GetDesignSettings()
ds.m_HoleClearance = pcbnew.FromMM(0.18)      # USB-C post is 0.194mm
ds.m_HoleToHoleMin = pcbnew.FromMM(0.18)
ds.m_SolderMaskMinWidth = pcbnew.FromMM(0.08) # 3 mil minimum mask web
ds.m_AllowSoldermaskBridgesInFPs = True
ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)

# 2. Shift components near edge safely inside
for ref in ["U7", "SW5", "RV2", "R33"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        p = fp.GetPosition()
        px = p.x / 1e6
        py = p.y / 1e6
        if px > 91.0:
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(90.0), p.y))

# 3. Clean up silkscreen on all footprints
# Major components whose references MUST be visible on silkscreen:
major_refs = {"U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", "U10", 
              "J1", "J2", "J3", "J4", "J5", "J6", "J7", 
              "SW1", "SW2", "SW3", "SW4", "SW5", "SW6", 
              "RV1", "RV2", "RV3", "JP1", "JP2", "F1",
              "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"}

for fp in board.Footprints():
    ref = fp.GetReference()
    fp.Value().SetVisible(False)
    
    rtext = fp.Reference()
    if ref in major_refs:
        rtext.SetVisible(True)
        rtext.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        # Position outside bounding box
        pos = fp.GetPosition()
        rtext.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y - pcbnew.FromMM(3.5)))
    else:
        # Hide reference for high density 0805 passives to eliminate silkscreen-over-copper collisions
        rtext.SetVisible(False)

pcbnew.SaveBoard(pcb_path, board)
print("Saved cleaned board!")
