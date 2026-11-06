import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

# Update values
d1 = board.FindFootprintByReference("D1")
if d1:
    d1.SetValue("PMEG3010AET")

c1 = board.FindFootprintByReference("C1")
if c1:
    c1.SetValue("100uF_Polymer")

# Find net TAPE_FILTERED
u5 = board.FindFootprintByReference("U5")
p7 = [p for p in u5.Pads() if p.GetPadName() == "7"][0]
tape_filt_net = p7.GetNet()
print("TAPE_FILTERED Net:", tape_filt_net.GetNetname())

# Connect U3 Pin 34 to TAPE_FILTERED
u3 = board.FindFootprintByReference("U3")
p34 = [p for p in u3.Pads() if p.GetPadName() == "34"][0]
print("Old net of U3 pin 34:", p34.GetNetname())
p34.SetNet(tape_filt_net)
print("New net of U3 pin 34:", p34.GetNetname())

board.Save(pcb_file)
print("Saved board")
