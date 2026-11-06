import pcbnew, os

src_board = pcbnew.LoadBoard("kicad/Tape-Master.kicad_pcb")
dsn_test = os.path.abspath("kicad/test_culprit.dsn")

# Let's test with just the outline first
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

# Copy nets
for net_name in src_board.GetNetsByName():
    if net_name:
        net = pcbnew.NETINFO_ITEM(b, net_name)
        b.Add(net)

print("Testing adding footprints one by one...")
fps = list(src_board.Footprints())

for idx, fp in enumerate(fps):
    ref = fp.GetReference()
    # clone fp
    lib_id = fp.GetFPIDAsString()
    # Add footprint to b
    fp_new = pcbnew.FOOTPRINT(b)
    # or just add from library
    # Let's try adding the footprint directly
    b.Add(fp)
    # Test DSN export
    # Note: we test without blocking
    print(f"[{idx+1}/{len(fps)}] Added {ref} ({lib_id})")
    try:
        res = pcbnew.ExportSpecctraDSN(b, dsn_test)
        if not res:
            print(f"FAILED on {ref}")
            break
    except Exception as e:
        print(f"EXCEPTION on {ref}: {e}")
        break

print("All footprints tested!")
