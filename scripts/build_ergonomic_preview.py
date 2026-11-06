import pcbnew

src_pcb = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
out_pcb = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master-ergonomic-preview.kicad_pcb"

board = pcbnew.LoadBoard(src_pcb)

# 1. Update Edge.Cuts to 145 x 95 mm
for dr in list(board.GetDrawings()):
    if dr.GetLayerName() == "Edge.Cuts":
        board.Remove(dr)

W, H = 145.0, 95.0

def add_line(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetFilled(False)
    s.SetWidth(int(0.15 * 1e6))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(pcbnew.VECTOR2I(int(x1 * 1e6), int(y1 * 1e6)))
    s.SetEnd(pcbnew.VECTOR2I(int(x2 * 1e6), int(y2 * 1e6)))
    board.Add(s)

add_line(0, 0, W, 0)
add_line(W, 0, W, H)
add_line(W, H, 0, H)
add_line(0, H, 0, 0)

fps = {fp.GetReference(): fp for fp in board.GetFootprints()}

# 2. Update Mounting Holes M3
mh_pos = {
    'H1': (5.0, 5.0),
    'H2': (W - 5.0, 5.0),
    'H3': (5.0, H - 5.0),
    'H4': (W - 5.0, H - 5.0)
}
for ref, (x, y) in mh_pos.items():
    if ref in fps:
        fps[ref].SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))

# 3. Position Connectors Flush to Edge
def place(ref, x, y, rot=0.0):
    if ref in fps:
        fp = fps[ref]
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))

# J1: USB-C flush to top edge (mouth faces Y=0)
place('J1', 25.0, 3.8, 180.0)

# J2: Micro-SD flush to top edge (mouth faces Y=0)
place('J2', 58.0, 3.0, 0.0)

# U3: Raspberry Pi Pico on right side (USB at top, separated >50mm from J2!)
place('U3', 110.0, 18.0, 0.0)

# Audio Jacks: 3 jacks aligned in column on Left Edge (mouths facing X=0)
place('J3', 8.5, 26.0, 90.0) # TAPE IN
place('J6', 8.5, 48.0, 90.0) # MONITOR
place('J7', 8.5, 70.0, 90.0) # AUDIO OUT

# C2N Connectors: unified on Bottom Edge
place('J4', 45.0, 91.5, 180.0) # C2N Datassette Edge Connector flush to bottom edge
place('J5', 74.0, 88.0, 90.0)  # C2N 6-pin Header horizontal right next to J4

# 4. User Interface (HMI) Layout
# DISP1: OLED 0.96" I2C Display
place('DISP1', 62.0, 24.0, 90.0)
if 'DISP1' in fps:
    disp = fps['DISP1']
    disp.Models().clear()
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = "${KIPRJMOD}/3dmodels/OLED_0.96_I2C.wrl"
    m.m_Scale = pcbnew.VECTOR3D(0.39370079, 0.39370079, 0.39370079)
    m.m_Offset = pcbnew.VECTOR3D(0, 0, 0)
    m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
    disp.Add3DModel(m)

# SW1: Rotary Encoder
place('SW1', 92.0, 26.0, 0.0)

# D10..D19: Horizontal VU-Meter Bargraph (8 Green, 1 Yellow, 1 Red)
vu_x = 42.0
vu_y = 44.0
vu_step = 4.0
for i, ref in enumerate(['D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19']):
    place(ref, vu_x + i * vu_step, vu_y, 0.0)

# D2..D5: Horizontal Status LEDs
status_x = 44.0
status_y = 53.0
status_step = 10.0
for i, ref in enumerate(['D2', 'D3', 'D4', 'D5']):
    place(ref, status_x + i * status_step, status_y, 0.0)

# SW2..SW6: Pushbutton Transport Bar
place('SW2', 38.0, 68.0, 0.0)  # PLAY/STOP
place('SW3', 54.0, 68.0, 0.0)  # REC/DUMP
place('SW4', 70.0, 68.0, 0.0)  # REW/PREV
place('SW5', 86.0, 68.0, 0.0)  # FFWD/NEXT
place('SW6', 104.0, 68.0, 0.0) # RESET

# Supporting ICs
# Power supply:
place('U1', 38.0, 10.0, 0.0)
place('D1', 32.0, 7.0, 0.0)
place('F1', 16.0, 10.0, 90.0)
place('C1', 44.0, 10.0, 0.0)
place('C2', 38.0, 16.0, 0.0)
place('C3', 44.0, 16.0, 0.0)
place('D6', 48.0, 16.0, 0.0)
place('R23', 48.0, 10.0, 0.0)

# Analog Ingest (behind audio jacks on left side):
place('U4', 22.0, 30.0, 0.0)
place('RV1', 28.0, 36.0, 0.0)
place('U5', 22.0, 48.0, 0.0)
place('U6', 22.0, 66.0, 0.0)
place('U8', 30.0, 52.0, 0.0)
place('RV3', 30.0, 60.0, 0.0)

# LED drivers:
place('U7', 95.0, 48.0, 90.0)
place('U11', 95.0, 62.0, 90.0)
place('R18', 88.0, 48.0, 0.0)
place('R20', 88.0, 62.0, 0.0)

# C2N Buffers:
place('U9', 60.0, 80.0, 0.0)
place('U10', 74.0, 78.0, 0.0)
place('Q1', 84.0, 80.0, 0.0)
place('Q2', 84.0, 86.0, 0.0)

# Add rich Silkscreen labels
def add_text(txt, x, y, size=1.2, layer="F.SilkS"):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
    t.SetTextSize(pcbnew.VECTOR2I(int(size * 1e6), int(size * 1e6)))
    t.SetTextThickness(int(size * 0.15 * 1e6))
    t.SetLayer(pcbnew.F_SilkS if layer == "F.SilkS" else pcbnew.B_SilkS)
    board.Add(t)

# Labels
add_text("USB-C 5V", 25.0, 8.5, 1.0)
add_text("MICRO SD", 58.0, 11.5, 1.0)
add_text("RP2040 CORE", 119.0, 10.0, 1.2)

# Audio Labels
add_text("TAPE IN", 18.0, 24.0, 1.0)
add_text("MONITOR", 18.0, 46.0, 1.0)
add_text("AUDIO OUT", 18.0, 68.0, 1.0)

# UI Labels
add_text("OLED 0.96\" I2C", 62.0, 18.0, 1.1)
add_text("ENC / MENU", 92.0, 18.0, 1.0)

# VU meter labels
add_text("-20dB          LEVEL / AZIMUTH          +3dB", 60.0, 40.5, 0.9)
add_text("G1  G2  G3  G4  G5  G6  G7  G8  Y1  R1", 60.0, 48.0, 0.8)

# Status LED labels
add_text("READ      WRITE     MOTOR     SIGNAL", 59.0, 58.0, 0.9)

# Pushbutton labels
add_text("[PLAY/STOP]", 38.0, 75.0, 1.0)
add_text("[REC/DUMP]", 54.0, 75.0, 1.0)
add_text("[REW/PREV]", 70.0, 75.0, 1.0)
add_text("[FFWD/NEXT]", 86.0, 75.0, 1.0)
add_text("[RESET]", 104.0, 75.0, 1.0)

# C2N labels
add_text("COMMODORE C2N DATASETTE BUS", 45.0, 85.0, 1.1)
add_text("C2N EXT", 74.0, 93.0, 0.9)

# Title & Copyright
add_text("TAPE MASTER EXERCISER & DIGITIZER v1.0", 72.5, 92.0, 1.4, layer="B.Silkscreen")
add_text("(C) 2026 by Alessio Iodice", 72.5, 3.5, 1.1)

# Clear tracks and filled polys on zones for clean 3D preview of the placement
for tr in list(board.GetTracks()):
    board.Remove(tr)
for z in board.Zones():
    z.ClearFilledPolysList()

board.Save(out_pcb)
print("Saved ergonomic preview board to:", out_pcb)
