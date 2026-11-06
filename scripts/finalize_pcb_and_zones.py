import os, sys, re, pcbnew
from pathlib import Path

kicad_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad")))
ses_file = kicad_dir / "Tape-Master.ses"
pcb_file = kicad_dir / "Tape-Master.kicad_pcb"
clean_ses = kicad_dir / "Tape-Master-clean.ses"

def finalize():
    if not ses_file.exists():
        print("SES file not found:", ses_file)
        return False
        
    content = ses_file.read_text(encoding="utf-8")
    
    # 1. Sanitize SES
    if "(lock_type position)" in content:
        content = content.replace("(lock_type position)", "")

    # Strip component placements
    content = re.sub(
        r"(\(placement\b[\s\S]*?)(?:\s*\(\s*component[\s\S]*?\n\s*\)\s*)+(?=\))",
        r"\1",
        content,
    )

    clean_ses.write_text(content, encoding="utf-8")
    print(f"Sanitized SES written ({clean_ses.stat().st_size} bytes).")

    board = pcbnew.LoadBoard(str(pcb_file))
    # Clear any old tracks
    for t in list(board.GetTracks()):
        board.Delete(t)
    print("Old tracks cleared.")

    ok = pcbnew.ImportSpecctraSES(board, str(clean_ses.resolve()))
    print("ImportSpecctraSES result:", ok)
    print("Tracks/vias after import:", len(board.GetTracks()))

    # 2. Add GND copper zones on F.Cu and B.Cu for 120mm x 90mm board
    gnd_net = board.FindNet("GND")
    if not gnd_net:
        print("ERROR: GND net not found!")
        return False

    # Remove existing zones if any
    for z in list(board.Zones()):
        board.Remove(z)

    # Board boundary coordinates (margin 0.25mm inside Edge.Cuts: 120mm x 90mm)
    poly_pts = [
        (pcbnew.FromMM(0.25), pcbnew.FromMM(0.25)),
        (pcbnew.FromMM(119.75), pcbnew.FromMM(0.25)),
        (pcbnew.FromMM(119.75), pcbnew.FromMM(89.75)),
        (pcbnew.FromMM(0.25), pcbnew.FromMM(89.75))
    ]

    for layer_id in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer_id)
        zone.SetNetCode(gnd_net.GetNetCode())
        poly = zone.Outline()
        poly.NewOutline()
        for x, y in poly_pts:
            poly.Append(pcbnew.VECTOR2I(x, y))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.35))
        zone.SetThermalReliefGap(pcbnew.FromMM(0.25))
        zone.SetMinThickness(pcbnew.FromMM(0.25))
        zone.SetAssignedPriority(0)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        board.Add(zone)

    print("Zones added. Filling copper pours...")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Copper zones filled successfully.")

    # 3. Ensure Design Settings are strictly compliant
    ds = board.GetDesignSettings()
    ds.m_HoleClearance = pcbnew.FromMM(0.18)
    ds.m_HoleToHoleMin = pcbnew.FromMM(0.18)
    ds.m_SolderMaskMinWidth = pcbnew.FromMM(0.08)
    ds.m_AllowSoldermaskBridgesInFPs = True
    ds.m_CopperEdgeClearance = pcbnew.FromMM(0.25)
    ds.m_MinClearance = pcbnew.FromMM(0.2)

    # 4. Verify Copyright Text on F.SilkS
    has_copyright = False
    for dwg in board.GetDrawings():
        if isinstance(dwg, pcbnew.PCB_TEXT) and "Alessio Iodice" in dwg.GetText():
            has_copyright = True
            break

    if not has_copyright:
        txt_copy = pcbnew.PCB_TEXT(board)
        txt_copy.SetLayer(pcbnew.F_SilkS)
        txt_copy.SetText("© 2026 by Alessio Iodice")
        txt_copy.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(60.0), pcbnew.FromMM(88.0)))
        txt_copy.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
        txt_copy.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        board.Add(txt_copy)

    pcbnew.SaveBoard(str(pcb_file), board)
    print("PCB saved successfully to:", pcb_file)
    return True

if __name__ == "__main__":
    finalize()
