import pcbnew

b = pcbnew.LoadBoard('kicad/Tape-Master.kicad_pcb')
u7 = b.FindFootprintByReference('U7')

for p in u7.Pads():
    if p.GetNumber() in ['9', '10']:
        print(f"Pad {p.GetNumber()}:")
        print(f"  Pos: ({pcbnew.ToMM(p.GetPosition().x):.4f}, {pcbnew.ToMM(p.GetPosition().y):.4f})")
        print(f"  Shape: {p.GetShape()}")
        print(f"  Size: ({pcbnew.ToMM(p.GetSize().x):.4f}, {pcbnew.ToMM(p.GetSize().y):.4f})")
        print(f"  Drill: {pcbnew.ToMM(p.GetDrillSize().x):.4f}")
        print(f"  Layers: {[b.GetLayerName(l) for l in p.GetLayerSet().Seq()]}")
        print(f"  Net: {p.GetNetname()}")
