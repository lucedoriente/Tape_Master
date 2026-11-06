import os, sys, subprocess, json, pcbnew

kicad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
pcb_path = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")
dsn_path = os.path.join(kicad_dir, "Tape-Master.dsn")
ses_path = os.path.join(kicad_dir, "Tape-Master.ses")

# 1. Update Board Design Rules & Constraints to JLCPCB / PCBWay standards
board = pcbnew.LoadBoard(pcb_path)

# Clear any old tracks/vias before routing
for t in list(board.GetTracks()):
    board.Delete(t)

ds = board.GetDesignSettings()
ds.m_HoleClearance = pcbnew.FromMM(0.18)      # USB-C NPTH post
ds.m_HoleToHoleMin = pcbnew.FromMM(0.18)
ds.m_SolderMaskMinWidth = pcbnew.FromMM(0.08) # 3 mil min solder mask web
ds.m_AllowSoldermaskBridgesInFPs = True
ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)
ds.m_MinClearance = pcbnew.FromMM(0.2)        # 8 mil trace clearance

# Set default track width and via size
ds.SetCustomTrackWidth(pcbnew.FromMM(0.25))
ds.SetCustomViaSize(pcbnew.FromMM(0.6))
ds.SetCustomViaDrill(pcbnew.FromMM(0.3))

# Ensure Silkscreen References are clean
major_refs = {"U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", "U10", "U11",
              "J1", "J2", "J3", "J4", "J5", "J6", "J7", 
              "SW1", "SW2", "SW3", "SW4", "SW5", "SW6", 
              "RV1", "RV3", "JP1", "JP2", "F1",
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

board.Save(pcb_path)
print("Board design rules and silkscreen updated.")

# 2. Export clean DSN without unclosed fp_arcs or groups
def strip_sexpr_tag(s, tag):
    out = []
    i = 0
    n = len(s)
    tag_str = '(' + tag
    while i < n:
        if s[i:i+len(tag_str)] == tag_str and (i == 0 or s[i-1] in ' \t\r\n'):
            depth = 1
            j = i + len(tag_str)
            while j < n and depth > 0:
                if s[j] == '"':
                    j += 1
                    while j < n and s[j] != '"':
                        if s[j] == '\\': j += 2
                        else: j += 1
                    j += 1
                    continue
                elif s[j] == '(': depth += 1
                elif s[j] == ')': depth -= 1
                j += 1
            while j < n and s[j] in ' \t': j += 1
            if j < n and s[j] == '\n': j += 1
            i = j
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)

with open(pcb_path, 'r', encoding='utf-8') as f:
    text = f.read()

cleaned = strip_sexpr_tag(text, 'fp_arc')
cleaned = strip_sexpr_tag(cleaned, 'group')
temp_pcb = os.path.join(kicad_dir, 'temp_clean_for_dsn.kicad_pcb')
with open(temp_pcb, 'w', encoding='utf-8') as f:
    f.write(cleaned)

b_clean = pcbnew.LoadBoard(temp_pcb)
dsn_ok = pcbnew.ExportSpecctraDSN(b_clean, dsn_path)
print(f"Exported DSN: {dsn_ok}, size: {os.path.getsize(dsn_path)} bytes")

# 3. Enforce Rule H: Headless Freerouting
cfg_paths = [
    os.path.expandvars(r"%LOCALAPPDATA%\Temp\freerouting\freerouting.json"),
    os.path.expandvars(r"%APPDATA%\freerouting\freerouting.json"),
    os.path.expandvars(r"%LOCALAPPDATA%\freerouting\freerouting.json")
]
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
for cp in cfg_paths:
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    with open(cp, "w", encoding="utf-8") as f:
        json.dump(fr_cfg, f, indent=2)

print("Enforced headless Freerouting in all config paths.")

# 4. Remove old SES if present
if os.path.exists(ses_path):
    os.remove(ses_path)

# 5. Launch Freerouting CLI
fr_exe = r"C:\Users\aless\AppData\Local\freerouting\freerouting.exe"
cmd = [fr_exe, "-de", dsn_path, "-do", ses_path, "-mp", "50"]
print("Launching Freerouting:", " ".join(cmd))
p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
print(f"Freerouting exit code: {p.returncode}")
if p.stdout:
    print("Freerouting stdout:", p.stdout[-500:])
if p.stderr:
    print("Freerouting stderr:", p.stderr[-500:])

if not os.path.exists(ses_path):
    print("ERROR: SES file was not generated!")
    sys.exit(1)

print(f"SES generated successfully! Size: {os.path.getsize(ses_path)} bytes")

# 6. Sanitize SES (strip locked placements if any)
with open(ses_path, 'r', encoding='utf-8') as f:
    ses_content = f.read()

import re
if "(lock_type position)" in ses_content:
    ses_content = ses_content.replace("(lock_type position)", "")

# Strip component placements
ses_content = re.sub(
    r"(\(placement\b[\s\S]*?)(?:\s*\(\s*component[\s\S]*?\n\s*\)\s*)+(?=\))",
    r"\1",
    ses_content,
)
clean_ses_path = os.path.join(kicad_dir, "Tape-Master-clean.ses")
with open(clean_ses_path, "w", encoding="utf-8") as f:
    f.write(ses_content)

# 7. Import Specctra SES into PCB
board = pcbnew.LoadBoard(pcb_path)
import_ok = pcbnew.ImportSpecctraSES(board, clean_ses_path)
print("ImportSpecctraSES result:", import_ok)
print("Total tracks/vias imported:", len(board.GetTracks()))

# 8. Add and Fill GND Copper Pours (120mm x 90mm)
# Remove existing zones
for z in list(board.Zones()):
    if not z.GetIsKeepout():
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
import apply_3d_fixes
print("3D models re-verified.")
