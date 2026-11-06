import pcbnew, os

board = pcbnew.BOARD()

# Add 4 lines on Edge.Cuts
corners = [
    (0, 0),
    (100, 0),
    (100, 85),
    (0, 85)
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

dsn_path = os.path.abspath("kicad/test_outline.dsn")
res = pcbnew.ExportSpecctraDSN(board, dsn_path)
print("DSN export result:", res)
with open(dsn_path, "r", encoding="utf-8") as f:
    text = f.read()

# Check boundary section
if "(boundary" in text:
    b_idx = text.find("(boundary")
    print(text[b_idx:b_idx+300])
else:
    print("WARNING: (boundary section not found in DSN!")
