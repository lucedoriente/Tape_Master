import pcbnew, os

pcb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kicad", "Tape-Master.kicad_pcb"))
board = pcbnew.LoadBoard(pcb_path)

print("Footprint Courtyard Sizes (width x height in mm):")
sizes = {}
for fp in board.Footprints():
    fp.BuildCourtyardCaches()
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    if not c or c.IsEmpty():
        c = fp.GetCourtyard(pcbnew.B_CrtYd)
    ref = fp.GetReference()
    if c and not c.IsEmpty():
        bb = c.BBox()
        w = pcbnew.ToMM(bb.GetWidth())
        h = pcbnew.ToMM(bb.GetHeight())
        sizes[ref] = (w, h)
    else:
        # Pad bounding box fallback
        bb = fp.GetBoundingBox(True, False)
        w = pcbnew.ToMM(bb.GetWidth())
        h = pcbnew.ToMM(bb.GetHeight())
        sizes[ref] = (w, h)

for ref in sorted(sizes.keys()):
    print(f"  {ref:6s}: {sizes[ref][0]:6.2f} x {sizes[ref][1]:6.2f} mm")
