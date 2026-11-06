import os
import re
import uuid
import subprocess
import shutil
from pathlib import Path

prj_dir = Path(r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad")
src_pcb = prj_dir / "Tape-Master.kicad_pcb"
out_pcb = prj_dir / "Tape-Master-ergonomic-preview.kicad_pcb"
kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
art_dir = Path(r"C:\Users\aless\.gemini\antigravity\brain\e4725c83-ea1a-4d3e-98e3-4ebaff3f7cb6")

with open(src_pcb, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Board Size: 145 x 95 mm
# Remove old Edge.Cuts drawings
text = re.sub(r'\(gr_line[^\)]+layer "Edge\.Cuts"[^\)]*\)\n?', '', text)
text = re.sub(r'\(gr_arc[^\)]+layer "Edge\.Cuts"[^\)]*\)\n?', '', text)
text = re.sub(r'\(gr_rect[^\)]+layer "Edge\.Cuts"[^\)]*\)\n?', '', text)

# Define new 145 x 95 mm border
W, H = 145.0, 95.0
edge_cuts_sexpr = f"""  (gr_line (start 0 0) (end {W} 0) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
  (gr_line (start {W} 0) (end {W} {H}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
  (gr_line (start {W} {H}) (end 0 {H}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
  (gr_line (start 0 {H}) (end 0 0) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
"""

# Insert edge cuts before the final closing parenthesis
last_paren = text.rfind(')')
text = text[:last_paren] + edge_cuts_sexpr + text[last_paren:]

# 2. Footprint positions dictionary: {ref: (x, y, rotation)}
placements = {
    # Mounting holes
    'H1': (5.0, 5.0, 0),
    'H2': (W - 5.0, 5.0, 0),
    'H3': (5.0, H - 5.0, 0),
    'H4': (W - 5.0, H - 5.0, 0),

    # External connectors
    'J1': (25.0, 3.8, 180),    # USB-C flush to top edge
    'J2': (60.0, 3.0, 0),      # Micro-SD flush to top edge
    'U3': (110.0, 18.0, 0),    # Raspberry Pi Pico (USB at top, separated >50mm from J2!)
    'J3': (8.5, 26.0, 90),     # TAPE IN (3.5mm jack facing left)
    'J6': (8.5, 48.0, 90),     # MONITOR (3.5mm jack facing left)
    'J7': (8.5, 70.0, 90),     # AUDIO OUT (3.5mm jack facing left)
    'J4': (45.0, 91.5, 180),   # Commodore C2N Edge Connector flush to bottom edge
    'J5': (75.0, 88.0, 90),    # Commodore C2N 6-pin Header horizontal right next to J4

    # User Interface (HMI)
    'DISP1': (60.0, 24.0, 90), # OLED 0.96" Display (horizontal)
    'SW1': (92.0, 26.0, 0),    # Rotary Encoder with Pushbutton

    # Horizontal VU-meter Bargraph (D10..D19)
    'D10': (42.0, 44.0, 0),    # VU Green 1
    'D11': (46.0, 44.0, 0),    # VU Green 2
    'D12': (50.0, 44.0, 0),    # VU Green 3
    'D13': (54.0, 44.0, 0),    # VU Green 4
    'D14': (58.0, 44.0, 0),    # VU Green 5
    'D15': (62.0, 44.0, 0),    # VU Green 6
    'D16': (66.0, 44.0, 0),    # VU Green 7
    'D17': (70.0, 44.0, 0),    # VU Green 8
    'D18': (74.0, 44.0, 0),    # VU Yellow 1
    'D19': (78.0, 44.0, 0),    # VU Red 1

    # Horizontal Status LEDs (D2..D5)
    'D2': (44.0, 53.0, 0),     # READ (Green)
    'D3': (54.0, 53.0, 0),     # WRITE (Red)
    'D4': (64.0, 53.0, 0),     # MOTOR (Yellow)
    'D5': (74.0, 53.0, 0),     # SIGNAL (Blue)

    # Tactile Transport Buttons (SW2..SW6)
    'SW2': (38.0, 68.0, 0),    # PLAY / STOP
    'SW3': (54.0, 68.0, 0),    # REC / DUMP
    'SW4': (70.0, 68.0, 0),    # REW / PREV
    'SW5': (86.0, 68.0, 0),    # FFWD / NEXT
    'SW6': (104.0, 68.0, 0),   # SYSTEM RESET

    # Power supply section
    'U1': (38.0, 10.0, 0),
    'D1': (32.0, 7.0, 0),
    'F1': (16.0, 10.0, 90),
    'C1': (44.0, 10.0, 0),
    'C2': (38.0, 16.0, 0),
    'C3': (44.0, 16.0, 0),
    'C4': (16.0, 15.0, 0),
    'C5': (20.0, 15.0, 0),
    'C6': (24.0, 15.0, 0),
    'C7': (48.0, 10.0, 0),
    'D6': (48.0, 16.0, 0),
    'R23': (52.0, 16.0, 0),
    'JP1': (34.0, 16.0, 0),
    'JP2': (20.0, 20.0, 0),

    # Analog Ingest section (Left side behind audio jacks)
    'U4': (22.0, 30.0, 0),
    'RV1': (28.0, 36.0, 0),
    'C15': (16.0, 28.0, 0),
    'C16': (16.0, 32.0, 0),
    'R24': (22.0, 24.0, 0),
    'R25': (22.0, 36.0, 0),
    'R26': (26.0, 24.0, 0),
    'D7': (28.0, 24.0, 0),
    'U5': (22.0, 48.0, 0),
    'C17': (16.0, 44.0, 0),
    'C18': (16.0, 48.0, 0),
    'C19': (16.0, 52.0, 0),
    'C20': (28.0, 44.0, 0),
    'R27': (22.0, 42.0, 0),
    'R28': (22.0, 54.0, 0),
    'R29': (26.0, 42.0, 0),
    'R30': (26.0, 54.0, 0),
    'U6': (22.0, 66.0, 0),
    'C21': (16.0, 62.0, 0),
    'C22': (16.0, 66.0, 0),
    'C23': (16.0, 70.0, 0),
    'C24': (28.0, 62.0, 0),
    'D8': (16.0, 74.0, 0),
    'D9': (20.0, 74.0, 0),
    'R31': (22.0, 60.0, 0),
    'R32': (22.0, 72.0, 0),
    'R33': (26.0, 60.0, 0),
    'U8': (30.0, 52.0, 0),
    'RV3': (30.0, 60.0, 0),
    'R34': (35.0, 48.0, 0),
    'R35': (35.0, 54.0, 0),
    'R36': (35.0, 60.0, 0),

    # LED Drivers
    'U7': (95.0, 46.0, 90),
    'U11': (95.0, 60.0, 90),
    'R18': (88.0, 46.0, 0),
    'R20': (88.0, 60.0, 0),
    'C25': (100.0, 46.0, 0),
    'C27': (100.0, 60.0, 0),

    # MCU pullups & switches
    'R1': (102.0, 24.0, 0),
    'R2': (102.0, 27.0, 0),
    'R3': (102.0, 30.0, 0),
    'R4': (102.0, 33.0, 0),
    'R9': (52.0, 24.0, 0),
    'R10': (52.0, 27.0, 0),
    'R11': (92.0, 33.0, 0),
    'R12': (96.0, 33.0, 0),
    'R13': (100.0, 33.0, 0),
    'R14': (38.0, 62.0, 0),
    'R15': (54.0, 62.0, 0),
    'R16': (70.0, 62.0, 0),
    'R17': (86.0, 62.0, 0),
    'C8': (108.0, 30.0, 0),
    'C9': (108.0, 33.0, 0),
    'C10': (108.0, 36.0, 0),
    'C11': (108.0, 39.0, 0),
    'C12': (108.0, 42.0, 0),
    'C13': (108.0, 45.0, 0),

    # C2N Buffers & Drivers
    'U9': (60.0, 80.0, 0),
    'U10': (74.0, 78.0, 0),
    'Q1': (84.0, 78.0, 0),
    'Q2': (84.0, 84.0, 0),
    'R37': (60.0, 74.0, 0),
    'R38': (64.0, 74.0, 0),
    'R39': (68.0, 74.0, 0),
    'R40': (72.0, 74.0, 0),
    'R41': (76.0, 74.0, 0),
    'R42': (80.0, 74.0, 0),
    'R43': (84.0, 74.0, 0),
    'R44': (66.0, 86.0, 0),
    'R45': (70.0, 86.0, 0),
    'R46': (74.0, 86.0, 0),
    'R47': (78.0, 86.0, 0),
    'R48': (88.0, 84.0, 0),
    'C26': (54.0, 82.0, 0),
    'C28': (54.0, 86.0, 0),
    'C29': (90.0, 80.0, 0),
    'C30': (90.0, 84.0, 0),
    'C31': (90.0, 88.0, 0),
    'C32': (94.0, 84.0, 0),
    'U2': (38.0, 22.0, 0),
}

# 3. Update footprint (at ...) coordinates in text
def update_footprint(match):
    block = match.group(0)
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', block)
    if not ref_m:
        return block
    ref = ref_m.group(1)
    if ref in placements:
        x, y, rot = placements[ref]
        # Replace the first (at ...) of the footprint
        if rot != 0:
            new_at = f'(at {x:.4f} {y:.4f} {rot})'
        else:
            new_at = f'(at {x:.4f} {y:.4f})'
        block = re.sub(r'\(at [^\)]+\)', new_at, block, count=1)
    
    # If DISP1, update 3D model to OLED_0.96_I2C.wrl
    if ref == 'DISP1':
        # Remove existing (model ...) inside this footprint
        block = re.sub(r'\s*\(model [^\)]+\([^\)]+\)\([^\)]+\)\([^\)]+\)\)', '', block)
        # Add OLED 3D model
        oled_model = f"""
    (model "${{KIPRJMOD}}/3dmodels/OLED_0.96_I2C.wrl"
      (offset (xyz 0 0 0))
      (scale (xyz 0.39370079 0.39370079 0.39370079))
      (rotate (xyz 0 0 0))
    )"""
        last_paren_idx = block.rfind(')')
        block = block[:last_paren_idx] + oled_model + "\n  )"
    return block

text = re.sub(r'\(footprint [^\n]+?\n  \)', update_footprint, text, flags=re.DOTALL)

# 4. Remove old tracks and vias for preview render (clean layout view)
text = re.sub(r'\(segment [^\)]+\)\n?', '', text)
text = re.sub(r'\(via [^\)]+\)\n?', '', text)
text = re.sub(r'\(zone [^\n]+?\n  \)\n?', '', text, flags=re.DOTALL)

# 5. Add rich, professional Silkscreen labels
silks = [
    # Header / Ports
    ('USB-C 5V', 25.0, 9.0, 1.1, 'F.SilkS'),
    ('MICRO SD', 60.0, 12.0, 1.1, 'F.SilkS'),
    ('RP2040 CORE', 119.0, 10.0, 1.2, 'F.SilkS'),

    # Audio I/O Column on Left
    ('TAPE IN', 18.0, 26.0, 1.1, 'F.SilkS'),
    ('MONITOR', 18.0, 48.0, 1.1, 'F.SilkS'),
    ('AUDIO OUT', 18.0, 70.0, 1.1, 'F.SilkS'),

    # UI Section
    ('OLED 0.96" I2C DISPLAY', 60.0, 16.0, 1.2, 'F.SilkS'),
    ('ENC / NAV', 92.0, 18.0, 1.0, 'F.SilkS'),

    # VU-Meter labels
    ('-20dB           LEVEL / AZIMUTH VU-METER           +3dB', 60.0, 41.0, 0.9, 'F.SilkS'),
    ('G1   G2   G3   G4   G5   G6   G7   G8   Y1   R1', 60.0, 47.5, 0.8, 'F.SilkS'),

    # Status LED labels
    ('READ        WRITE       MOTOR       SIGNAL', 59.0, 56.5, 0.9, 'F.SilkS'),

    # Pushbutton labels
    ('[ PLAY/STOP ]', 38.0, 75.0, 1.0, 'F.SilkS'),
    ('[ REC/DUMP ]', 54.0, 75.0, 1.0, 'F.SilkS'),
    ('[ REW/PREV ]', 70.0, 75.0, 1.0, 'F.SilkS'),
    ('[ FFWD/NEXT ]', 86.0, 75.0, 1.0, 'F.SilkS'),
    ('[ RESET ]', 104.0, 75.0, 1.0, 'F.SilkS'),

    # C2N Section
    ('COMMODORE C2N DATASETTE BUS', 45.0, 85.0, 1.2, 'F.SilkS'),
    ('C2N EXT', 75.0, 93.0, 0.9, 'F.SilkS'),

    # Title & Copyright
    ('TAPE MASTER EXERCISER & DIGITIZER v1.0', 72.5, 92.0, 1.3, 'B.SilkS'),
    ('(C) 2026 by Alessio Iodice', 72.5, 3.5, 1.1, 'F.SilkS'),
]

silk_sexpr = ""
for txt, x, y, sz, layer in silks:
    silk_sexpr += f"""  (gr_text "{txt}" (at {x:.4f} {y:.4f}) (layer "{layer}") (uuid "{uuid.uuid4()}")
    (effects (font (size {sz:.2f} {sz:.2f}) (thickness {sz*0.15:.3f})))
  )\n"""

last_paren = text.rfind(')')
text = text[:last_paren] + silk_sexpr + text[last_paren:]

with open(out_pcb, "w", encoding="utf-8") as f:
    f.write(text)

print("Created ergonomic preview PCB:", out_pcb)

# 6. Render 3D images
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

print("Both 3D renders generated and copied to artifacts directory successfully!")
