import pcbnew

pcb_file = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
board = pcbnew.LoadBoard(pcb_file)

def set_models(fp, model_specs):
    # Clear existing models
    fp.Models().clear()
    for fname, offset, scale, rot in model_specs:
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = fname
        m.m_Offset = pcbnew.VECTOR3D(offset[0], offset[1], offset[2])
        m.m_Scale = pcbnew.VECTOR3D(scale[0], scale[1], scale[2])
        m.m_Rotation = pcbnew.VECTOR3D(rot[0], rot[1], rot[2])
        m.m_Show = True
        fp.Add3DModel(m)

# 1. J4: C2N Edge Connector
j4 = board.FindFootprintByReference("J4")
if j4:
    set_models(j4, [
        ("${KIPRJMOD}/3dmodels/C2N_Edge_Connector.wrl", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        ("${KIPRJMOD}/3dmodels/C2N_Edge_Connector.step", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    ])
    print("Updated J4 3D models")

# 2. SW1: Rotary Encoder
sw1 = board.FindFootprintByReference("SW1")
if sw1:
    set_models(sw1, [
        ("${KIPRJMOD}/3dmodels/EC11_Encoder.wrl", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        ("${KIPRJMOD}/3dmodels/EC11_Encoder.step", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    ])
    print("Updated SW1 3D models")

# 3. J3, J6, J7: Audio Jacks
for ref in ["J3", "J6", "J7"]:
    fp = board.FindFootprintByReference(ref)
    if fp:
        set_models(fp, [
            ("${KICAD9_3DMODEL_DIR}/Connector_Audio.3dshapes/Jack_3.5mm_CUI_SJ1-3523N_Horizontal.wrl", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
            ("${KICAD9_3DMODEL_DIR}/Connector_Audio.3dshapes/Jack_3.5mm_CUI_SJ1-3523N_Horizontal.step", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        ])
        print(f"Updated {ref} 3D models")

# 4. J5: Header 1x06
j5 = board.FindFootprintByReference("J5")
if j5:
    set_models(j5, [
        ("${KICAD9_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x06_P2.54mm_Vertical.wrl", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        ("${KICAD9_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x06_P2.54mm_Vertical.step", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    ])
    print("Updated J5 3D models")

board.Save(pcb_file)
print("Successfully saved board:", pcb_file)
