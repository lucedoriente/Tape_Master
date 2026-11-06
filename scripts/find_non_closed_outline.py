import pcbnew, os

board = pcbnew.LoadBoard("kicad/Tape-Master.kicad_pcb")

print("Checking board Edge.Cuts...")
for dwg in board.GetDrawings():
    if dwg.GetLayerName() == "Edge.Cuts":
        print(f"Edge drawing: shape={dwg.GetShapeStr()}, start=({dwg.GetStartX()/1e6}, {dwg.GetStartY()/1e6}), end=({dwg.GetEndX()/1e6}, {dwg.GetEndY()/1e6})")

print("Checking footprint graphical items and courtyards...")
for fp in board.Footprints():
    ref = fp.GetReference()
    for g in fp.GraphicalItems():
        if isinstance(g, pcbnew.PCB_SHAPE) and g.GetShape() == pcbnew.SHAPE_T_POLY:
            poly = g.GetPolyShape()
            if poly and not poly.IsEmpty():
                for o_idx in range(poly.OutlineCount()):
                    line_chain = poly.Outline(o_idx)
                    if not line_chain.IsClosed():
                        print(f"NON-CLOSED outline in {ref} layer {g.GetLayerName()}")
