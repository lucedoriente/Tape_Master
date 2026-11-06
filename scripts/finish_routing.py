import pcbnew, os

kicad_dir = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad"
pcb_path = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")
clean_ses_path = os.path.join(kicad_dir, "Tape-Master-clean.ses")

board = pcbnew.LoadBoard(pcb_path)
import_ok = pcbnew.ImportSpecctraSES(board, clean_ses_path)
print("ImportSpecctraSES result:", import_ok)
print("Total tracks/vias imported:", len(board.GetTracks()))

# 8. Add and Fill GND Copper Pours (120mm x 90mm)
for z in list(board.Zones()):
    if not z.GetIsRuleArea():
        board.Remove(z)

gnd_net = board.FindNet("GND")
if not gnd_net:
    print("WARNING: GND net not found!")
else:
    for layer in [pcbnew.B_Cu, pcbnew.F_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd_net)
        zone.SetMinThickness(pcbnew.FromMM(0.25))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.35))
        zone.SetThermalReliefGap(pcbnew.FromMM(0.25))
        
        # 120mm x 90mm polygon (0.25mm inset inside board edge)
        poly = pcbnew.SHAPE_LINE_CHAIN()
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(0.25), pcbnew.FromMM(0.25)))
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(119.75), pcbnew.FromMM(0.25)))
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(119.75), pcbnew.FromMM(89.75)))
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(0.25), pcbnew.FromMM(89.75)))
        poly.SetClosed(True)
        
        poly_set = pcbnew.SHAPE_POLY_SET()
        poly_set.AddOutline(poly)
        zone.SetOutline(poly_set)
        board.Add(zone)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Filled GND copper zones on F.Cu and B.Cu successfully!")

board.Save(pcb_path)
print("Routed board saved to:", pcb_path)

# Apply 3D fixes
import apply_3d_fixes
print("Finished!")
