import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)
for fp in board.Footprints():
    fp.BuildCourtyardCaches()

def get_c_bbox(fp):
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    if not c or c.IsEmpty(): c = fp.GetCourtyard(pcbnew.B_CrtYd)
    if not c or c.IsEmpty(): bb = fp.GetBoundingBox(True, False)
    else: bb = c.BBox()
    return (pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), 
            pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))

for ref in ["J4", "H3", "J5", "U3", "U7", "U11", "U9", "U10", "J6", "J7", "SW1", "SW2", "H4", "SW6"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        bx1, by1, bx2, by2 = get_c_bbox(fp)
        print(f"{ref:6s}: X=[{bx1:6.2f} .. {bx2:6.2f}], Y=[{by1:6.2f} .. {by2:6.2f}]")
