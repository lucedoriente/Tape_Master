import pcbnew, os, sys, json, subprocess, math

kicad_dir = os.path.abspath("kicad")
pcb_path = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")
dsn_path = os.path.join(kicad_dir, "Tape-Master.dsn")
ses_path = os.path.join(kicad_dir, "Tape-Master.ses")

board = pcbnew.LoadBoard(pcb_path)

# 1. Update Board Design Rules & Constraints to JLCPCB / PCBWay standards
ds = board.GetDesignSettings()
ds.m_HoleClearance = pcbnew.FromMM(0.18)      # 0.194mm USB-C NPTH post
ds.m_HoleToHoleMin = pcbnew.FromMM(0.18)
ds.m_SolderMaskMinWidth = pcbnew.FromMM(0.08) # 3 mil minimum mask web
ds.m_AllowSoldermaskBridgesInFPs = True
ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)
ds.m_MinClearance = pcbnew.FromMM(0.2)        # 8 mil trace clearance

# Set default track width and via size
ds.SetCustomTrackWidth(pcbnew.FromMM(0.25))
ds.SetCustomViaSize(pcbnew.FromMM(0.6))
ds.SetCustomViaDrill(pcbnew.FromMM(0.3))

# 2. Position J4 and J5 vertically along the right edge
j4 = board.FindFootprintByReference("J4")
if j4:
    j4.SetOrientationDegrees(90)
    j4.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(94.0), pcbnew.FromMM(48.0)))

j5 = board.FindFootprintByReference("J5")
if j5:
    j5.SetOrientationDegrees(0)
    j5.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(84.0), pcbnew.FromMM(48.0)))

# Shift U7, RV2, R33 safely inside
u7 = board.FindFootprintByReference("U7")
if u7:
    u7.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(76.0), pcbnew.FromMM(74.0)))

rv2 = board.FindFootprintByReference("RV2")
if rv2:
    rv2.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(88.0), pcbnew.FromMM(74.0)))

r33 = board.FindFootprintByReference("R33")
if r33:
    r33.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(92.0), pcbnew.FromMM(68.0)))

# 3. Clean up silkscreen
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
    else:
        rtext.SetVisible(False)

# Ensure Copyright text is present on F.SilkS
has_copyright = False
for dwg in board.GetDrawings():
    if isinstance(dwg, pcbnew.PCB_TEXT) and "Alessio Iodice" in dwg.GetText():
        has_copyright = True
        break

if not has_copyright:
    txt_copy = pcbnew.PCB_TEXT(board)
    txt_copy.SetLayer(pcbnew.F_SilkS)
    txt_copy.SetText("© 2026 by Alessio Iodice")
    txt_copy.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(50.0), pcbnew.FromMM(83.5)))
    txt_copy.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
    txt_copy.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    board.Add(txt_copy)

# 4. Save and Export Specctra DSN
pcbnew.SaveBoard(pcb_path, board)
res = pcbnew.ExportSpecctraDSN(board, dsn_path)
print("Exported Specctra DSN:", res)

# 5. Enforce Rule H: Set freerouting.json "gui": { "enabled": false }
temp_dir = os.environ.get("TEMP", os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"))
fr_dir = os.path.join(temp_dir, "freerouting")
os.makedirs(fr_dir, exist_ok=True)
fr_json_path = os.path.join(fr_dir, "freerouting.json")

fr_cfg = {
    "profile": {
        "id": "b14c330b-0443-4b67-a2f2-1a42532cb7b2",
        "email": "alessio67@gmail.com",
        "allow_telemetry": False,
        "allow_contact": False
    },
    "gui": {
        "enabled": False
    }
}
with open(fr_json_path, "w", encoding="utf-8") as f:
    json.dump(fr_cfg, f, indent=2)
print("Enforced headless mode in", fr_json_path)

# 6. Run Freerouting CLI
fr_exe = r"C:\Users\aless\AppData\Local\freerouting\freerouting.exe"
cmd = [fr_exe, "-de", dsn_path, "-do", ses_path]
print("Launching Freerouting:", " ".join(cmd))
p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
print("Freerouting return code:", p.returncode)
if p.stdout:
    print("Freerouting stdout:", p.stdout[-500:])
if p.stderr:
    print("Freerouting stderr:", p.stderr[-500:])

if os.path.exists(ses_path):
    print("SES file generated successfully, size:", os.path.getsize(ses_path))
    # 7. Import Specctra SES
    import_res = pcbnew.ImportSpecctraSES(board, ses_path)
    print("Imported Specctra SES result:", import_res)
    
    # 8. Clean up dangling vias (vias on only one layer or not connected)
    net_gnd = board.FindNet("GND")
    
    # 9. Add and Fill Copper Pours (GND on F.Cu and B.Cu)
    # Remove existing zones first to avoid duplicates
    for z in list(board.Zones()):
        board.Remove(z)
        
    for layer in [pcbnew.B_Cu, pcbnew.F_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        if net_gnd:
            zone.SetNet(net_gnd)
        zone.SetMinThickness(pcbnew.FromMM(0.2))
        
        # Define outline rectangle
        poly = pcbnew.SHAPE_LINE_CHAIN()
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(0.5)))
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(99.5), pcbnew.FromMM(0.5)))
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(99.5), pcbnew.FromMM(84.5)))
        poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(84.5)))
        poly.SetClosed(True)
        
        poly_set = pcbnew.SHAPE_POLY_SET()
        poly_set.AddOutline(poly)
        zone.SetOutline(poly_set)
        board.Add(zone)
        
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Filled copper zones on F.Cu and B.Cu!")
    
    pcbnew.SaveBoard(pcb_path, board)
    print("Saved routed board to", pcb_path)
else:
    print("ERROR: SES file was not created!")
