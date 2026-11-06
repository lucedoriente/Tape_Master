import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

# Find net /03_Analog_Ingest/TAPE_FILTERED
old_net = board.FindNet("/03_Analog_Ingest/TAPE_FILTERED")
target_net = board.FindNet("TAPE_FILTERED")

if not target_net:
    target_net = pcbnew.NETINFO_ITEM(board, "TAPE_FILTERED")
    board.Add(target_net)

# Reassign all pads and tracks on old_net to target_net
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname() == "/03_Analog_Ingest/TAPE_FILTERED":
            p.SetNet(target_net)

for tr in board.GetTracks():
    if tr.GetNetname() == "/03_Analog_Ingest/TAPE_FILTERED":
        tr.SetNet(target_net)

# Assign U3 Pin 34 to target_net
u3 = board.FindFootprintByReference("U3")
p34 = [p for p in u3.Pads() if p.GetPadName() == "34"][0]
p34.SetNet(target_net)

# Update values for D1 and C1
d1 = board.FindFootprintByReference("D1")
if d1:
    d1.SetValue("PMEG3010AET")

c1 = board.FindFootprintByReference("C1")
if c1:
    c1.SetValue("100uF_Polymer")

board.Save(pcb_file)
print("Updated net and component values on PCB.")
