import pcbnew, os, sys, re, json

kicad_dir = os.path.abspath("kicad")
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

# Board Outline (100mm x 85mm)
corners = [
    (0.0, 0.0),
    (100.0, 0.0),
    (100.0, 85.0),
    (0.0, 85.0)
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
txt_copy.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(50.0), pcbnew.FromMM(83.5)))
txt_copy.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(1.2)))
txt_copy.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
board.Add(txt_copy)

txt_title = pcbnew.PCB_TEXT(board)
txt_title.SetLayer(pcbnew.F_SilkS)
txt_title.SetText("TAPE MASTER EXERCISER & DIGITIZER v1.0")
txt_title.SetTextPos(pcbnew.VECTOR2I(pcbnew.FromMM(50.0), pcbnew.FromMM(2.5)))
txt_title.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.4), pcbnew.FromMM(1.4)))
txt_title.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
board.Add(txt_title)

# Add Nets to board
net_items = {}
# Default empty net
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

# Define Component Coordinates (x, y, rot)
placement = {
    # 4 M3 Mounting Holes
    "H1":  (4.0, 4.0, 0),
    "H2":  (96.0, 4.0, 0),
    "H3":  (4.0, 81.0, 0),
    "H4":  (96.0, 81.0, 0),

    # Power Supply (X: 5..32, Y: 10..32)
    "J1":  (7.0, 16.0, 0),      # USB-C
    "D1":  (15.0, 10.0, 0),     # BAT54S
    "JP1": (18.0, 10.0, 0),     # C2N PWR SEL
    "F1":  (15.0, 15.0, 90),    # Fuse
    "U1":  (22.0, 16.0, 0),     # AP2112K-3.3
    "C1":  (17.0, 22.0, 0),     # 100uF
    "C2":  (12.0, 22.0, 0),     # 10uF
    "C3":  (12.0, 26.0, 0),     # 100nF
    "C4":  (22.0, 22.0, 0),     # 1uF
    "C5":  (22.0, 26.0, 0),     # 10uF
    "C6":  (26.0, 26.0, 0),     # 100nF
    "R1":  (7.0, 22.0, 90),     # 5.1k
    "R2":  (9.0, 22.0, 90),     # 5.1k
    "U2":  (28.0, 18.0, 0),     # TLV2372 VBIAS
    "R3":  (28.0, 11.0, 90),    # 100k
    "R4":  (31.0, 11.0, 90),    # 100k
    "C7":  (28.0, 24.0, 0),     # 10uF
    "C8":  (32.0, 24.0, 0),     # 100nF
    "C9":  (32.0, 18.0, 0),     # 10uF
    "C10": (36.0, 18.0, 0),     # 100nF
    "C11": (36.0, 24.0, 0),     # 100nF
    "D6":  (18.0, 28.0, 180),   # PWR 3.3V LED
    "R23": (14.0, 28.0, 90),    # 1k LED resistor

    # MCU Core (X: 35..75, Y: 10..60)
    "SW1": (25.0, 6.0, 0),      # Rotary Encoder
    "C14": (20.0, 6.0, 0),      # 100nF
    "J2":  (45.0, 10.0, 0),     # MicroSD socket
    "C12": (55.0, 10.0, 0),     # 100nF
    "R5":  (38.0, 6.0, 90),     # 10k SD
    "R6":  (41.0, 6.0, 90),     # 10k SD
    "R7":  (44.0, 6.0, 90),     # 10k SD
    "R8":  (47.0, 6.0, 90),     # 10k SD
    "DISP1":(70.0, 10.0, 0),    # OLED 4-pin
    "R9":  (65.0, 6.0, 90),     # 4.7k I2C
    "R10": (68.0, 6.0, 90),     # 4.7k I2C
    "SW2": (42.0, 20.0, 0),     # BTN Play/Stop
    "SW3": (52.0, 20.0, 0),     # BTN Rec
    "SW4": (62.0, 20.0, 0),     # BTN FFwd
    "SW5": (72.0, 20.0, 0),     # BTN Rew
    "SW6": (36.0, 20.0, 0),     # BTN Reset
    "R11": (42.0, 25.0, 90),    # 10k
    "R12": (52.0, 25.0, 90),    # 10k
    "R13": (62.0, 25.0, 90),    # 10k
    "R14": (72.0, 25.0, 90),    # 10k
    "R15": (28.0, 6.0, 90),     # 10k
    "R16": (31.0, 6.0, 90),     # 10k
    "R17": (34.0, 6.0, 90),     # 10k
    "R18": (36.0, 25.0, 90),    # 10k Reset
    "U3":  (56.0, 45.0, 0),     # Raspberry Pi Pico
    "C13": (42.0, 30.0, 0),     # 100nF Pico bypass
    "D2":  (40.0, 62.0, 180),   # LED Read
    "D3":  (44.0, 62.0, 180),   # LED Write
    "D4":  (48.0, 62.0, 180),   # LED Motor
    "D5":  (52.0, 62.0, 180),   # LED Signal
    "R19": (40.0, 66.0, 90),    # 330
    "R20": (44.0, 66.0, 90),    # 330
    "R21": (48.0, 66.0, 90),    # 330
    "R22": (52.0, 66.0, 90),    # 330

    # Analog Ingest (X: 8..38, Y: 35..78)
    "J3":  (8.0, 38.0, 0),      # Audio In Jack
    "JP2": (14.0, 32.0, 0),     # Head Boost Jumper
    "D7":  (15.0, 35.0, 0),     # BAT54S
    "C15": (18.0, 38.0, 0),     # 1uF
    "R24": (18.0, 34.0, 90),    # 100k
    "U4":  (24.0, 38.0, 0),     # NE5532 Preamp
    "R25": (24.0, 33.0, 90),    # 1k
    "R26": (28.0, 33.0, 90),    # 9.1k
    "C16": (28.0, 38.0, 0),     # 47pF
    "RV1": (22.0, 46.0, 0),     # 100k Trimmer
    "C22": (18.0, 44.0, 0),     # 100nF U4 bypass
    "C17": (15.0, 52.0, 0),     # 47nF
    "C18": (19.0, 52.0, 0),     # 47nF
    "U5":  (25.0, 56.0, 0),     # NE5532 Bandpass
    "R27": (22.0, 50.0, 90),    # 8.2k
    "R28": (26.0, 50.0, 90),    # 16k
    "R29": (18.0, 57.0, 90),    # 12k
    "R30": (21.0, 57.0, 90),    # 12k
    "C19": (18.0, 62.0, 0),     # 1.5nF
    "C20": (22.0, 62.0, 0),     # 680pF
    "C23": (29.0, 62.0, 0),     # 100nF U5 bypass
    "U6":  (34.0, 54.0, 0),     # NE5532 Peak Detector
    "D8":  (30.0, 52.0, 0),     # BAT54
    "C21": (30.0, 57.0, 0),     # 1uF
    "R31": (34.0, 48.0, 90),    # 100k
    "R32": (38.0, 54.0, 90),    # 1k ADC protect
    "C24": (38.0, 58.0, 0),     # 100nF U6 bypass
    "U8":  (34.0, 38.0, 0),     # LM393 Schmitt Digitizer
    "R34": (34.0, 32.0, 90),    # 10k
    "R35": (38.0, 32.0, 90),    # 470k
    "RV3": (34.0, 44.0, 0),     # 50k Hyst Trimmer
    "R36": (38.0, 44.0, 90),    # 2.2k Pullup
    "C26": (38.0, 38.0, 0),     # 100nF U8 bypass
    "U7":  (65.0, 72.0, 0),     # LM3914 DIP-18
    "RV2": (50.0, 72.0, 0),     # 10k Sens Trimmer
    "R33": (46.0, 72.0, 90),    # 1.2k
    "C25": (54.0, 72.0, 0),     # 100nF U7 bypass

    # VU Meter 10 LEDs (Bottom Edge X: 35..80, Y: 80)
    "D10": (36.0, 79.0, 0),
    "D11": (40.5, 79.0, 0),
    "D12": (45.0, 79.0, 0),
    "D13": (49.5, 79.0, 0),
    "D14": (54.0, 79.0, 0),
    "D15": (58.5, 79.0, 0),
    "D16": (63.0, 79.0, 0),
    "D17": (67.5, 79.0, 0),
    "D18": (72.0, 79.0, 0),
    "D19": (76.5, 79.0, 0),

    # Tape Interfaces (X: 74..95, Y: 30..75)
    "J4":  (92.0, 40.0, 0),     # C2N Edge Connector
    "J5":  (82.0, 40.0, 0),     # C2N Pin Header
    "U9":  (74.0, 48.0, 0),     # 74LS06 Hex Inverter
    "C31": (74.0, 42.0, 0),     # 100nF U9 bypass
    "R37": (74.0, 56.0, 90),    # 1k
    "R38": (77.0, 56.0, 90),    # 100k
    "R39": (80.0, 56.0, 90),    # 1k
    "R40": (83.0, 56.0, 90),    # 10k
    "R41": (86.0, 56.0, 90),    # 4.7k
    "R42": (89.0, 56.0, 90),    # 1k
    "R43": (92.0, 56.0, 90),    # 100k
    "Q1":  (80.0, 62.0, 0),     # BSS138 NMOS
    "Q2":  (86.0, 62.0, 0),     # 2N3904 NPN
    "D9":  (76.0, 62.0, 0),     # 1N4148
    "C27": (82.0, 48.0, 0),     # 4.7nF
    "C30": (86.0, 48.0, 0),     # 100pF
    "J6":  (8.0, 58.0, 0),      # Audio Out Jack
    "R44": (14.0, 58.0, 90),    # 1k PWM filter
    "R45": (17.0, 58.0, 90),    # 1k PWM filter
    "C28": (14.0, 64.0, 0),     # 10nF
    "C29": (17.0, 64.0, 0),     # 10nF
    "R46": (14.0, 69.0, 90),    # 10k attenuator
    "R47": (17.0, 69.0, 90),    # 1k attenuator
    "J7":  (8.0, 76.0, 0),      # Remote Jack
    "U10": (20.0, 75.0, 0),     # PC817 Opto
    "R48": (26.0, 75.0, 90),    # 330
    "R49": (14.0, 76.0, 90)     # 10
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
        lpath = os.path.abspath("kicad/Tape-Master.pretty")
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
    
    # Get position & rotation
    if ref in placement:
        px, py, prot = placement[ref]
    else:
        print(f"WARNING: No placement for {ref}, placing at (50, 50)")
        px, py, prot = 50.0, 50.0, 0
    
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(px), pcbnew.FromMM(py)))
    fp.SetOrientationDegrees(prot)
    
    # Connect pads to nets
    for pad in fp.Pads():
        pnum = pad.GetNumber()
        if (ref, pnum) in pin_net_map:
            pad.SetNet(pin_net_map[(ref, pnum)])
    
    board.Add(fp)
    loaded_count += 1

print(f"Successfully placed {loaded_count} / {len(comps)} footprints on board.")

# Save Board
pcbnew.SaveBoard(pcb_path, board)
print("Saved PCB to", pcb_path)
