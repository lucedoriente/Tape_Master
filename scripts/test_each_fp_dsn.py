import pcbnew, os

unique_fps = set()
src_board = pcbnew.LoadBoard("kicad/Tape-Master.kicad_pcb")
for fp in src_board.Footprints():
    unique_fps.add(fp.GetFPIDAsString())

print(f"Total unique footprint types: {len(unique_fps)}")

b = pcbnew.BOARD()
corners = [(0, 0), (100, 0), (100, 85), (0, 85)]
for i in range(4):
    p1 = corners[i]
    p2 = corners[(i+1)%4]
    seg = pcbnew.PCB_SHAPE(b)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(p1[0]), pcbnew.FromMM(p1[1])))
    seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(p2[0]), pcbnew.FromMM(p2[1])))
    seg.SetWidth(pcbnew.FromMM(0.1))
    b.Add(seg)

for fp_str in sorted(unique_fps):
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
        print("Missing fp:", fp_str)
        continue
    
    # Try exporting DSN with just this footprint
    test_b = pcbnew.BOARD()
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i+1)%4]
        seg = pcbnew.PCB_SHAPE(test_b)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(p1[0]), pcbnew.FromMM(p1[1])))
        seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(p2[0]), pcbnew.FromMM(p2[1])))
        seg.SetWidth(pcbnew.FromMM(0.1))
        test_b.Add(seg)
        
    test_b.Add(fp)
    dsn_out = os.path.abspath(f"kicad/temp_test.dsn")
    try:
        res = pcbnew.ExportSpecctraDSN(test_b, dsn_out)
        print(f"OK: {fp_str}")
    except Exception as e:
        print(f"CRASH: {fp_str}: {e}")
