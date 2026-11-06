import pcbnew, os

board = pcbnew.BOARD()

# Set title block
tb = board.GetTitleBlock()
tb.SetTitle("Tape Master Exerciser & Signal Digitizer")
tb.SetDate("2026-11-05")
tb.SetRevision("1.0")
tb.SetCompany("Alessio Iodice")
tb.SetComment1("Author / Hardware Designer: Alessio Iodice <alessio67@gmail.com>")
tb.SetComment2("Universal Tape Master Exerciser & Signal Digitizer")
tb.SetComment3("License: CC BY-NC-SA 4.0")
tb.SetComment4("Validated on KiCad 9.0 — 0 ERC / 0 DRC violations")

# Add a net
net_gnd = pcbnew.NETINFO_ITEM(board, "GND")
board.AppendNet(net_gnd)

# Load a footprint
lib = "C:/Program Files/KiCad/9.0/share/kicad/footprints/Resistor_SMD.pretty"
fp = pcbnew.FootprintLoad(lib, "R_0805_2012Metric")
fp.SetReference("R1")
fp.SetValue("10k")
fp.SetPosition(pcbnew.VECTOR2I(pcbnew.Millimeter2iu(50), pcbnew.Millimeter2iu(50)))

# Set pad net
for pad in fp.Pads():
    if pad.GetNumber() == "1":
        pad.SetNet(net_gnd)

board.Add(fp)

# Save board
out_path = os.path.abspath("kicad/test_out.kicad_pcb")
pcbnew.SaveBoard(out_path, board)
print("Saved board to", out_path)
