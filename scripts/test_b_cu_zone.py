import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

z = board.Zones()[0]
poly = z.Outline()
for i in range(poly.PointCount(0)):
    pt = poly.CPoint(0, i)
    print(f"Point {i}: ({pt.x/1e6:.2f}, {pt.y/1e6:.2f})")

z1 = board.Zones()[1]
poly1 = z1.Outline()
print("Zone 1:")
for i in range(poly1.PointCount(0)):
    pt = poly1.CPoint(0, i)
    print(f"Point {i}: ({pt.x/1e6:.2f}, {pt.y/1e6:.2f})")
