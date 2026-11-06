import pcbnew, os, sys
from pathlib import Path

pcb_path = Path(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb")

board = pcbnew.LoadBoard(str(pcb_path))

# 1. Clear existing tracks, vias, and zones for clean autoroute
for t in list(board.GetTracks()):
    board.Delete(t)
for z in list(board.Zones()):
    board.Delete(z)

# 2. Update footprint positions
moves = {
    "J7": (104.0, 81.0),
    "SW6": (112.5, 72.0),
    "R42": (74.5, 68.0),
    "R43": (74.5, 71.0)
}

fp_dict = {fp.GetReference(): fp for fp in board.Footprints()}

for ref, (x, y) in moves.items():
    if ref in fp_dict:
        fp_dict[ref].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        print(f"Moved {ref} to ({x:.1f}, {y:.1f})")

# 3. Clean up silkscreen references
if "J4" in fp_dict:
    fp_dict["J4"].Reference().SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(38.0), pcbnew.FromMM(89.5)))

if "D9" in fp_dict:
    fp_dict["D9"].Reference().SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(29.0), pcbnew.FromMM(67.5)))

if "J7" in fp_dict:
    fp_dict["J7"].Reference().SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(104.0), pcbnew.FromMM(76.0)))

if "RV3" in fp_dict:
    fp_dict["RV3"].Reference().SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(37.46), pcbnew.FromMM(35.5)))

# 4. Clean up PCB texts on F.Silkscreen
for dwg in list(board.GetDrawings()):
    if isinstance(dwg, pcbnew.PCB_TEXT):
        txt = dwg.GetText()
        if "TAPE MASTER" in txt:
            dwg.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(25.0), pcbnew.FromMM(4.0)))
            dwg.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
            dwg.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
            print("Updated Title text position to (25.0, 4.0)")
        elif "Alessio Iodice" in txt:
            dwg.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(22.0), pcbnew.FromMM(87.5)))
            dwg.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
            dwg.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
            print("Updated Copyright text position to (22.0, 87.5)")

# 5. Set Design Rules
ds = board.GetDesignSettings()
ds.m_MinResolvedSpokes = 1
ds.m_HoleClearance = pcbnew.FromMM(0.18)
ds.m_HoleToHoleMin = pcbnew.FromMM(0.18)
ds.m_SolderMaskMinWidth = pcbnew.FromMM(0.08)
ds.m_AllowSoldermaskBridgesInFPs = True
ds.m_CopperEdgeClearance = pcbnew.FromMM(0.25)
ds.m_MinClearance = pcbnew.FromMM(0.2)

# Save board
pcbnew.SaveBoard(str(pcb_path), board)
print("Updated board saved to:", pcb_path)
