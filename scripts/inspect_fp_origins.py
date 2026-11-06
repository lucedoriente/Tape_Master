import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)
for fp in board.Footprints():
    fp.BuildCourtyardCaches()

def get_rel_bbox(fp):
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    if not c or c.IsEmpty(): c = fp.GetCourtyard(pcbnew.B_CrtYd)
    if not c or c.IsEmpty(): bb = fp.GetBoundingBox(True, False)
    else: bb = c.BBox()
    pos = fp.GetPosition()
    rx1 = pcbnew.ToMM(bb.GetX() - pos.x)
    ry1 = pcbnew.ToMM(bb.GetY() - pos.y)
    rx2 = pcbnew.ToMM(bb.GetRight() - pos.x)
    ry2 = pcbnew.ToMM(bb.GetBottom() - pos.y)
    return (rx1, ry1, rx2, ry2)

targets = ["U3", "J1", "J2", "J3", "J4", "J5", "J6", "J7", "SW1", "SW2", "DISP1", "U7", "U9", "RV1"]
for ref in targets:
    fp = board.FindFootprintByReference(ref)
    if fp:
        rx1, ry1, rx2, ry2 = get_rel_bbox(fp)
        print(f"{ref:6s} (rot={fp.GetOrientationDegrees():3.0f}): rel X=[{rx1:6.2f} .. {rx2:6.2f}], rel Y=[{ry1:6.2f} .. {ry2:6.2f}]")
