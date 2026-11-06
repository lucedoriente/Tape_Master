import pcbnew
import subprocess
import shutil
from pathlib import Path

prj_dir = Path(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad")
src_pcb = prj_dir / "Tape-Master.kicad_pcb"
out_pcb = prj_dir / "Tape-Master-ergonomic-preview.kicad_pcb"
kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
art_dir = Path(r"C:\Users\aless\.gemini\antigravity\brain\e4725c83-ea1a-4d3e-98e3-4ebaff3f7cb6")

board = pcbnew.LoadBoard(str(src_pcb))

# 1. Update Edge.Cuts to 145 x 95 mm
W, H = 145.0, 95.0
edge_lines = [dr for dr in board.GetDrawings() if dr.GetLayerName() == "Edge.Cuts"]
pts = [
    ((0, 0), (W, 0)),
    ((W, 0), (W, H)),
    ((W, H), (0, H)),
    ((0, H), (0, 0))
]
for dr, ((x1, y1), (x2, y2)) in zip(edge_lines, pts):
    dr.SetStart(pcbnew.VECTOR2I_MM(x1, y1))
    dr.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))

fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

def place(ref, x, y, rot=0.0):
    if ref in fps:
        fp = fps[ref]
        fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))

# 2. Mounting holes M3
place('H1', 5.0, 5.0)
place('H2', W - 5.0, 5.0)
place('H3', 5.0, H - 5.0)
place('H4', W - 5.0, H - 5.0)

# 3. Connectors
# J1: USB-C flush to top edge (mouth faces Y=0)
place('J1', 22.0, 3.8, 180.0)

# J2: Micro-SD flush to top edge (mouth faces Y=0), well separated between J1 and OLED
place('J2', 45.0, 3.0, 0.0)

# U3: Raspberry Pi Pico (USB at top, separated >70mm from J2!)
place('U3', 120.0, 16.0, 0.0)

# Audio Jacks: 3 jacks aligned in column on Left Edge (mouths facing X=0)
place('J3', 8.5, 26.0, 90.0) # TAPE IN
place('J6', 8.5, 48.0, 90.0) # MONITOR
place('J7', 8.5, 70.0, 90.0) # AUDIO OUT

# C2N Connectors: unified on Bottom Edge
place('J4', 42.0, 91.5, 180.0) # C2N Datassette Edge Connector flush to bottom edge
if 'J4' in fps:
    j4 = fps['J4']
    j4.Models().clear()
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/3dmodels/C2N_Edge_Connector.wrl"
    m.m_Scale = pcbnew.VECTOR3D(0.39370079, 0.39370079, 0.39370079)
    m.m_Offset = pcbnew.VECTOR3D(0, 0, 0)
    m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
    j4.Add3DModel(m)

place('J5', 72.0, 88.0, 90.0)  # C2N 6-pin Header horizontal right next to J4

# 4. User Interface (HMI) Layout - TIGHT UNIFIED CONSOLE STACK
# Top of Console: DISP1 (OLED 0.96") & SW1 (Rotary Encoder)
place('DISP1', 68.0, 18.0, 0.0)
if 'DISP1' in fps:
    disp = fps['DISP1']
    disp.Models().clear()
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/3dmodels/OLED_0.96_I2C.wrl"
    m.m_Scale = pcbnew.VECTOR3D(0.39370079, 0.39370079, 0.39370079)
    m.m_Offset = pcbnew.VECTOR3D(0, 0, 0)
    m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
    disp.Add3DModel(m)

place('SW1', 96.0, 24.0, 0.0)
if 'SW1' in fps:
    sw1 = fps['SW1']
    sw1.Models().clear()
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/3dmodels/EC11_Encoder.wrl"
    m.m_Scale = pcbnew.VECTOR3D(1.0, 1.0, 1.0)
    m.m_Offset = pcbnew.VECTOR3D(0, 0, 0)
    m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
    sw1.Add3DModel(m)

# Middle of Console: D10..D19 (Horizontal VU-Meter) immediately below OLED!
# OLED glass sits at Y=12..32, so VU-meter at Y=38 is directly below!
vu_x = 50.0
vu_y = 38.0
vu_step = 4.0
for i, ref in enumerate(['D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19']):
    place(ref, vu_x + i * vu_step, vu_y, 0.0)

# D2..D5: Horizontal Status LEDs immediately below VU-meter!
status_x = 53.0
status_y = 46.0
status_step = 10.0
for i, ref in enumerate(['D2', 'D3', 'D4', 'D5']):
    place(ref, status_x + i * status_step, status_y, 0.0)

# Bottom of Console: SW2..SW6 (Pushbuttons) immediately below the LED row!
# Pushbuttons at Y=58.0 mm
place('SW2', 40.0, 58.0, 0.0)  # PLAY/STOP
place('SW3', 54.0, 58.0, 0.0)  # REC/DUMP
place('SW4', 68.0, 58.0, 0.0)  # REW/PREV
place('SW5', 82.0, 58.0, 0.0)  # FFWD/NEXT
place('SW6', 98.0, 58.0, 0.0)  # RESET

# Supporting ICs
# Power supply:
place('U1', 32.0, 10.0, 0.0)
place('D1', 22.0, 10.0, 0.0)
place('F1', 14.0, 10.0, 90.0)
place('C1', 38.0, 10.0, 0.0)
place('C2', 32.0, 16.0, 0.0)
place('C3', 38.0, 16.0, 0.0)
place('C4', 14.0, 16.0, 0.0)
place('C5', 18.0, 16.0, 0.0)
place('C6', 22.0, 16.0, 0.0)
place('C7', 44.0, 10.0, 0.0)
place('D6', 44.0, 16.0, 0.0)
place('R23', 48.0, 16.0, 0.0)
place('JP1', 28.0, 16.0, 0.0)
place('JP2', 18.0, 20.0, 0.0)

# Analog Ingest (behind audio jacks on left side):
place('U4', 22.0, 30.0, 0.0)
place('RV1', 28.0, 36.0, 0.0)
place('C15', 16.0, 28.0, 0.0)
place('C16', 16.0, 32.0, 0.0)
place('R24', 22.0, 24.0, 0.0)
place('R25', 22.0, 36.0, 0.0)
place('R26', 26.0, 24.0, 0.0)
place('D7', 28.0, 24.0, 0.0)
place('U5', 22.0, 48.0, 0.0)
place('C17', 16.0, 44.0, 0.0)
place('C18', 16.0, 48.0, 0.0)
place('C19', 16.0, 52.0, 0.0)
place('C20', 28.0, 44.0, 0.0)
place('R27', 22.0, 42.0, 0.0)
place('R28', 22.0, 54.0, 0.0)
place('R29', 26.0, 42.0, 0.0)
place('R30', 26.0, 54.0, 0.0)
place('U6', 22.0, 66.0, 0.0)
place('C21', 16.0, 62.0, 0.0)
place('C22', 16.0, 66.0, 0.0)
place('C23', 16.0, 70.0, 0.0)
place('C24', 28.0, 62.0, 0.0)
place('D8', 16.0, 74.0, 0.0)
place('D9', 20.0, 74.0, 0.0)
place('R31', 22.0, 60.0, 0.0)
place('R32', 22.0, 72.0, 0.0)
place('R33', 26.0, 60.0, 0.0)
place('U8', 30.0, 52.0, 0.0)
place('RV3', 30.0, 60.0, 0.0)
place('R34', 35.0, 48.0, 0.0)
place('R35', 35.0, 54.0, 0.0)
place('R36', 35.0, 60.0, 0.0)

# LED drivers:
place('U7', 104.0, 42.0, 90.0)
place('U11', 104.0, 56.0, 90.0)
place('R18', 98.0, 42.0, 0.0)
place('R20', 98.0, 56.0, 0.0)
place('C25', 109.0, 42.0, 0.0)
place('C27', 109.0, 56.0, 0.0)

# MCU pullups & passives:
place('R1', 110.0, 24.0, 0.0)
place('R2', 110.0, 27.0, 0.0)
place('R3', 110.0, 30.0, 0.0)
place('R4', 110.0, 33.0, 0.0)
place('R9', 62.0, 14.0, 0.0)
place('R10', 62.0, 17.0, 0.0)
place('R11', 94.0, 17.0, 0.0)
place('R12', 98.0, 17.0, 0.0)
place('R13', 102.0, 17.0, 0.0)
place('R14', 40.0, 65.0, 0.0)
place('R15', 54.0, 65.0, 0.0)
place('R16', 68.0, 65.0, 0.0)
place('R17', 82.0, 65.0, 0.0)
place('C8', 110.0, 36.0, 0.0)
place('C9', 110.0, 39.0, 0.0)
place('C10', 110.0, 42.0, 0.0)
place('C11', 110.0, 45.0, 0.0)
place('C12', 110.0, 48.0, 0.0)
place('C13', 110.0, 51.0, 0.0)

# C2N Buffers:
place('U9', 58.0, 84.0, 0.0)
place('U10', 70.0, 80.0, 0.0)
place('Q1', 82.0, 80.0, 0.0)
place('Q2', 82.0, 86.0, 0.0)
place('R37', 58.0, 78.0, 0.0)
place('R38', 62.0, 78.0, 0.0)
place('R39', 66.0, 78.0, 0.0)
place('R40', 70.0, 78.0, 0.0)
place('R41', 74.0, 78.0, 0.0)
place('R42', 78.0, 78.0, 0.0)
place('R43', 82.0, 74.0, 0.0)
place('R44', 64.0, 88.0, 0.0)
place('R45', 68.0, 88.0, 0.0)
place('R46', 72.0, 84.0, 0.0)
place('R47', 76.0, 84.0, 0.0)
place('R48', 86.0, 84.0, 0.0)
place('C26', 52.0, 82.0, 0.0)
place('C28', 52.0, 86.0, 0.0)
place('C29', 88.0, 80.0, 0.0)
place('C30', 88.0, 84.0, 0.0)
place('C31', 88.0, 88.0, 0.0)
place('C32', 92.0, 84.0, 0.0)
place('U2', 32.0, 22.0, 0.0)

# Remove old text on F.SilkS
for item in list(board.GetDrawings()):
    if isinstance(item, pcbnew.PCB_TEXT) and item.GetLayer() == pcbnew.F_SilkS:
        board.Remove(item)

# Add rich Silkscreen labels
def add_text(txt, x, y, size=1.1, layer="F.SilkS"):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    t.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    t.SetTextThickness(int(size * 0.15 * 1e6))
    t.SetLayer(pcbnew.F_SilkS if layer == "F.SilkS" else pcbnew.B_SilkS)
    board.Add(t)

# Port labels
add_text("USB-C 5V", 22.0, 8.5, 1.1)
add_text("MICRO SD", 45.0, 11.5, 1.1)
add_text("RP2040 CORE", 128.0, 10.0, 1.2)

# Audio Labels on Left
add_text("TAPE IN", 18.0, 26.0, 1.1)
add_text("MONITOR", 18.0, 48.0, 1.1)
add_text("AUDIO OUT", 18.0, 70.0, 1.1)

# UI Labels
add_text("OLED 0.96\" I2C DISPLAY", 68.0, 12.0, 1.1)
add_text("ENC / MENU", 96.0, 16.0, 1.0)

# VU meter labels (tightly below display)
add_text("-20dB       LEVEL / AZIMUTH VU-METER       +3dB", 68.0, 35.0, 0.9)
add_text("G1  G2  G3  G4  G5  G6  G7  G8  Y1  R1", 68.0, 41.5, 0.8)

# Status LED labels
add_text("READ       WRITE      MOTOR      SIGNAL", 68.0, 49.5, 0.85)

# Pushbutton labels (tightly below LEDs)
add_text("[PLAY/STOP]", 40.0, 52.8, 0.85)
add_text("[REC/DUMP]", 54.0, 52.8, 0.85)
add_text("[REW/PREV]", 68.0, 52.8, 0.85)
add_text("[FFWD/NEXT]", 82.0, 52.8, 0.85)
add_text("[RESET]", 98.0, 52.8, 0.85)

# C2N labels
add_text("COMMODORE C2N DATASETTE BUS", 42.0, 85.0, 1.1)
add_text("C2N EXT", 72.0, 93.0, 0.9)

# Title & Copyright
add_text("TAPE MASTER EXERCISER & DIGITIZER v1.0", 72.5, 92.0, 1.4, layer="B.SilkS")
add_text("(C) 2026 by Alessio Iodice", 72.5, 3.5, 1.1)

board.Save(str(out_pcb))
print("Saved refined preview board to:", out_pcb)

# Render 3D images
print("Rendering 3D Top View...")
top_png = prj_dir / "renders" / "Tape-Master-3D-ergonomic-top.png"
subprocess.run([
    kicad_cli, "pcb", "render",
    "--width", "1920", "--height", "1080",
    "--side", "top",
    "--quality", "high",
    "-o", str(top_png),
    str(out_pcb)
], check=True)
if art_dir.exists():
    shutil.copyfile(top_png, art_dir / "Tape-Master-3D-ergonomic-top.png")

print("Rendering 3D Isometric View...")
iso_png = prj_dir / "renders" / "Tape-Master-3D-ergonomic-iso.png"
subprocess.run([
    kicad_cli, "pcb", "render",
    "--width", "1920", "--height", "1080",
    "--rotate", "45,0,45",
    "--perspective",
    "--quality", "high",
    "-o", str(iso_png),
    str(out_pcb)
], check=True)
if art_dir.exists():
    shutil.copyfile(iso_png, art_dir / "Tape-Master-3D-ergonomic-iso.png")

print("Renders updated successfully!")
