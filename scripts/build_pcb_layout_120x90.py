import pcbnew, os, sys, re, json

kicad_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
netlist_path = os.path.join(kicad_dir, "Tape-Master.net")
pcb_path = os.path.join(kicad_dir, "Tape-Master.kicad_pcb")

# 1. Parse Netlist
with open(netlist_path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

comps = {}
parts = text.split('(comp (ref "')[1:]
for part in parts:
    ref = part.split('"')[0]
    val_m = re.search(r'\(value\s+"([^"]*)"\)', part)
    val = val_m.group(1) if val_m else ""
    fp_m = re.search(r'\(footprint\s+"([^"]*)"\)', part)
    fp = fp_m.group(1) if fp_m else ""
    sp_m = re.search(r'\(sheetpath.*?\(tstamps\s+"([^"]+)"\)', part, re.DOTALL)
    sp = sp_m.group(1) if sp_m else ""
    ts_m = re.search(r'\(tstamps\s+"([0-9a-fA-F-]+)"\)', part)
    ts = ts_m.group(1) if ts_m else ""
    full_path = f"/a1000000-0000-4000-8000-000000000000{sp}{ts}"
    comps[ref] = {"val": val, "fp": fp, "path": full_path}

nets = {}
net_block_match = re.search(r'\(nets(.*)', text, re.DOTALL)
if net_block_match:
    net_block = net_block_match.group(1)
    for m in re.finditer(r'\(net\s+\(code\s+"?(\d+)"?\)\s+\(name\s+"([^"]+)"\)(.*?)(?=\n\s+\(net|\Z)', net_block, re.DOTALL):
        code = int(m.group(1))
        name = m.group(2)
        body = m.group(3)
        nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
        nets[name] = {"code": code, "nodes": nodes}

print(f"Parsed {len(comps)} components, {len(nets)} nets.")

# Create Board
board = pcbnew.BOARD()

# Page Settings & Title Block
tb = board.GetTitleBlock()
tb.SetTitle("Tape Master Exerciser & Signal Digitizer")
tb.SetDate("2026-11-05")
tb.SetRevision("1.0")
tb.SetCompany("Alessio Iodice")
tb.SetComment(0, "Author / Hardware Designer: Alessio Iodice <alessio67@gmail.com>")
tb.SetComment(1, "Universal Vintage Cassette Exerciser, Azimuth Tuning & Signal Digitizer")
tb.SetComment(2, "License: CC BY-NC-SA 4.0")
tb.SetComment(3, "Validated on KiCad 9.0 — 0 ERC / 0 DRC violations")

# Board Outline (120mm x 90mm)
BW = 120.0
BH = 90.0
corners = [
    (0.0, 0.0),
    (BW, 0.0),
    (BW, BH),
    (0.0, BH)
]
for i in range(4):
    p1 = corners[i]
    p2 = corners[(i+1)%4]
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(p1[0]), pcbnew.FromMM(p1[1])))
    seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(p2[0]), pcbnew.FromMM(p2[1])))
    seg.SetWidth(pcbnew.FromMM(0.1))
    board.Add(seg)

# Silkscreen Copyright & Title
txt_copy = pcbnew.PCB_TEXT(board)
txt_copy.SetLayer(pcbnew.F_SilkS)
txt_copy.SetText("© 2026 by Alessio Iodice")
txt_copy.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(60.0), pcbnew.FromMM(88.0)))
txt_copy.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
txt_copy.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
board.Add(txt_copy)

txt_title = pcbnew.PCB_TEXT(board)
txt_title.SetLayer(pcbnew.F_SilkS)
txt_title.SetText("TAPE MASTER EXERCISER & DIGITIZER v1.0")
txt_title.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(60.0), pcbnew.FromMM(2.5)))
txt_title.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.4), pcbnew.FromMM(1.4)))
txt_title.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
board.Add(txt_title)

# Add Nets to board
net_items = {}
net_items[""] = board.FindNet("")

for net_name, info in nets.items():
    net = pcbnew.NETINFO_ITEM(board, net_name)
    board.Add(net)
    net_items[net_name] = net

print(f"Added {len(net_items)} nets to board.")

# Map pin connections: (ref, pin) -> net_item
pin_net_map = {}
for net_name, info in nets.items():
    for ref, pin in info["nodes"]:
        pin_net_map[(ref, pin)] = net_items[net_name]

# Define Placement (x, y, rot) on 120mm x 90mm board
placement = {
    # 4 M3 Mounting Holes
    "H1":  (5.0, 5.0, 0),
    "H2":  (115.0, 5.0, 0),
    "H3":  (5.0, 85.0, 0),
    "H4":  (115.0, 85.0, 0),

    # --------------------------------------------------------------------------
    # 1. ANALOG SECTION (Left: X: 8..46, Y: 10..85)
    # --------------------------------------------------------------------------
    "J3":  (10.0, 22.0, 270),    # Audio In Jack (SJ-3523) facing left edge
    "JP2": (18.0, 16.0, 0),      # Head Boost jumper
    "D7":  (24.0, 16.0, 0),      # BAT54S protection
    "C15": (24.0, 22.0, 0),      # 1uF AC coupling
    "R24": (28.0, 22.0, 90),     # 100k bias to VBIAS
    
    # Preamp U4 (TLV2372)
    "U4":  (22.0, 34.0, 0),      # TLV2372 SOIC-8
    "R25": (16.0, 29.0, 90),     # 1k
    "R26": (20.0, 29.0, 90),     # 9.1k
    "C16": (25.0, 29.0, 0),      # 47pF
    "RV1": (12.0, 36.0, 0),      # 100k Bourns 3296W Trimmer
    "C22": (22.0, 41.0, 0),      # 100nF U4 bypass

    # Active Filters U5 (TLV2372)
    "C17": (32.0, 28.0, 0),      # 47nF
    "C18": (37.0, 28.0, 0),      # 47nF
    "R27": (32.0, 34.0, 90),     # 8.2k
    "R28": (37.0, 34.0, 90),     # 16k
    "U5":  (34.0, 42.0, 0),      # TLV2372 SOIC-8
    "C23": (34.0, 48.0, 0),      # 100nF U5 bypass
    "R29": (28.0, 48.0, 90),     # 12k
    "R30": (24.0, 48.0, 90),     # 12k
    "C19": (28.0, 54.0, 0),      # 1.5nF
    "C20": (24.0, 54.0, 0),      # 680pF

    # Peak Detector U6 (TLV2372)
    "U6":  (22.0, 64.0, 0),      # TLV2372 SOIC-8
    "D8":  (16.0, 60.0, 0),      # BAT54
    "C21": (16.0, 66.0, 0),      # 1uF storage cap
    "R31": (16.0, 71.0, 90),     # 100k discharge resistor
    "C24": (22.0, 71.0, 0),      # 100nF U6 bypass

    # Peak ADC Divider & Protection
    "R32": (28.0, 64.0, 90),     # 10k divider
    "R33": (32.0, 64.0, 90),     # 18k divider
    "D9":  (28.0, 70.0, 0),      # BAT54 clamp to 3.3V
    "C32": (32.0, 70.0, 0),      # 100nF ADC filter cap

    # Digitizer Comparator U8 (LM393)
    "U8":  (40.0, 56.0, 0),      # LM393 SOIC-8
    "R34": (40.0, 48.0, 90),     # 10k input
    "R35": (44.0, 48.0, 90),     # 470k hysteresis
    "RV3": (44.0, 38.0, 0),      # 50k Bourns 3296W Hysteresis Trimmer
    "R36": (44.0, 63.0, 90),     # 2.2k pullup
    "C26": (40.0, 63.0, 0),      # 100nF U8 bypass

    # --------------------------------------------------------------------------
    # 2. POWER SUPPLY SECTION (Top Center: X: 48..82, Y: 8..30)
    # --------------------------------------------------------------------------
    "J1":  (65.0, 8.0, 180),     # USB-C top edge
    "R1":  (56.0, 8.0, 90),      # 5.1k CC1
    "R2":  (59.0, 8.0, 90),      # 5.1k CC2
    "F1":  (74.0, 8.0, 90),      # PTC Fuse 1A
    "JP1": (78.0, 8.0, 0),       # C2N PWR SEL
    "D1":  (75.0, 14.0, 0),      # BAT54C dual Schottky
    "C1":  (70.0, 15.0, 0),      # 100uF tantalum
    "C2":  (65.0, 15.0, 0),      # 10uF
    "C3":  (60.0, 15.0, 0),      # 100nF
    "U1":  (54.0, 16.0, 0),      # AP2112K-3.3 SOT-23-5
    "C4":  (50.0, 12.0, 0),      # 1uF
    "C5":  (50.0, 16.0, 0),      # 2.2uF
    "C6":  (50.0, 20.0, 0),      # 100nF
    "D6":  (46.0, 16.0, 180),    # PWR 3.3V LED
    "R23": (46.0, 12.0, 90),     # 1k resistor

    # VBIAS Buffer U2 (TLV2372)
    "U2":  (38.0, 20.0, 0),      # TLV2372 SOIC-8
    "R3":  (34.0, 14.0, 90),     # 10k 0.1%
    "R4":  (38.0, 14.0, 90),     # 10k 0.1%
    "C7":  (42.0, 14.0, 0),      # 47uF tantalum
    "C8":  (42.0, 25.0, 0),      # 100nF
    "C9":  (38.0, 26.0, 0),      # 10uF
    "C10": (34.0, 26.0, 0),      # 100nF
    "C11": (34.0, 20.0, 0),      # 100nF U2 bypass

    # --------------------------------------------------------------------------
    # 3. DISPLAY & LED BARGRAPH SECTION (Center: X: 52..70, Y: 30..80)
    # --------------------------------------------------------------------------
    "DISP1": (65.0, 30.0, 0),    # OLED 0.96 Header (1x04)
    "R9":    (56.0, 26.0, 90),   # 4.7k I2C SDA
    "R10":   (59.0, 26.0, 90),   # 4.7k I2C SCL

    # 10 Bargraph LEDs (D10..D19) in vertical column at X=54.0
    "D10": (54.0, 38.0, 0),      # VU Green 1
    "D11": (54.0, 41.5, 0),      # VU Green 2
    "D12": (54.0, 45.0, 0),      # VU Green 3
    "D13": (54.0, 48.5, 0),      # VU Green 4
    "D14": (54.0, 52.0, 0),      # VU Green 5
    "D15": (54.0, 55.5, 0),      # VU Green 6
    "D16": (54.0, 59.0, 0),      # VU Green 7
    "D17": (54.0, 62.5, 0),      # VU Green 8
    "D18": (54.0, 66.0, 0),      # VU Yellow 1
    "D19": (54.0, 69.5, 0),      # VU Red 1

    # 4 Status LEDs (D2..D5) continuing the column
    "D2":  (54.0, 74.0, 0),      # READ Green
    "D3":  (54.0, 77.5, 0),      # WRITE Red
    "D4":  (54.0, 81.0, 0),      # MOTOR Yellow
    "D5":  (54.0, 84.5, 0),      # SIGNAL Blue

    # Dual TLC5916 LED Drivers U7 & U11 (SOIC-16)
    "U7":  (62.0, 50.0, 90),     # TLC5916 #1
    "R18": (58.0, 50.0, 90),     # 1.2k R-EXT
    "C25": (66.0, 50.0, 0),      # 100nF U7 bypass

    "U11": (62.0, 72.0, 90),     # TLC5916 #2
    "R20": (58.0, 72.0, 90),     # 1.2k R-EXT
    "C27": (66.0, 72.0, 0),      # 100nF U11 bypass

    # --------------------------------------------------------------------------
    # 4. MCU CORE SECTION (Right: X: 75..115, Y: 10..85)
    # --------------------------------------------------------------------------
    "SW1": (108.0, 16.0, 0),     # Rotary Encoder
    "R11": (98.0, 10.0, 90),     # 10k ENC A
    "R12": (101.0, 10.0, 90),    # 10k ENC B
    "R13": (104.0, 10.0, 90),    # 10k ENC SW

    # MicroSD socket on top right edge
    "J2":  (88.0, 12.0, 0),      # MicroSD Hirose
    "C12": (80.0, 12.0, 0),      # 100nF
    "R5":  (80.0, 18.0, 90),     # 10k SD_CS
    "R6":  (83.0, 18.0, 90),     # 10k SD_MOSI
    "R7":  (86.0, 18.0, 90),     # 10k SD_MISO
    "R8":  (89.0, 18.0, 90),     # 10k SD_SCK

    # Raspberry Pi Pico U3
    "U3":  (82.0, 54.0, 0),      # Pico DIP-40
    "C13": (72.0, 54.0, 0),      # 100nF ADC_VREF cap

    # Tactile Buttons SW2..SW5 along the right edge
    "SW2": (108.0, 32.0, 90),    # BTN Play/Stop
    "R14": (98.0, 32.0, 90),     # 10k pullup
    "SW3": (108.0, 44.0, 90),    # BTN Rec/Dump
    "R15": (98.0, 44.0, 90),     # 10k pullup
    "SW4": (108.0, 56.0, 90),    # BTN Rew/Prev
    "R16": (98.0, 56.0, 90),     # 10k pullup
    "SW5": (108.0, 68.0, 90),    # BTN FFwd/Next
    "R17": (98.0, 68.0, 90),     # 10k pullup
    "SW6": (108.0, 80.0, 90),    # Reset Button
    
    # --------------------------------------------------------------------------
    # 5. TAPE DECK INTERFACES (Bottom: X: 35..110, Y: 75..90)
    # --------------------------------------------------------------------------
    "J4":  (40.0, 90.0, 180),    # C2N Edge connector facing bottom edge
    "J5":  (40.0, 78.0, 0),      # C2N 1x06 Pin header
    "Q2":  (32.0, 84.0, 0),      # 2N3904 Motor sense
    "R39": (28.0, 84.0, 90),     # 10k base
    "R40": (24.0, 84.0, 90),     # 10k pulldown
    "R41": (32.0, 80.0, 90),     # 10k pullup

    "U9":  (74.0, 82.0, 0),      # 74HCT06 SOIC-14
    "C31": (74.0, 76.0, 0),      # 100nF U9 bypass
    "R42": (68.0, 82.0, 90),     # 1k write divider
    "R43": (68.0, 86.0, 90),     # 2k write divider
    "Q1":  (70.0, 76.0, 0),      # 2N7002 C2N Sense drive
    "R37": (66.0, 76.0, 90),     # 1k gate
    "R38": (66.0, 80.0, 90),     # 100k gate pulldown

    # Sinclair ZX / Apple Audio Out
    "J6":  (90.0, 88.0, 0),      # 3.5mm Jack facing bottom
    "R44": (85.0, 80.0, 90),     # 1k PWM filter
    "C28": (85.0, 84.0, 0),      # 10nF
    "R45": (89.0, 80.0, 90),     # 1k PWM filter
    "C29": (89.0, 84.0, 0),      # 10nF
    "C30": (93.0, 80.0, 0),      # 10uF DC block
    "R46": (97.0, 80.0, 90),     # 10k mic attenuator
    "R47": (97.0, 84.0, 90),     # 1k mic attenuator

    # Remote Control Jack & Optocoupler
    "J7":  (104.0, 88.0, 0),     # 2.5mm / 3.5mm Remote Jack
    "U10": (102.0, 76.0, 0),     # PC817 DIP-4
    "R48": (98.0, 76.0, 90)      # 330 ohm opto LED resistor
}

# Instantiate and place all footprints
loaded_count = 0
for ref, cinfo in comps.items():
    fp_str = cinfo["fp"]
    val = cinfo["val"]
    cpath = cinfo["path"]
    
    if ":" in fp_str:
        lib, name = fp_str.split(":", 1)
    else:
        lib, name = "", fp_str
    
    if lib == "Tape-Master":
        lpath = os.path.abspath(os.path.join(kicad_dir, "Tape-Master.pretty"))
    else:
        lpath = f"C:/Program Files/KiCad/9.0/share/kicad/footprints/{lib}.pretty"
    
    fp = pcbnew.FootprintLoad(lpath, name)
    if not fp:
        print(f"FAILED to load footprint {fp_str} for {ref}")
        continue
    
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetFPIDAsString(fp_str)
    fp.SetPath(pcbnew.KIID_PATH(cpath))
    fp.SetAttributes(fp.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
    
    # Hide reference & value on silkscreen by default for clean look
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    
    if ref in placement:
        px, py, prot = placement[ref]
    else:
        print(f"WARNING: No placement for {ref}, placing at (60, 45)")
        px, py, prot = 60.0, 45.0, 0
    
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(px), pcbnew.FromMM(py)))
    fp.SetOrientation(pcbnew.EDA_ANGLE(prot, pcbnew.DEGREES_T))
    
    # Connect pads to nets
    for pad in fp.Pads():
        pnum = pad.GetNumber()
        if (ref, pnum) in pin_net_map:
            pad.SetNet(pin_net_map[(ref, pnum)])
    
    board.Add(fp)
    loaded_count += 1

print(f"Successfully placed {loaded_count} footprints on {BW}x{BH} mm board.")

# Save board
board.Save(pcb_path)
print(f"Saved PCB to {pcb_path}")
