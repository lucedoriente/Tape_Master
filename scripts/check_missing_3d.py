import pcbnew
import os

board_path = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\Tape-Master.kicad_pcb"
kicad_3d = r"C:\Program Files\KiCad\9.0\share\kicad\3dmodels"
prj_3d = r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad\3dmodels"

board = pcbnew.LoadBoard(board_path)
missing = []

for fp in board.GetFootprints():
    ref = fp.GetReference()
    models = fp.Models()
    if not models:
        missing.append((ref, "NO MODEL", fp.GetFPID().GetUniStringLibId()))
        continue
    for m in models:
        raw = m.m_Filename
        path = raw
        if "${KICAD9_3DMODEL_DIR}" in path:
            path = path.replace("${KICAD9_3DMODEL_DIR}", kicad_3d)
        if "${KIPRJMOD}/3dmodels" in path:
            path = path.replace("${KIPRJMOD}/3dmodels", prj_3d)
        if "${KIPRJMOD}" in path:
            path = path.replace("${KIPRJMOD}", r"C:\Users\aless\OneDrive\temp\Manutenzione\Kicad_Project\Tape_Master\kicad")
        
        path = os.path.normpath(path)
        base, _ = os.path.splitext(path)
        step_f = base + ".step"
        wrl_f = base + ".wrl"
        stp_f = base + ".stp"
        
        exists = os.path.exists(path) or os.path.exists(step_f) or os.path.exists(wrl_f) or os.path.exists(stp_f)
        if not exists:
            missing.append((ref, raw, fp.GetFPID().GetUniStringLibId()))

print("Actually missing 3D models:")
for item in sorted(set(missing)):
    print(item)
